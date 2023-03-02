# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
import datetime
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Literal
from typing import Tuple
from uuid import UUID
from uuid import uuid4

import structlog
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
from ramqp import AMQPSystem
from ramqp.mo import MORouter
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import RequestType
from ramqp.mo.models import ServiceType
from ramqp.utils import RejectMessage
from tqdm import tqdm

from . import usernames
from .config import Settings
from .converters import LdapConverter
from .converters import read_mapping_json
from .dataloaders import DataLoader
from .exceptions import IncorrectMapping
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .exceptions import NotSupportedException
from .ldap import cleanup
from .ldap import configure_ldap_connection
from .ldap import get_attribute_types
from .ldap import ldap_healthcheck
from .ldap_classes import LdapObject
from .utils import mo_datestring_to_utc

logger = structlog.get_logger()
fastapi_router = APIRouter()
amqp_router = MORouter()
internal_amqp_router = MORouter()

"""
Employee.schema()
help(MORouter)
help(ServiceType)
help(ObjectType)
help(RequestType)
"""

# UUIDs in this list will be ignored by listen_to_changes ONCE
uuids_to_ignore: dict[UUID, list[datetime.datetime]] = {}


def reject_on_failure(func):
    """
    Decorator to turn message into dead letter in case of exceptions.
    """

    async def modified_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except (
            NotSupportedException,  # For features that are not supported: Abort
            IncorrectMapping,  # If the json dict is incorrectly configured: Abort
            TransportQueryError,  # In case an ldap entry cannot be uploaded: Abort
            NoObjectsReturnedException,  # In case an object is deleted halfway: Abort
        ):
            raise RejectMessage()

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
            payload.object_uuid, add_validity=True
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
        if validity_to <= now:
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


async def listen_to_changes_in_employees(
    context: Context,
    payload: PayloadType,
    routing_key: MORoutingKey,
    delete: bool,
    current_objects_only: bool,
) -> None:

    logger.info("[MO] Registered change in the employee model")
    user_context = context["user_context"]
    dataloader = user_context["dataloader"]
    converter = user_context["converter"]

    # Get MO employee
    changed_employee = await dataloader.load_mo_employee(
        payload.uuid,
        current_objects_only=current_objects_only,
    )
    logger.info(f"Found Employee in MO: {changed_employee}")

    mo_object_dict: dict[str, Any] = {"mo_employee": changed_employee}

    if routing_key.object_type == ObjectType.EMPLOYEE:
        logger.info("[MO] Change registered in the employee object type")

        # Convert to LDAP
        ldap_employee = converter.to_ldap(mo_object_dict, "Employee")

        # Upload to LDAP - overwrite because all employee fields are unique.
        # One person cannot have multiple names.
        await dataloader.upload_ldap_object(
            ldap_employee,
            "Employee",
            overwrite=True,
            delete=delete,
        )

    elif routing_key.object_type == ObjectType.ADDRESS:
        logger.info("[MO] Change registered in the address object type")

        # Get MO address
        changed_address = await dataloader.load_mo_address(
            payload.object_uuid,
            current_objects_only=current_objects_only,
        )
        address_type_uuid = str(changed_address.address_type.uuid)
        json_key = converter.get_address_type_user_key(address_type_uuid)

        logger.info(f"Obtained address type user key = {json_key}")
        mo_object_dict["mo_employee_address"] = changed_address

        # Convert & Upload to LDAP
        await dataloader.upload_ldap_object(
            converter.to_ldap(mo_object_dict, json_key),
            json_key,
            delete=delete,
        )

        addresses_in_mo = await dataloader.load_mo_employee_addresses(
            changed_employee.uuid, changed_address.address_type.uuid
        )

        await cleanup(
            json_key,
            "value",
            "mo_employee_address",
            addresses_in_mo,
            user_context,
            changed_employee,
        )

    elif routing_key.object_type == ObjectType.IT:
        logger.info("[MO] Change registered in the IT object type")

        # Get MO IT-user
        changed_it_user = await dataloader.load_mo_it_user(
            payload.object_uuid,
            current_objects_only=current_objects_only,
        )
        it_system_type_uuid = changed_it_user.itsystem.uuid
        json_key = converter.get_it_system_user_key(it_system_type_uuid)

        logger.info(f"Obtained IT system name = {json_key}")
        mo_object_dict["mo_employee_it_user"] = changed_it_user

        # Convert & Upload to LDAP
        await dataloader.upload_ldap_object(
            converter.to_ldap(mo_object_dict, json_key),
            json_key,
            delete=delete,
        )

        # Load IT users belonging to this employee
        it_users_in_mo = await dataloader.load_mo_employee_it_users(
            changed_employee.uuid, it_system_type_uuid
        )

        await cleanup(
            json_key,
            "user_key",
            "mo_employee_it_user",
            it_users_in_mo,
            user_context,
            changed_employee,
        )

    elif routing_key.object_type == ObjectType.ENGAGEMENT:
        logger.info("[MO] Change registered in the Engagement object type")

        # Get MO Engagement
        changed_engagement = await dataloader.load_mo_engagement(
            payload.object_uuid,
            current_objects_only=current_objects_only,
        )

        json_key = "Engagement"
        mo_object_dict["mo_employee_engagement"] = changed_engagement

        # Convert & Upload to LDAP
        # Note: We upload an engagement to LDAP regardless of its 'primary' attribute.
        # Because it looks like you cannot set 'primary' when creating an engagement
        # in the OS2mo GUI.
        await dataloader.upload_ldap_object(
            converter.to_ldap(mo_object_dict, json_key),
            json_key,
            delete=delete,
        )

        engagements_in_mo = await dataloader.load_mo_employee_engagements(
            changed_employee.uuid
        )

        await cleanup(
            json_key,
            "user_key",
            "mo_employee_engagement",
            engagements_in_mo,
            user_context,
            changed_employee,
        )


async def listen_to_changes_in_org_units(
    context: Context,
    payload: PayloadType,
    routing_key: MORoutingKey,
    delete: bool,
    current_objects_only: bool,
) -> None:

    user_context = context["user_context"]
    dataloader = user_context["dataloader"]
    converter = user_context["converter"]

    # When an org-unit is changed we need to update the org unit info. So we
    # know the new name of the org unit in case it was changed
    if routing_key.object_type == ObjectType.ORG_UNIT:
        logger.info("Updating org unit info")
        converter.org_unit_info = dataloader.load_mo_org_units()
        converter.check_org_unit_info_dict()

    if routing_key.object_type == ObjectType.ADDRESS:
        logger.info("[MO] Change registered in the address object type")

        # Get MO address
        changed_address = await dataloader.load_mo_address(
            payload.object_uuid,
            current_objects_only=current_objects_only,
        )
        address_type_uuid = str(changed_address.address_type.uuid)
        json_key = converter.address_type_info[address_type_uuid]["user_key"]

        logger.info(f"Obtained address type user key = {json_key}")

        ldap_object_class = converter.find_ldap_object_class(json_key)
        employee_object_class = converter.find_ldap_object_class("Employee")

        if ldap_object_class != employee_object_class:
            raise NotSupportedException(
                (
                    "Mapping organization unit addresses "
                    "to non-employee objects is not supported"
                )
            )

        affected_employees = await dataloader.load_mo_employees_in_org_unit(
            payload.uuid
        )
        logger.info(f"[MO] Found {len(affected_employees)} affected employees")

        for affected_employee in affected_employees:
            mo_object_dict = {
                "mo_employee": affected_employee,
                "mo_org_unit_address": changed_address,
            }

            # Convert & Upload to LDAP
            await dataloader.upload_ldap_object(
                converter.to_ldap(mo_object_dict, json_key),
                json_key,
                delete=delete,
            )

            addresses_in_mo = await dataloader.load_mo_org_unit_addresses(
                payload.uuid, changed_address.address_type.uuid
            )

            await cleanup(
                json_key,
                "value",
                "mo_org_unit_address",
                addresses_in_mo,
                user_context,
                affected_employee,
            )


@internal_amqp_router.register("*.*.*")
@amqp_router.register("*.*.*")
@reject_on_failure
async def listen_to_changes(
    context: Context, payload: PayloadType, mo_routing_key: MORoutingKey
) -> None:
    global uuids_to_ignore

    # Remove all timestamps which have been in this dict for more than 60 seconds.
    now = datetime.datetime.now()
    for uuid, timestamps in uuids_to_ignore.items():
        for timestamp in timestamps:
            age_in_seconds = (now - timestamp).total_seconds()
            if age_in_seconds > 60:
                logger.info(
                    (
                        f"Removing timestamp belonging to {uuid} from uuids_to_ignore. "
                        f"It is {age_in_seconds} seconds old"
                    )
                )
                timestamps.remove(timestamp)

    # If the object was uploaded by us, it does not need to be synchronized.
    # Unless the serviceType is org_unit: Those potentially map to multiple employees.
    if (
        payload.object_uuid in uuids_to_ignore
        and uuids_to_ignore[payload.object_uuid]
        and mo_routing_key.service_type == ServiceType.EMPLOYEE
    ):
        logger.info(
            f"[listen_to_changes] Ignoring {mo_routing_key}-{payload.object_uuid}"
        )

        # Remove timestamp so it does not get ignored twice.
        oldest_timestamp = min(uuids_to_ignore[payload.object_uuid])
        uuids_to_ignore[payload.object_uuid].remove(oldest_timestamp)
        return None

    # If we are not supposed to listen: reject and turn the message into a dead letter.
    elif not Settings().listen_to_changes_in_mo:
        raise RejectMessage()

    logger.info(f"[MO] Routing key: {mo_routing_key}")
    logger.info(f"[MO] Payload: {payload}")

    delete = await get_delete_flag(mo_routing_key, payload, context)
    current_objects_only = False if delete else True

    args = dict(
        context=context,
        payload=payload,
        routing_key=mo_routing_key,
        delete=delete,
        current_objects_only=current_objects_only,
    )

    if mo_routing_key.service_type == ServiceType.EMPLOYEE:
        await listen_to_changes_in_employees(**args)
    elif mo_routing_key.service_type == ServiceType.ORG_UNIT:
        await listen_to_changes_in_org_units(**args)


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
        url=settings.mo_url + "/graphql/v2",
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

    logger.info("Initializing converters")
    converter = LdapConverter(fastramqpi.get_context())
    fastramqpi.add_context(cpr_field=converter.cpr_field)
    fastramqpi.add_context(converter=converter)

    logger.info("Initializing internal AMQP system")
    internal_amqpsystem = AMQPSystem(
        settings=settings.internal_amqp, router=internal_amqp_router  # type: ignore
    )
    fastramqpi.add_context(internal_amqpsystem=internal_amqpsystem)
    fastramqpi.add_lifespan_manager(internal_amqpsystem)
    internal_amqpsystem.router.registry.update(internal_amqp_router.registry)
    internal_amqpsystem.context = fastramqpi._context

    return fastramqpi


def encode_result(result):
    # This removes all bytes objects from the result. for example images
    json_compatible_result = jsonable_encoder(
        result, custom_encoder={bytes: lambda v: None}
    )
    return json_compatible_result


async def format_converted_objects(converted_objects, json_key, user_context):
    """
    for Address and Engagement objects:
        Loops through the objects, and sets the uuid if an existing matching object is
        found
    for ITUser objects:
        Loops through the objects and removes it if an existing matchin object is found
    for all other objects:
        returns the input list of converted_objects
    """

    converter = user_context["converter"]
    dataloader = user_context["dataloader"]
    mo_object_class = converter.find_mo_object_class(json_key).split(".")[-1]

    # Load addresses already in MO
    if mo_object_class == "Address":
        if converted_objects[0].person:
            objects_in_mo = await dataloader.load_mo_employee_addresses(
                converted_objects[0].person.uuid, converted_objects[0].address_type.uuid
            )
        elif converted_objects[0].org_unit:
            objects_in_mo = await dataloader.load_mo_org_unit_addresses(
                converted_objects[0].org_unit.uuid,
                converted_objects[0].address_type.uuid,
            )
        else:
            logger.info(
                (
                    "Could not format converted objects: "
                    "An address needs to have either a person uuid OR an org unit uuid"
                )
            )
            return []
        value_key = "value"

    # Load engagements already in MO
    elif mo_object_class == "Engagement":
        objects_in_mo = await dataloader.load_mo_employee_engagements(
            converted_objects[0].person.uuid
        )
        value_key = "user_key"
        user_keys = [o.user_key for o in objects_in_mo]

        # If we have duplicate user_keys, remove those which are the same as the primary
        # engagement's user_key
        if len(set(user_keys)) < len(user_keys):
            primary = [await dataloader.is_primary(o.uuid) for o in objects_in_mo]

            # There can be only one primary unit. Not sure what to do if there are
            # multiple, so better just do nothing.
            if sum(primary) == 1:
                primary_engagement = objects_in_mo[primary.index(True)]
                logger.info(
                    (
                        f"Found primary engagement with "
                        f"uuid={primary_engagement.uuid},"
                        f"user_key='{primary_engagement.user_key}'"
                    )
                )
                logger.info("Removing engagements with identical user keys")
                objects_in_mo = [
                    o
                    for o in objects_in_mo
                    if o == primary_engagement
                    or o.user_key != primary_engagement.user_key
                ]

    elif mo_object_class == "ITUser":
        # If an ITUser already exists, MO throws an error - it cannot be updated if the
        # key is identical to an existing key.
        it_users_in_mo = await dataloader.load_mo_employee_it_users(
            converted_objects[0].person.uuid, converted_objects[0].itsystem.uuid
        )
        user_keys_in_mo = [a.user_key for a in it_users_in_mo]

        return [
            converted_object
            for converted_object in converted_objects
            if converted_object.user_key not in user_keys_in_mo
        ]

    else:
        return converted_objects

    objects_in_mo_dict = {a.uuid: a for a in objects_in_mo}
    mo_attributes = converter.get_mo_attributes(json_key)

    # Set uuid if a matching one is found. so an object gets updated
    # instead of duplicated
    converted_objects_uuid_checked = []
    for converted_object in converted_objects:
        values_in_mo = [getattr(a, value_key) for a in objects_in_mo_dict.values()]
        converted_object_value = getattr(converted_object, value_key)

        if values_in_mo.count(converted_object_value) == 1:
            logger.info(
                (
                    f"Found matching MO '{json_key}' with "
                    f"value='{getattr(converted_object,value_key)}'"
                )
            )

            for uuid, mo_object in objects_in_mo_dict.items():
                value = getattr(mo_object, value_key)
                if value == converted_object_value:
                    matching_object_uuid = uuid
                    break

            matching_object = objects_in_mo_dict[matching_object_uuid]
            converted_mo_object_dict = converted_object.dict()

            mo_object_dict_to_upload = matching_object.dict()
            for key in mo_attributes:
                if (
                    key not in ["validity", "uuid", "objectClass"]
                    and key in converted_mo_object_dict.keys()
                ):
                    logger.info(f"Setting {key} = {converted_mo_object_dict[key]}")
                    mo_object_dict_to_upload[key] = converted_mo_object_dict[key]

            mo_class = converter.import_mo_object_class(json_key)
            converted_object_uuid_checked = mo_class(**mo_object_dict_to_upload)

            # If an object is identical to the one already there, it does not need
            # to be uploaded.
            if converted_object_uuid_checked == matching_object:
                logger.info(
                    "Converted object is identical to existing object. Skipping."
                )
            else:
                converted_objects_uuid_checked.append(converted_object_uuid_checked)

        elif values_in_mo.count(converted_object_value) == 0:
            converted_objects_uuid_checked.append(converted_object)
        else:
            logger.warning(
                f"Could not determine which '{json_key}' MO object "
                f"{value_key}='{converted_object_value}' belongs to. Skipping"
            )

    return converted_objects_uuid_checked


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)
    settings = Settings(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    login_manager = LoginManager(
        settings.authentication_secret.get_secret_value(),
        "/login",
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

    context = fastramqpi._context
    user_context = context["user_context"]
    converter = user_context["converter"]
    dataloader = user_context["dataloader"]
    ldap_connection = user_context["ldap_connection"]
    internal_amqpsystem = user_context["internal_amqpsystem"]

    attribute_types = get_attribute_types(ldap_connection)
    accepted_attributes = tuple(sorted(attribute_types.keys()))

    ldap_classes = tuple(sorted(converter.overview.keys()))
    default_ldap_class = converter.raw_mapping["mo_to_ldap"]["Employee"]["objectClass"]

    accepted_json_keys = tuple(converter.get_accepted_json_keys())
    detected_json_keys = converter.get_ldap_to_mo_json_keys()

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
    @app.get("/Import/all", status_code=202, tags=["Import"])
    async def import_all_objects_from_LDAP(
        test_on_first_20_entries: bool = False, user=Depends(login_manager)
    ) -> Any:
        all_ldap_objects = await dataloader.load_ldap_objects("Employee")
        all_cpr_numbers = [o.dict()[converter.cpr_field] for o in all_ldap_objects]
        all_cpr_numbers = sorted(list(set([a for a in all_cpr_numbers if a])))

        if test_on_first_20_entries:
            # Only upload the first 20 entries
            logger.info("Slicing the first 20 entries")
            all_cpr_numbers = all_cpr_numbers[:20]

        number_of_entries = len(all_cpr_numbers)
        logger.info(f"Found {number_of_entries} cpr-indexed entries in AD")

        with tqdm(total=number_of_entries, unit="ldap object") as progress_bar:
            progress_bar.set_description("LDAP import progress")

            # Note: This can be done in a more parallel way using asyncio.gather() but:
            # - it was experienced that fastapi throws broken pipe errors
            # - MO was observed to not handle that well either.
            # - We don't need the additional speed. This is meant as a one-time import
            for cpr in all_cpr_numbers:
                await import_single_user_from_LDAP(cpr)
                progress_bar.update()

    # Load a single user from LDAP, and import him/her/hir into MO
    @app.get("/Import/{cpr}", status_code=202, tags=["Import"])
    async def import_single_user_from_LDAP(
        cpr: str, user=Depends(login_manager)
    ) -> Any:
        global uuids_to_ignore
        # Get the employee's uuid (if he exists)
        # Note: We could optimize this by loading all relevant employees once. But:
        # - What if an employee is created by someone else while this code is running?
        # - We don't need the additional speed. This is meant as a one-time import
        # - We won't gain much; This is an asynchronous request. The code moves on while
        #   we are waiting for MO's response
        employee_uuid = await dataloader.find_mo_employee_uuid(cpr)
        if not employee_uuid:
            employee_uuid = uuid4()

        # First import the Employee
        # Then import other objects (which link to the employee)
        json_keys = ["Employee"] + [k for k in detected_json_keys if k != "Employee"]

        for json_key in json_keys:
            if not converter.__import_to_mo__(json_key):
                logger.info(f"__import_to_mo__ == False for json_key = '{json_key}'")
                continue
            logger.info(f"Loading {json_key} object")
            try:
                loaded_object = dataloader.load_ldap_cpr_object(cpr, json_key)
            except MultipleObjectsReturnedException as e:
                logger.warning(f"Could not upload {json_key} object: {e}")
                break

            logger.info(f"Loaded {loaded_object.dn}")

            converted_objects = converter.from_ldap(
                loaded_object, json_key, employee_uuid=employee_uuid
            )

            if len(converted_objects) == 0:
                logger.info("No converted objects")
                continue

            converted_objects = await format_converted_objects(
                converted_objects, json_key, user_context
            )

            if len(converted_objects) > 0:
                logger.info(f"Importing {converted_objects}")

                for mo_object in converted_objects:
                    if mo_object.uuid in uuids_to_ignore:
                        uuids_to_ignore[mo_object.uuid].append(datetime.datetime.now())
                    else:
                        uuids_to_ignore[mo_object.uuid] = [datetime.datetime.now()]
                await dataloader.upload_mo_objects(converted_objects)

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
        ):
            self.publish_amqp_messages = publish_amqp_messages
            self.object_uuid = object_uuid

    # Export object(s) from MO to LDAP
    @app.post("/Export", status_code=202, tags=["Export"])
    async def export_mo_objects(
        user=Depends(login_manager),
        params: ExportQueryParams = Depends(),
    ) -> Any:

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
        cpr: str,
        user=Depends(login_manager),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str,
        response: Response,
        user=Depends(login_manager),
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
        result = await dataloader.load_ldap_objects(json_key)
        return encode_result(result[-entries_to_return:])

    # Modify a person in LDAP
    @app.post("/LDAP/{json_key}", tags=["LDAP"])
    async def post_object_to_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        ldap_object: LdapObject,
        user=Depends(login_manager),
    ) -> Any:
        await dataloader.upload_ldap_object(ldap_object, json_key)

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
    @app.get("/LDAP_overview", status_code=202, tags=["LDAP"])
    async def load_overview_from_LDAP(
        user=Depends(login_manager),
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_overview()
        return ldap_overview[ldap_class]

    # Get populated LDAP overview
    @app.get("/LDAP_overview/populated", status_code=202, tags=["LDAP"])
    async def load_populated_overview_from_LDAP(
        user=Depends(login_manager),
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_populated_overview(
            ldap_classes=[ldap_class]
        )
        return encode_result(ldap_overview.get(ldap_class))

    # Get LDAP attribute details
    @app.get("/LDAP_overview/attribute/{attribute}", status_code=202, tags=["LDAP"])
    async def load_attribute_details_from_LDAP(
        attribute: Literal[accepted_attributes],  # type: ignore
        user=Depends(login_manager),
    ) -> Any:
        return attribute_types[attribute]

    # Get LDAP object
    @app.get("/LDAP_overview/object/{dn}", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap(
        dn: str, user=Depends(login_manager), nest: bool = False
    ) -> Any:
        return dataloader.load_ldap_object(dn, ["*"], nest=nest)

    # Get MO address types
    @app.get("/MO/Address_types", status_code=202, tags=["MO"])
    async def load_address_types_from_MO(user=Depends(login_manager)) -> Any:
        result = dataloader.load_mo_address_types()
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
        date: str = datetime.datetime.today().strftime("%Y-%m-%d"),
        params: SyncQueryParams = Depends(),
    ) -> Any:

        # Load all objects
        all_objects = await dataloader.load_all_mo_objects(add_validity=True)

        # Filter out all that is not from/to today and determine request type
        # Note: It is not possible in graphql (yet?) To load just today's objects
        todays_objects = []
        for mo_object in all_objects:
            from_date = str(mo_object["validity"]["from"])
            to_date = str(mo_object["validity"]["to"])
            if from_date.startswith(date):
                if to_date.startswith(date):
                    mo_object["request_type"] = RequestType.TERMINATE
                else:
                    mo_object["request_type"] = RequestType.REFRESH
                todays_objects.append(mo_object)
            elif to_date.startswith(date):
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
            if params.publish_amqp_messages:
                await internal_amqpsystem.publish_message(
                    str(routing_key), jsonable_encoder(payload)
                )

    return app
