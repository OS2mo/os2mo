# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
import asyncio
import datetime
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta
from functools import partial
from functools import wraps
from typing import Any
from typing import Callable
from typing import Literal
from typing import Tuple
from typing import Union
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Query
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastramqpi.context import Context
from fastramqpi.main import FastRAMQPI
from gql.transport.exceptions import TransportQueryError
from ldap3 import Connection
from pydantic import ValidationError
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramodels.mo._shared import validate_cpr
from ramqp import AMQPSystem
from ramqp.mo import MORouter
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import PayloadType
from ramqp.mo.models import RequestType
from ramqp.mo.models import ServiceType
from ramqp.utils import RejectMessage
from tqdm import tqdm

from . import usernames
from .config import Settings
from .converters import LdapConverter
from .converters import read_mapping_json
from .customer_specific_checks import ExportChecks
from .dataloaders import DataLoader
from .dependencies import valid_cpr
from .exceptions import CPRFieldNotFound
from .exceptions import IgnoreChanges
from .exceptions import IncorrectMapping
from .exceptions import NoObjectsReturnedException
from .exceptions import NotSupportedException
from .import_export import SyncTool
from .ldap import check_ou_in_list_of_ous
from .ldap import configure_ldap_connection
from .ldap import get_attribute_types
from .ldap import ldap_healthcheck
from .ldap import poller_healthcheck
from .ldap import setup_listener
from .ldap_classes import LdapObject
from .logging import logger
from .os2mo_init import InitEngine
from .utils import countdown
from .utils import listener
from .utils import mo_datestring_to_utc


fastapi_router = APIRouter()
amqp_router = MORouter()
internal_amqp_router = MORouter()
delay_on_error = 10

"""
Employee.schema()
help(MORouter)
help(ServiceType)
help(ObjectType)
help(RequestType)
"""


def reject_on_failure(func):
    """
    Decorator to turn message into dead letter in case of exceptions.
    """

    @wraps(func)
    async def modified_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except (
            NotSupportedException,  # For features that are not supported: Abort
            IncorrectMapping,  # If the json dict is incorrectly configured: Abort
            TransportQueryError,  # In case an ldap entry cannot be uploaded: Abort
            NoObjectsReturnedException,  # In case an object is deleted halfway: Abort
            IgnoreChanges,  # In case changes should be ignored: Abort
            RejectMessage,  # In case we explicitly reject the message: Abort
        ) as e:
            logger.info(e)
            raise RejectMessage()
        except Exception:  # pylint: disable=broad-except
            await asyncio.sleep(delay_on_error)
            raise

    modified_func.__wrapped__ = func  # type: ignore
    return modified_func


async def get_delete_flag(
    routing_key: MORoutingKey, payload: PayloadType, context: Context
):
    """
    Determines if an object should be deleted based on the routing key and validity
    to-date
    """
    dataloader = context["user_context"]["dataloader"]

    if routing_key.request_type == RequestType.TERMINATE:

        mo_object = await dataloader.load_mo_object(
            payload.object_uuid, routing_key.object_type, add_validity=True
        )

        if not mo_object:
            # The object is not a current object AND request_type==TERMINATE.
            # Meaning it was deleted and the date was set to a day before today
            # In any case the object is not in MO and can therefore be deleted from LDAP
            logger.info(
                (
                    "[get_delete_flag] Returning delete=True because "
                    f"there is no current object with uuid={payload.object_uuid}"
                )
            )
            return True

        now = datetime.datetime.utcnow()
        validity_to = mo_datestring_to_utc(mo_object["validity"]["to"])
        if validity_to and validity_to <= now:
            logger.info(
                (
                    "[get_delete_flag] Returning delete=True because "
                    f"to-date ({validity_to}) <= current date ({now})"
                )
            )
            return True
        else:
            logger.info(
                "[get_delete_flag] RequestType = TERMINATE but to_date is not <= today"
            )
            # Abort so we do not risk deleting an object.
            # This is more safe, than returning 'False' and giving the caller the
            # responsibility to abort.
            raise RejectMessage()
    else:
        return False


@internal_amqp_router.register("*.*.*")
@amqp_router.register("*.*.*")
@reject_on_failure
async def listen_to_changes(
    context: Context, payload: PayloadType, mo_routing_key: MORoutingKey
) -> None:

    # If we are not supposed to listen: reject and turn the message into a dead letter.
    if not Settings().listen_to_changes_in_mo:
        logger.info("listen_to_changes_in_mo = False. Aborting.")
        raise RejectMessage()

    logger.info(f"[MO] Routing key: {mo_routing_key}")
    logger.info(f"[MO] Payload: {payload}")
    sync_tool = context["user_context"]["sync_tool"]

    delete = await get_delete_flag(mo_routing_key, payload, context)
    current_objects_only = False if delete else True

    args = dict(
        payload=payload,
        routing_key=mo_routing_key,
        delete=delete,
        current_objects_only=current_objects_only,
    )

    if mo_routing_key.service_type == ServiceType.EMPLOYEE:
        await sync_tool.listen_to_changes_in_employees(**args)
    elif mo_routing_key.service_type == ServiceType.ORG_UNIT:
        await sync_tool.listen_to_changes_in_org_units(**args)


@asynccontextmanager
async def open_ldap_connection(ldap_connection: Connection) -> AsyncIterator[None]:
    """Open the LDAP connection during FastRAMQPI lifespan.

    Yields:
        None
    """
    with ldap_connection:
        yield


def construct_gql_client(settings: Settings, sync=False):
    return PersistentGraphQLClient(
        url=settings.mo_url + "/graphql/v3",
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
        auth_server=settings.auth_server,
        auth_realm=settings.auth_realm,
        execute_timeout=settings.graphql_timeout,
        httpx_client_kwargs={"timeout": settings.graphql_timeout},
        sync=sync,
    )


def construct_model_client(settings: Settings):
    return ModelClient(
        base_url=settings.mo_url,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
        auth_server=settings.auth_server,
        auth_realm=settings.auth_realm,
    )


def construct_clients(
    settings: Settings,
) -> Tuple[PersistentGraphQLClient, PersistentGraphQLClient, ModelClient]:
    """Construct clients froms settings.

    Args:
        settings: Integration settings module.

    Returns:
        Tuple with PersistentGraphQLClient and ModelClient.
    """
    gql_client = construct_gql_client(settings)
    gql_client_sync = construct_gql_client(settings, sync=True)
    model_client = construct_model_client(settings)
    return gql_client, gql_client_sync, model_client


def create_fastramqpi(**kwargs: Any) -> FastRAMQPI:
    """FastRAMQPI factory.

    Returns:
        FastRAMQPI system.
    """
    logger.info("Retrieving settings")
    settings = Settings(**kwargs)

    # ldap_ou_for_new_users needs to be in the search base. Otherwise we cannot
    # find newly created users...
    check_ou_in_list_of_ous(
        settings.ldap_ou_for_new_users,
        settings.ldap_ous_to_search_in,
    )

    # We also need to check for permission to write to this OU
    check_ou_in_list_of_ous(
        settings.ldap_ou_for_new_users,
        settings.ldap_ous_to_write_to,
    )

    logger.info("Setting up FastRAMQPI")
    fastramqpi = FastRAMQPI(application_name="ad2mosync", settings=settings.fastramqpi)
    fastramqpi.add_context(settings=settings)

    logger.info("AMQP router setup")
    amqpsystem = fastramqpi.get_amqpsystem()
    amqpsystem.router.registry.update(amqp_router.registry)

    logger.info("Setting up clients")
    gql_client, gql_client_sync, model_client = construct_clients(settings)
    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)
    fastramqpi._context["graphql_client"] = gql_client
    fastramqpi.add_context(gql_client_sync=gql_client_sync)

    logger.info("Configuring LDAP connection")
    ldap_connection = configure_ldap_connection(settings)
    fastramqpi.add_context(ldap_connection=ldap_connection)
    fastramqpi.add_healthcheck(name="LDAPConnection", healthcheck=ldap_healthcheck)
    fastramqpi.add_lifespan_manager(open_ldap_connection(ldap_connection), 1500)

    logger.info("Loading mapping file")
    mappings_file = os.environ.get("CONVERSION_MAP")
    if not mappings_file:
        mappings_file = "magenta_demo.json"
        logger.warning(f"CONVERSION_MAP is not set, falling back to {mappings_file}")
    mappings_file = os.path.normpath(
        mappings_file
        if mappings_file.startswith("/")
        else os.path.join(os.path.dirname(__file__), "mappings", mappings_file)
    )
    if not os.path.isfile(mappings_file):
        raise FileNotFoundError(
            f"Configured mapping file {mappings_file} does not exist "
            f"(this is set by the CONVERSION_MAP environment variable)"
        )
    mapping = read_mapping_json(mappings_file)
    fastramqpi.add_context(mapping=mapping)
    logger.info(f"Loaded mapping file {mappings_file}")

    logger.info("Initializing dataloader")
    dataloader = DataLoader(fastramqpi.get_context())
    fastramqpi.add_context(dataloader=dataloader)

    userNameGeneratorClass_string = mapping["username_generator"]["objectClass"]
    logger.info(f"Importing {userNameGeneratorClass_string}")
    UserNameGenerator = getattr(usernames, userNameGeneratorClass_string)

    logger.info("Initializing username generator")
    username_generator = UserNameGenerator(fastramqpi.get_context())
    fastramqpi.add_context(username_generator=username_generator)

    if not hasattr(username_generator, "generate_dn"):
        raise AttributeError("Username generator needs to have a generate_dn function")

    logger.info("Initializing os2mo-init engine")
    init_engine = InitEngine(fastramqpi.get_context())
    init_engine.create_facets()
    init_engine.create_it_systems()
    fastramqpi.add_context(init_engine=init_engine)

    logger.info("Initializing converters")
    converter = LdapConverter(fastramqpi.get_context())
    fastramqpi.add_context(cpr_field=converter.cpr_field)
    fastramqpi.add_context(ldap_it_system_user_key=converter.ldap_it_system)
    fastramqpi.add_context(converter=converter)

    logger.info("Initializing internal AMQP system")
    internal_amqpsystem = AMQPSystem(
        settings=settings.internal_amqp, router=internal_amqp_router  # type: ignore
    )
    fastramqpi.add_context(internal_amqpsystem=internal_amqpsystem)
    fastramqpi.add_lifespan_manager(internal_amqpsystem)
    internal_amqpsystem.router.registry.update(internal_amqp_router.registry)
    internal_amqpsystem.context = fastramqpi._context

    logger.info("Starting export checks module")
    export_checks = ExportChecks(fastramqpi.get_context())
    fastramqpi.add_context(export_checks=export_checks)

    logger.info("Initializing Sync tool")
    sync_tool = SyncTool(fastramqpi.get_context())
    fastramqpi.add_context(sync_tool=sync_tool)

    logger.info("Starting LDAP listener")
    fastramqpi.add_context(event_loop=asyncio.get_event_loop())
    fastramqpi.add_context(poll_time=settings.poll_time)

    if settings.listen_to_changes_in_ldap:
        pollers = setup_listener(
            fastramqpi.get_context(),
            partial(listener, fastramqpi.get_context()),
        )
        fastramqpi.add_context(pollers=pollers)
        fastramqpi.add_healthcheck(name="LDAPPoller", healthcheck=poller_healthcheck)

    return fastramqpi


def encode_result(result):
    # This removes all bytes objects from the result. for example images
    json_compatible_result = jsonable_encoder(
        result, custom_encoder={bytes: lambda v: None}
    )
    return json_compatible_result


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)
    settings = Settings(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    # Fix for for login manager not respecting root_path
    # See https://github.com/tiangolo/fastapi/issues/5778
    app.mount("/ldap_ie", app)

    login_manager = LoginManager(
        settings.authentication_secret.get_secret_value(),
        "/ldap_ie/login",
        default_expiry=timedelta(hours=settings.token_expiry_time),
    )

    user_database = {
        "admin": {
            "password": settings.admin_password.get_secret_value(),
        }
    }
    user_loader: Callable = login_manager.user_loader

    @user_loader()
    def query_user(user_id: str):
        return user_database.get(user_id)

    user_context = fastramqpi._context["user_context"]
    converter = user_context["converter"]
    dataloader = user_context["dataloader"]
    ldap_connection = user_context["ldap_connection"]
    internal_amqpsystem = user_context["internal_amqpsystem"]
    sync_tool = user_context["sync_tool"]
    cpr_field = user_context["cpr_field"]

    attribute_types = get_attribute_types(ldap_connection)
    accepted_attributes = tuple(sorted(attribute_types.keys()))

    ldap_classes = tuple(sorted(converter.overview.keys()))
    default_ldap_class = converter.raw_mapping["mo_to_ldap"]["Employee"]["objectClass"]

    accepted_json_keys = tuple(converter.get_accepted_json_keys())

    @app.post("/login")
    def login(data: OAuth2PasswordRequestForm = Depends()):
        user_id = data.username
        password = data.password

        user = query_user(user_id)
        if not user or password != user["password"]:
            raise InvalidCredentialsException

        access_token = login_manager.create_access_token(data={"sub": user_id})
        return {"access_token": access_token}

    @app.post("/reload_info_dicts", status_code=202, tags=["Maintenance"])
    async def reload_info_dicts(user=Depends(login_manager)):
        """
        Endpoint to reload info dicts on the converter. To make sure that they are
        up-to-date and represent the information in OS2mo.
        """
        converter.load_info_dicts()

    # Load all users from LDAP, and import them into MO
    @app.get("/Import", status_code=202, tags=["Import"])
    async def import_all_objects_from_LDAP(
        test_on_first_20_entries: bool = False,
        user=Depends(login_manager),
        delay_in_hours: int = 0,
        delay_in_minutes: int = 0,
        delay_in_seconds: float = 0,
        cpr_indexed_entries_only: bool = True,
        search_base: Union[str, None] = None,
    ) -> Any:

        if cpr_indexed_entries_only and not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        delay = delay_in_hours * 60 * 60 + delay_in_minutes * 60 + delay_in_seconds
        if delay > 0:
            await countdown(delay, "/Import")

        all_ldap_objects = await dataloader.load_ldap_objects(
            "Employee",
            search_base=search_base,
        )

        if test_on_first_20_entries:
            # Only upload the first 20 entries
            logger.info("Slicing the first 20 entries")
            all_ldap_objects = all_ldap_objects[:20]

        number_of_entries = len(all_ldap_objects)
        logger.info(f"Found {number_of_entries} entries in AD")

        with tqdm(total=number_of_entries, unit="ldap object") as progress_bar:
            progress_bar.set_description("LDAP import progress")

            # Note: This can be done in a more parallel way using asyncio.gather() but:
            # - it was experienced that fastapi throws broken pipe errors
            # - MO was observed to not handle that well either.
            # - We don't need the additional speed. This is meant as a one-time import
            for ldap_object in all_ldap_objects:
                logger.info(f"Importing {ldap_object.dn}")
                if cpr_indexed_entries_only:
                    cpr_no = getattr(ldap_object, cpr_field)
                    try:
                        validate_cpr(cpr_no)
                    except (ValueError, TypeError):
                        logger.info(f"{cpr_no} is not a valid cpr number")
                        progress_bar.update()
                        continue

                await sync_tool.import_single_user(ldap_object.dn, manual_import=True)

                progress_bar.update()

    # Load a single user from LDAP, and import him/her/hir into MO
    @app.get("/Import/{objectGUID}", status_code=202, tags=["Import"])
    async def import_single_user_from_LDAP(
        objectGUID: UUID,
        user=Depends(login_manager),
    ) -> Any:
        dn = dataloader.get_ldap_dn(objectGUID)
        await sync_tool.import_single_user(dn, manual_import=True)

    class ExportQueryParams:
        def __init__(
            self,
            publish_amqp_messages: bool = Query(
                True,
                description=(
                    "If False, do not publish anything, "
                    "just inspect what would be published"
                ),
            ),
            object_uuid: str = Query(
                "", description="If specified, export only the object with this uuid"
            ),
            delay_in_hours: int = Query(
                0,
                description="Number of hours to wait before starting this job",
            ),
            delay_in_minutes: int = Query(
                0,
                description="Number of minutes to wait before starting this job",
            ),
            delay_in_seconds: float = Query(
                0,
                description="Number of seconds to wait before starting this job",
            ),
        ):
            self.publish_amqp_messages = publish_amqp_messages
            self.object_uuid = object_uuid
            self.delay_in_hours = delay_in_hours
            self.delay_in_minutes = delay_in_minutes
            self.delay_in_seconds = delay_in_seconds

    # Export object(s) from MO to LDAP
    @app.post("/Export", status_code=202, tags=["Export"])
    async def export_mo_objects(
        user=Depends(login_manager),
        params: ExportQueryParams = Depends(),
    ) -> Any:
        delay = (
            params.delay_in_hours * 60 * 60
            + params.delay_in_minutes * 60
            + params.delay_in_seconds
        )
        if delay > 0:
            await countdown(delay, "/Export")

        # Load mo objects
        mo_objects = await dataloader.load_all_mo_objects(uuid=params.object_uuid)
        logger.info(f"Found {len(mo_objects)} objects")

        for mo_object in mo_objects:
            routing_key = MORoutingKey.build(
                service_type=mo_object["service_type"],
                object_type=mo_object["object_type"],
                request_type=RequestType.REFRESH,
            )
            payload = mo_object["payload"]

            logger.info(f"Publishing {routing_key}")
            logger.info(f"payload.uuid = {payload.uuid}")
            logger.info(f"payload.object_uuid = {payload.object_uuid}")

            if params.publish_amqp_messages:
                await internal_amqpsystem.publish_message(
                    str(routing_key), jsonable_encoder(payload)
                )

    # Get all objects from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/converted", status_code=202, tags=["LDAP"])
    async def convert_all_objects_from_ldap(
        json_key: Literal[accepted_json_keys],  # type: ignore
        user=Depends(login_manager),
    ) -> Any:
        result = await dataloader.load_ldap_objects(json_key)
        converted_results = []
        for r in result:
            try:
                converted_results.extend(
                    converter.from_ldap(r, json_key, employee_uuid=uuid4())
                )
            except ValidationError as e:
                logger.error(f"Cannot convert {r} to MO {json_key}: {e}")
        return converted_results

    # Get a specific cpr-indexed object from LDAP
    @app.get("/LDAP/{json_key}/{cpr}", status_code=202, tags=["LDAP"])
    async def load_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str = Depends(valid_cpr),
        user=Depends(login_manager),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key, ["objectGUID"])
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        response: Response,
        user=Depends(login_manager),
        cpr: str = Depends(valid_cpr),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        try:
            return converter.from_ldap(result, json_key, employee_uuid=uuid4())
        except ValidationError as e:
            logger.error(f"Cannot convert {result} to MO {json_key}: {e}")
            response.status_code = (
                status.HTTP_404_NOT_FOUND
            )  # TODO: return other status?
            return None

    # Get all objects from LDAP
    @app.get("/LDAP/{json_key}", status_code=202, tags=["LDAP"])
    async def load_all_objects_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        user=Depends(login_manager),
        entries_to_return: int = Query(ge=1),
    ) -> Any:
        result = await dataloader.load_ldap_objects(json_key, ["objectGUID"])
        return encode_result(result[-entries_to_return:])

    # Get all objects from LDAP with invalid cpr numbers
    @app.get("/Inspect/invalid_cpr_numbers", status_code=202, tags=["LDAP"])
    async def get_invalid_cpr_numbers_from_LDAP(user=Depends(login_manager)) -> Any:
        if not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        result = await dataloader.load_ldap_objects("Employee")

        formatted_result = {}
        for entry in result:
            cpr = str(getattr(entry, cpr_field))

            try:
                validate_cpr(cpr)
            except ValueError:
                formatted_result[entry.dn] = cpr
        return formatted_result

    # Modify a person in LDAP
    @app.post("/LDAP/{json_key}", tags=["LDAP"])
    async def post_object_to_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        ldap_object: LdapObject,
        user=Depends(login_manager),
    ) -> Any:
        await dataloader.modify_ldap_object(ldap_object, json_key)

    # Post an object to MO
    @app.post("/MO/{json_key}", tags=["MO"])
    async def post_object_to_MO(
        json_key: Literal[accepted_json_keys],  # type: ignore
        mo_object_json: dict,
        user=Depends(login_manager),
    ) -> None:
        mo_object = converter.import_mo_object_class(json_key)
        logger.info(f"Posting {mo_object} = {mo_object_json} to MO")
        await dataloader.upload_mo_objects([mo_object(**mo_object_json)])

    # Get a speficic address from MO
    @app.get("/MO/Address/{uuid}", status_code=202, tags=["MO"])
    async def load_address_from_MO(
        uuid: UUID, request: Request, user=Depends(login_manager)
    ) -> Any:
        result = await dataloader.load_mo_address(uuid)
        return result

    # Get a speficic person from MO
    @app.get("/MO/Employee/{uuid}", status_code=202, tags=["MO"])
    async def load_employee_from_MO(
        uuid: UUID, request: Request, user=Depends(login_manager)
    ) -> Any:
        result = await dataloader.load_mo_employee(uuid)
        return result

    # Get LDAP overview
    @app.get("/Inspect/overview", status_code=202, tags=["LDAP"])
    async def load_overview_from_LDAP(
        user=Depends(login_manager),
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_overview()
        return ldap_overview[ldap_class]

    # Get populated LDAP overview
    @app.get("/Inspect/overview/populated", status_code=202, tags=["LDAP"])
    async def load_populated_overview_from_LDAP(
        user=Depends(login_manager),
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_populated_overview(
            ldap_classes=[ldap_class]
        )
        return encode_result(ldap_overview.get(ldap_class))

    # Get LDAP attribute details
    @app.get("/Inspect/attribute/{attribute}", status_code=202, tags=["LDAP"])
    async def load_attribute_details_from_LDAP(
        attribute: Literal[accepted_attributes],  # type: ignore
        user=Depends(login_manager),
    ) -> Any:
        return attribute_types[attribute]

    # Get LDAP attribute values
    @app.get("/Inspect/attribute/values/{attribute}", status_code=202, tags=["LDAP"])
    async def load_unique_attribute_values_from_LDAP(
        attribute: Literal[accepted_attributes],  # type: ignore
        user=Depends(login_manager),
    ) -> Any:
        return dataloader.load_ldap_attribute_values(attribute)

    # Get LDAP object
    @app.get("/Inspect/object/{objectGUID}", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap(
        objectGUID: UUID, user=Depends(login_manager), nest: bool = False
    ) -> Any:
        dn = dataloader.get_ldap_dn(objectGUID)
        return encode_result(dataloader.load_ldap_object(dn, ["*"], nest=nest))

    # Get MO address types
    @app.get("/MO/Address_types_org_unit", status_code=202, tags=["MO"])
    async def load_org_unit_address_types_from_MO(user=Depends(login_manager)) -> Any:
        result = dataloader.load_mo_org_unit_address_types()
        return result

    # Get MO address types
    @app.get("/MO/Address_types_employee", status_code=202, tags=["MO"])
    async def load_employee_address_types_from_MO(user=Depends(login_manager)) -> Any:
        result = dataloader.load_mo_employee_address_types()
        return result

    # Get MO IT system types
    @app.get("/MO/IT_systems", status_code=202, tags=["MO"])
    async def load_it_systems_from_MO(user=Depends(login_manager)) -> Any:
        result = dataloader.load_mo_it_systems()
        return result

    # Get MO primary types
    @app.get("/MO/Primary_types", status_code=202, tags=["MO"])
    async def load_primary_types_from_MO(user=Depends(login_manager)) -> Any:
        return dataloader.load_mo_primary_types()

    class SyncQueryParams:
        def __init__(
            self,
            publish_amqp_messages: bool = Query(
                True,
                description=(
                    "If False, do not publish anything, "
                    "just inspect what would be published"
                ),
            ),
        ):
            self.publish_amqp_messages = publish_amqp_messages

    # Load all objects with to/from dates == today and send amqp messages for them
    @app.post("/Synchronize_todays_events", status_code=202, tags=["Maintenance"])
    async def synchronize_todays_events(
        user=Depends(login_manager),
        date: Union[datetime.date, None] = None,
        params: SyncQueryParams = Depends(),
    ) -> Any:

        date = date or datetime.date.today()

        # Load all objects
        all_objects = await dataloader.load_all_mo_objects(add_validity=True)

        # Filter out all that is not from/to today and determine request type
        # Note: It is not possible in graphql (yet?) To load just today's objects
        todays_objects = []
        for mo_object in all_objects:
            from_date = mo_datestring_to_utc(mo_object["validity"]["from"])
            to_date = mo_datestring_to_utc(mo_object["validity"]["to"])
            if from_date and from_date.date() == date:
                if to_date and to_date.date() == date:
                    mo_object["request_type"] = RequestType.TERMINATE
                else:
                    mo_object["request_type"] = RequestType.REFRESH
                todays_objects.append(mo_object)
            elif to_date and to_date.date() == date:
                mo_object["request_type"] = RequestType.TERMINATE
                todays_objects.append(mo_object)

        def sorting_key(mo_object):
            return 0 if mo_object["request_type"] == RequestType.TERMINATE else 1

        # Make sure that we send termination messages before other messages
        # Otherwise we risk that newly exported information gets erased right away
        todays_objects = sorted(todays_objects, key=sorting_key)

        logger.info(
            f"Found {len(todays_objects)} objects which are valid from/to today"
        )

        for mo_object in todays_objects:
            routing_key = MORoutingKey.build(
                service_type=mo_object["service_type"],
                object_type=mo_object["object_type"],
                request_type=mo_object["request_type"],
            )
            payload = mo_object["payload"]

            logger.info(f"Publishing {routing_key}")
            logger.info(f"payload.uuid = {payload.uuid}")
            logger.info(f"payload.object_uuid = {payload.object_uuid}")

            # Note: OS2mo does not send out AMQP messages (yet) when objects become
            # valid. That is why we have to do it ourselves.
            if params.publish_amqp_messages and settings.listen_to_changes_in_mo:
                await internal_amqpsystem.publish_message(
                    str(routing_key), jsonable_encoder(payload)
                )

    return app
