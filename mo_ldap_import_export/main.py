# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
import asyncio
import datetime
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import partial
from functools import wraps
from inspect import iscoroutinefunction
from typing import Annotated
from typing import Any
from typing import Literal
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
from fastapi_utils.tasks import repeat_every
from fastramqpi.main import FastRAMQPI
from gql.transport.exceptions import TransportQueryError
from ldap3 import Connection
from pydantic import ValidationError
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramodels.mo._shared import validate_cpr
from ramqp import AMQPSystem
from ramqp.depends import Context
from ramqp.depends import rate_limit
from ramqp.mo import MORouter
from ramqp.mo import MORoutingKey
from ramqp.mo import PayloadUUID
from ramqp.utils import RejectMessage
from ramqp.utils import RequeueMessage
from tqdm import tqdm

from . import usernames
from .config import Settings
from .converters import LdapConverter
from .customer_specific_checks import ExportChecks
from .customer_specific_checks import ImportChecks
from .dataloaders import DataLoader
from .dependencies import valid_cpr
from .exceptions import CPRFieldNotFound
from .exceptions import IgnoreChanges
from .exceptions import IncorrectMapping
from .exceptions import NoObjectsReturnedException
from .exceptions import NotEnabledException
from .exceptions import NotSupportedException
from .exceptions import ObjectGUIDITSystemNotFound
from .import_export import SyncTool
from .ldap import check_ou_in_list_of_ous
from .ldap import configure_ldap_connection
from .ldap import get_attribute_types
from .ldap import ldap_healthcheck
from .ldap import paged_search
from .ldap import poller_healthcheck
from .ldap import setup_listener
from .ldap_classes import LdapObject
from .logging import logger
from .os2mo_init import InitEngine
from .processors import _hide_cpr as hide_cpr
from .utils import countdown
from .utils import get_object_type_from_routing_key
from .utils import listener
from .utils import mo_datestring_to_utc

fastapi_router = APIRouter()
amqp_router = MORouter()
internal_amqp_router = MORouter()
delay_on_error = 10  # Try errors again after a short period of time
delay_on_requeue = 60 * 60 * 24  # Requeue messages for tomorrow (or after a reboot)
RateLimit = Annotated[None, Depends(rate_limit(delay_on_error))]


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
            NotEnabledException,  # In case a feature is not enabled: Abort
        ) as e:
            logger.info(e)
            raise RejectMessage()
        except RequeueMessage:
            await asyncio.sleep(delay_on_requeue)
            raise

    modified_func.__wrapped__ = func  # type: ignore
    return modified_func


def get_delete_flag(mo_object) -> bool:
    """
    Determines if an object should be deleted based on the validity to-date
    """
    now = datetime.datetime.utcnow()
    validity_to = mo_datestring_to_utc(mo_object["validity"]["to"])
    if validity_to and validity_to <= now:
        logger.info(
            "[Get-delete-flag] Returning delete=True because "
            f"to-date ({validity_to}) <= current date ({now})"
        )
        return True
    else:
        return False


async def unpack_payload(
    context: Context, object_uuid: PayloadUUID, mo_routing_key: MORoutingKey
):
    """
    Takes the payload of an AMQP message, and returns a set of parameters to be used
    by export functions in `import_export.py`. Also return the mo object as a dict
    """

    # If we are not supposed to listen: reject and turn the message into a dead letter.
    settings = context["user_context"]["settings"]
    if not settings.listen_to_changes_in_mo:
        logger.info("[Unpack-payload] listen_to_changes_in_mo = False. Aborting.")
        raise RejectMessage()

    logger.info(
        "[Unpack-payload] Unpacking payload.",
        mo_routing_key=mo_routing_key,
        object_uuid=str(object_uuid),
    )

    dataloader = context["user_context"]["dataloader"]

    object_type = get_object_type_from_routing_key(mo_routing_key)

    mo_object = await dataloader.load_mo_object(
        object_uuid,
        object_type,
        add_validity=True,
        current_objects_only=False,
    )

    delete = get_delete_flag(mo_object)
    current_objects_only = False if delete else True

    args = dict(
        uuid=mo_object["parent_uuid"],
        object_uuid=object_uuid,
        routing_key=mo_routing_key,
        delete=delete,
        current_objects_only=current_objects_only,
    )

    return args, mo_object


@internal_amqp_router.register("address")
@amqp_router.register("address")
@reject_on_failure
async def process_address(
    context: Context,
    object_uuid: PayloadUUID,
    mo_routing_key: MORoutingKey,
    _: RateLimit,
) -> None:
    args, mo_object = await unpack_payload(context, object_uuid, mo_routing_key)
    service_type = mo_object["service_type"]

    sync_tool = context["user_context"]["sync_tool"]
    if service_type == "employee":
        await sync_tool.listen_to_changes_in_employees(**args)
    elif service_type == "org_unit":
        await sync_tool.listen_to_changes_in_org_units(**args)


@internal_amqp_router.register("engagement")
@amqp_router.register("engagement")
@reject_on_failure
async def process_engagement(
    context: Context,
    object_uuid: PayloadUUID,
    mo_routing_key: MORoutingKey,
    _: RateLimit,
) -> None:
    args, _ = await unpack_payload(context, object_uuid, mo_routing_key)

    sync_tool = context["user_context"]["sync_tool"]
    await sync_tool.listen_to_changes_in_employees(**args)
    await sync_tool.export_org_unit_addresses_on_engagement_change(**args)


@internal_amqp_router.register("ituser")
@amqp_router.register("ituser")
@reject_on_failure
async def process_ituser(
    context: Context,
    object_uuid: PayloadUUID,
    mo_routing_key: MORoutingKey,
    _: RateLimit,
) -> None:
    args, _ = await unpack_payload(context, object_uuid, mo_routing_key)

    sync_tool = context["user_context"]["sync_tool"]
    await sync_tool.listen_to_changes_in_employees(**args)


@internal_amqp_router.register("person")
@amqp_router.register("person")
@reject_on_failure
async def process_person(
    context: Context,
    object_uuid: PayloadUUID,
    mo_routing_key: MORoutingKey,
    _: RateLimit,
) -> None:
    args, _ = await unpack_payload(context, object_uuid, mo_routing_key)

    sync_tool = context["user_context"]["sync_tool"]
    await sync_tool.listen_to_changes_in_employees(**args)


@internal_amqp_router.register("org_unit")
@amqp_router.register("org_unit")
@reject_on_failure
async def process_org_unit(
    context: Context,
    object_uuid: PayloadUUID,
    mo_routing_key: MORoutingKey,
    _: RateLimit,
) -> None:
    args, _ = await unpack_payload(context, object_uuid, mo_routing_key)

    sync_tool = context["user_context"]["sync_tool"]
    await sync_tool.listen_to_changes_in_org_units(**args)


@asynccontextmanager
async def open_ldap_connection(ldap_connection: Connection) -> AsyncIterator[None]:
    """Open the LDAP connection during FastRAMQPI lifespan.

    Yields:
        None
    """
    with ldap_connection:
        yield


def construct_gql_client(settings: Settings, version: str = "v7"):
    return PersistentGraphQLClient(
        url=settings.mo_url + "/graphql/" + version,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
        auth_server=settings.auth_server,
        auth_realm=settings.auth_realm,
        execute_timeout=settings.graphql_timeout,
        httpx_client_kwargs={"timeout": settings.graphql_timeout},
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
) -> tuple[PersistentGraphQLClient, ModelClient]:
    """Construct clients froms settings.

    Args:
        settings: Integration settings module.

    Returns:
        Tuple with PersistentGraphQLClient and ModelClient.
    """
    gql_client = construct_gql_client(settings)
    model_client = construct_model_client(settings)
    return gql_client, model_client


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def initialize_sync_tool(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    logger.info("Initializing Sync tool")
    sync_tool = SyncTool(fastramqpi.get_context())
    fastramqpi.add_context(sync_tool=sync_tool)
    yield


@asynccontextmanager
async def initialize_checks(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    logger.info("Initializing Import/Export checks")
    export_checks = ExportChecks(fastramqpi.get_context())
    import_checks = ImportChecks(fastramqpi.get_context())
    fastramqpi.add_context(export_checks=export_checks, import_checks=import_checks)
    yield


@asynccontextmanager
async def initialize_converters(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    logger.info("Initializing converters")
    converter = LdapConverter(fastramqpi.get_context())
    await converter._init()
    fastramqpi.add_context(cpr_field=converter.cpr_field)
    fastramqpi.add_context(ldap_it_system_user_key=converter.ldap_it_system)
    fastramqpi.add_context(converter=converter)
    yield


@asynccontextmanager
async def initialize_init_engine(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    logger.info("Initializing os2mo-init engine")
    init_engine = InitEngine(fastramqpi.get_context())
    await init_engine.create_facets()
    await init_engine.create_it_systems()
    fastramqpi.add_context(init_engine=init_engine)
    yield


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
    fastramqpi = FastRAMQPI(application_name="ldap_ie", settings=settings.fastramqpi)
    fastramqpi.add_context(settings=settings)

    logger.info("AMQP router setup")
    amqpsystem = fastramqpi.get_amqpsystem()
    amqpsystem.router.registry.update(amqp_router.registry)

    logger.info("Setting up clients")
    gql_client, model_client = construct_clients(settings)
    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)
    fastramqpi._context["graphql_client"] = gql_client

    logger.info("Configuring LDAP connection")
    ldap_connection = configure_ldap_connection(settings)
    fastramqpi.add_context(ldap_connection=ldap_connection)
    fastramqpi.add_healthcheck(name="LDAPConnection", healthcheck=ldap_healthcheck)
    fastramqpi.add_lifespan_manager(
        open_ldap_connection(ldap_connection), 1500  # type: ignore
    )

    logger.info("Loading mapping file")
    mapping = settings.conversion_mapping.dict(exclude_unset=True, by_alias=True)
    fastramqpi.add_context(mapping=mapping)

    mappings_path = os.path.join(os.path.dirname(__file__), "mappings")
    forbidden_usernames_path = os.path.join(mappings_path, "forbidden_usernames")
    fastramqpi.add_context(forbidden_usernames_path=forbidden_usernames_path)

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

    if not iscoroutinefunction(getattr(username_generator, "generate_dn")):
        raise TypeError("generate_dn function needs to be a coroutine")

    fastramqpi.add_lifespan_manager(initialize_init_engine(fastramqpi), 2700)
    fastramqpi.add_lifespan_manager(initialize_converters(fastramqpi), 2800)

    logger.info("Initializing internal AMQP system")
    internal_amqpsystem = AMQPSystem(
        settings=settings.internal_amqp, router=internal_amqp_router  # type: ignore
    )
    fastramqpi.add_context(internal_amqpsystem=internal_amqpsystem)
    fastramqpi.add_lifespan_manager(internal_amqpsystem)
    internal_amqpsystem.router.registry.update(internal_amqp_router.registry)
    internal_amqpsystem.context = fastramqpi._context

    fastramqpi.add_lifespan_manager(initialize_checks(fastramqpi), 2900)
    fastramqpi.add_lifespan_manager(initialize_sync_tool(fastramqpi), 3000)

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
        result, custom_encoder={bytes: lambda _: None}
    )
    return json_compatible_result


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    user_context = fastramqpi._context["user_context"]
    dataloader = user_context["dataloader"]
    ldap_connection = user_context["ldap_connection"]
    internal_amqpsystem = user_context["internal_amqpsystem"]
    mapping = user_context["mapping"]
    settings = user_context["settings"]

    attribute_types = get_attribute_types(ldap_connection)
    accepted_attributes = tuple(sorted(attribute_types.keys()))

    overview = dataloader.load_ldap_overview()
    ldap_classes = tuple(sorted(overview.keys()))

    default_ldap_class = mapping["mo_to_ldap"]["Employee"]["objectClass"]
    accepted_json_keys = tuple(sorted(mapping["mo_to_ldap"].keys()))

    # TODO: Eliminate this function and make reloading dicts eventdriven
    #       When this method is eliminated the fastapi_utils package can be removed
    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24)
    async def reload_info_dicts() -> None:  # pragma: no cover
        """
        Endpoint to reload info dicts on the converter. To make sure that they are
        up-to-date and represent the information in OS2mo.
        """
        converter = user_context["converter"]
        await converter.load_info_dicts()

    # Load all users from LDAP, and import them into MO
    @app.get("/Import", status_code=202, tags=["Import"])
    async def import_all_objects_from_LDAP(
        test_on_first_20_entries: bool = False,
        delay_in_hours: int = 0,
        delay_in_minutes: int = 0,
        delay_in_seconds: float = 0,
        cpr_indexed_entries_only: bool = True,
        search_base: str | None = None,
    ) -> Any:
        converter = user_context["converter"]
        cpr_field = converter.cpr_field
        sync_tool = user_context["sync_tool"]

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
    @app.get("/Import/{unique_ldap_uuid}", status_code=202, tags=["Import"])
    async def import_single_user_from_LDAP(
        unique_ldap_uuid: UUID,
    ) -> Any:
        sync_tool = user_context["sync_tool"]

        dn = dataloader.get_ldap_dn(unique_ldap_uuid)
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

    # Export all objects related to a single employee from MO to LDAP
    @app.post("/Export/{employee_uuid}", status_code=202, tags=["Export"])
    async def export_mo_employee(
        employee_uuid: UUID,
    ) -> Any:
        sync_tool = user_context["sync_tool"]
        await sync_tool.refresh_employee(employee_uuid)

    # Export object(s) from MO to LDAP
    @app.post("/Export", status_code=202, tags=["Export"])
    async def export_mo_objects(
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
            routing_key = mo_object["object_type"]
            payload = mo_object["payload"]

            logger.info(
                "[Export-mo-objects] Publishing.",
                routing_key=routing_key,
                payload=payload,
            )

            if params.publish_amqp_messages:
                await internal_amqpsystem.publish_message(routing_key, payload)

    # Get all objects from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/converted", status_code=202, tags=["LDAP"])
    async def convert_all_objects_from_ldap(
        json_key: Literal[accepted_json_keys],  # type: ignore
    ) -> Any:
        converter = user_context["converter"]
        result = await dataloader.load_ldap_objects(json_key)
        converted_results = []
        for r in result:
            try:
                converted_results.extend(
                    await converter.from_ldap(r, json_key, employee_uuid=uuid4())
                )
            except ValidationError as e:
                logger.error(f"Cannot convert {r} to MO {json_key}: {e}")
        return converted_results

    # Get a specific cpr-indexed object from LDAP
    @app.get("/LDAP/{json_key}/{cpr}", status_code=202, tags=["LDAP"])
    async def load_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str = Depends(valid_cpr),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(
            cpr, json_key, [settings.ldap_unique_id_field]
        )
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        response: Response,
        cpr: str = Depends(valid_cpr),
    ) -> Any:
        converter = user_context["converter"]
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        try:
            return await converter.from_ldap(result, json_key, employee_uuid=uuid4())
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
        entries_to_return: int = Query(ge=1),
    ) -> Any:
        result = await dataloader.load_ldap_objects(
            json_key, [settings.ldap_unique_id_field]
        )
        return encode_result(result[-entries_to_return:])

    @app.get("/Inspect/non_existing_unique_ldap_uuids", status_code=202, tags=["LDAP"])
    async def get_non_existing_unique_ldap_uuids_from_MO() -> Any:
        it_system_uuid = dataloader.get_ldap_it_system_uuid()
        if not it_system_uuid:
            raise ObjectGUIDITSystemNotFound("Could not find it_system_uuid")

        def to_uuid(uuid_string: str) -> UUID | str:
            try:
                return UUID(uuid_string)
            except ValueError:
                return uuid_string

        all_unique_ldap_uuids = [
            to_uuid(u)
            for u in dataloader.load_ldap_attribute_values(
                settings.ldap_unique_id_field
            )
        ]
        all_it_users = await dataloader.load_all_current_it_users(it_system_uuid)

        # Find unique ldap UUIDs which are stored in MO but do not exist in LDAP
        non_existing_unique_ldap_uuids = []
        for it_user in all_it_users:
            unique_ldap_uuid = to_uuid(it_user["user_key"])
            if unique_ldap_uuid not in all_unique_ldap_uuids:
                employee = await dataloader.load_mo_employee(it_user["employee_uuid"])
                output_dict = {
                    "name": f"{employee.givenname} {employee.surname}".strip(),
                    "MO employee uuid": employee.uuid,
                    "unique_ldap_uuid in MO": it_user["user_key"],
                }
                non_existing_unique_ldap_uuids.append(output_dict)

        return non_existing_unique_ldap_uuids

    @app.get("/Inspect/duplicate_cpr_numbers", status_code=202, tags=["LDAP"])
    async def get_duplicate_cpr_numbers_from_LDAP() -> Any:
        converter = user_context["converter"]
        cpr_field = converter.cpr_field
        if not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        searchParameters = {
            "search_filter": "(objectclass=*)",
            "attributes": [cpr_field],
        }

        responses = [
            r
            for r in paged_search(fastramqpi._context, searchParameters)
            if r["attributes"][cpr_field]
        ]

        cpr_values = [r["attributes"][cpr_field] for r in responses]
        output = {}

        for cpr in set(cpr_values):
            if cpr_values.count(cpr) > 1:
                output[hide_cpr(cpr)] = [
                    r["dn"] for r in responses if r["attributes"][cpr_field] == cpr
                ]

        return output

    # Get all objects from LDAP with invalid cpr numbers
    @app.get("/Inspect/invalid_cpr_numbers", status_code=202, tags=["LDAP"])
    async def get_invalid_cpr_numbers_from_LDAP() -> Any:
        converter = user_context["converter"]
        cpr_field = converter.cpr_field
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
    ) -> Any:
        await dataloader.modify_ldap_object(ldap_object, json_key)

    # Post an object to MO
    @app.post("/MO/{json_key}", tags=["MO"])
    async def post_object_to_MO(
        json_key: Literal[accepted_json_keys],  # type: ignore
        mo_object_json: dict,
    ) -> None:
        converter = user_context["converter"]
        mo_object = converter.import_mo_object_class(json_key)
        logger.info(f"Posting {mo_object} = {mo_object_json} to MO")
        await dataloader.upload_mo_objects([mo_object(**mo_object_json)])

    # Get a speficic address from MO
    @app.get("/MO/Address/{uuid}", status_code=202, tags=["MO"])
    async def load_address_from_MO(
        uuid: UUID,
        request: Request,
    ) -> Any:
        result = await dataloader.load_mo_address(uuid)
        return result

    # Get a speficic person from MO
    @app.get("/MO/Employee/{uuid}", status_code=202, tags=["MO"])
    async def load_employee_from_MO(
        uuid: UUID,
        request: Request,
    ) -> Any:
        result = await dataloader.load_mo_employee(uuid)
        return result

    # Get LDAP overview
    @app.get("/Inspect/overview", status_code=202, tags=["LDAP"])
    async def load_overview_from_LDAP(
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_overview()
        return ldap_overview[ldap_class]

    # Get LDAP overview
    @app.get("/Inspect/structure", status_code=202, tags=["LDAP"])
    async def load_structure_from_LDAP(search_base: str | None = None) -> Any:
        return dataloader.load_ldap_OUs(search_base=search_base)

    # Get populated LDAP overview
    @app.get("/Inspect/overview/populated", status_code=202, tags=["LDAP"])
    async def load_populated_overview_from_LDAP(
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
    ) -> Any:
        return attribute_types[attribute]

    # Get LDAP attribute values
    @app.get("/Inspect/attribute/values/{attribute}", status_code=202, tags=["LDAP"])
    async def load_unique_attribute_values_from_LDAP(
        attribute: Literal[accepted_attributes],  # type: ignore
        search_base: str | None = None,
    ) -> Any:
        return dataloader.load_ldap_attribute_values(attribute, search_base=search_base)

    # Get LDAP object by unique_ldap_uuid
    @app.get("/Inspect/object/unique_ldap_uuid", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap_by_unique_ldap_uuid(
        unique_ldap_uuid: UUID, nest: bool = False
    ) -> Any:
        dn = dataloader.get_ldap_dn(unique_ldap_uuid)
        return encode_result(dataloader.load_ldap_object(dn, ["*"], nest=nest))

    # Get LDAP object by DN
    @app.get("/Inspect/object/dn", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap_by_dn(dn: str, nest: bool = False) -> Any:
        return encode_result(dataloader.load_ldap_object(dn, ["*"], nest=nest))

    # Get LDAP unique_ldap_uuid
    @app.get("/unique_ldap_uuid/{dn}", status_code=202, tags=["LDAP"])
    async def load_unique_uuid_from_ldap(dn: str) -> Any:
        return dataloader.get_ldap_unique_ldap_uuid(dn)

    # Get MO address types
    @app.get("/MO/Address_types_org_unit", status_code=202, tags=["MO"])
    async def load_org_unit_address_types_from_MO() -> Any:
        result = await dataloader.load_mo_org_unit_address_types()
        return result

    # Get MO address types
    @app.get("/MO/Address_types_employee", status_code=202, tags=["MO"])
    async def load_employee_address_types_from_MO() -> Any:
        result = await dataloader.load_mo_employee_address_types()
        return result

    # Get MO IT system types
    @app.get("/MO/IT_systems", status_code=202, tags=["MO"])
    async def load_it_systems_from_MO() -> Any:
        result = await dataloader.load_mo_it_systems()
        return result

    # Get MO primary types
    @app.get("/MO/Primary_types", status_code=202, tags=["MO"])
    async def load_primary_types_from_MO() -> Any:
        return await dataloader.load_mo_primary_types()

    return app
