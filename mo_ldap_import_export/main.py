# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from typing import Literal
from typing import Tuple
from uuid import UUID
from uuid import uuid4

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastramqpi.context import Context
from fastramqpi.main import FastRAMQPI
from ldap3 import Connection
from pydantic import ValidationError
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramodels.mo.details.address import Address
from ramqp.mo import MORouter
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import RequestType
from ramqp.utils import RejectMessage
from tqdm import tqdm

from . import usernames
from .config import Settings
from .converters import LdapConverter
from .converters import read_mapping_json
from .dataloaders import DataLoader
from .exceptions import IncorrectMapping
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NotSupportedException
from .ldap import configure_ldap_connection
from .ldap import ldap_healthcheck
from .ldap_classes import LdapObject

logger = structlog.get_logger()
fastapi_router = APIRouter()
amqp_router = MORouter()

"""
Employee.schema()
help(MORouter)
help(ServiceType)
help(ObjectType)
help(RequestType)
"""

# UUIDs in this list will be ignored by listen_to_changes ONCE
uuids_to_ignore: list[UUID] = []


def reject_on_failure(func):
    """
    Decorator to turn message into dead letter in case of exceptions.
    """

    async def modified_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except (NotSupportedException, IncorrectMapping):
            raise RejectMessage()

    modified_func.__wrapped__ = func  # type: ignore
    return modified_func


@amqp_router.register("employee.*.*")
@reject_on_failure
async def listen_to_changes_in_employees(
    context: Context, payload: PayloadType, **kwargs: Any
) -> None:

    global uuids_to_ignore

    # If the object was uploaded by us, it does not need to be synchronized.
    if payload.object_uuid in uuids_to_ignore:
        logger.info(f"[listen_to_changes] Ignoring {payload.object_uuid}")

        # Remove uuid so it does not get ignored twice.
        uuids_to_ignore.remove(payload.object_uuid)
        return None

    # If we are not supposed to listen: reject and turn the message into a dead letter.
    elif not Settings().listen_to_changes_in_mo:
        raise RejectMessage()

    routing_key = kwargs["mo_routing_key"]
    logger.info("[MO] Registered change in the employee model")
    logger.info(f"[MO] Routing key: {routing_key}")
    logger.info(f"[MO] Payload: {payload}")

    # TODO: Add support for deleting users / fields from LDAP
    if routing_key.request_type == RequestType.TERMINATE:
        # Note: Deleting an object is not straightforward, because MO specifies a future
        # date, on which the object is to be deleted. We would need a job which runs
        # daily and checks for users/addresses/etc... that need to be deleted
        raise NotSupportedException("Terminations are not supported")

    user_context = context["user_context"]
    dataloader = user_context["dataloader"]
    converter = user_context["converter"]

    # Get MO employee
    changed_employee = await dataloader.load_mo_employee(payload.uuid)
    logger.info(f"Found Employee in MO: {changed_employee}")

    def cleanup(
        json_key: str, value_key: str, mo_dict_key: str, mo_objects_in_mo: list[Any]
    ):
        # Get all matching objects for this user in LDAP (note that LDAP can contain
        # multiple entries in one object.)
        loaded_ldap_object = dataloader.load_ldap_cpr_object(
            changed_employee.cpr_no, json_key
        )

        # Convert to MO so the two are easy to compare
        mo_objects_in_ldap = converter.from_ldap(loaded_ldap_object, json_key)

        # Format as lists
        values_in_ldap = sorted([getattr(a, value_key) for a in mo_objects_in_ldap])
        values_in_mo = sorted([getattr(a, value_key) for a in mo_objects_in_mo])

        logger.info(f"Found following '{json_key}' values in LDAP: {values_in_ldap}")
        logger.info(f"Found following '{json_key}' values in MO: {values_in_mo}")

        # Clean from LDAP as needed
        ldap_objects_to_clean = []
        for mo_object in mo_objects_in_ldap:
            if getattr(mo_object, value_key) not in values_in_mo:
                ldap_objects_to_clean.append(
                    converter.to_ldap(
                        {
                            "mo_employee": changed_employee,
                            mo_dict_key: mo_object,
                        },
                        json_key,
                        dn=loaded_ldap_object.dn,
                    )
                )

        if len(ldap_objects_to_clean) == 0:
            logger.info("No synchronization required")
        else:
            dataloader.cleanup_attributes_in_ldap(ldap_objects_to_clean)

    mo_object_dict: dict[str, Any] = {"mo_employee": changed_employee}

    if routing_key.object_type == ObjectType.EMPLOYEE:
        logger.info("[MO] Change registered in the employee object type")

        # Convert to LDAP
        ldap_employee = converter.to_ldap(mo_object_dict, "Employee")

        # Upload to LDAP - overwrite because all employee fields are unique.
        # One person cannot have multiple names.
        await dataloader.upload_ldap_object(ldap_employee, "Employee", overwrite=True)

    elif routing_key.object_type == ObjectType.ADDRESS:
        logger.info("[MO] Change registered in the address object type")

        # Get MO address
        changed_address, meta_info = await dataloader.load_mo_address(
            payload.object_uuid
        )
        address_type = json_key = meta_info["address_type_name"]

        logger.info(f"Obtained address type = {address_type}")

        # Convert to LDAP
        mo_object_dict["mo_address"] = changed_address

        # Upload to LDAP
        await dataloader.upload_ldap_object(
            converter.to_ldap(mo_object_dict, json_key), json_key
        )

        addresses_in_mo = await dataloader.load_mo_employee_addresses(
            changed_employee.uuid, changed_address.address_type.uuid
        )

        cleanup(json_key, "value", "mo_address", [a[0] for a in addresses_in_mo])

    elif routing_key.object_type == ObjectType.IT:
        logger.info("[MO] Change registered in the IT object type")

        # Get MO IT-user
        changed_it_user = await dataloader.load_mo_it_user(payload.object_uuid)
        it_system_type_uuid = changed_it_user.itsystem.uuid
        it_system_type = converter.get_it_system(it_system_type_uuid)

        it_system_name = json_key = it_system_type["name"]

        logger.info(f"Obtained IT system name = {it_system_name}")

        # Convert to LDAP
        mo_object_dict["mo_it_user"] = changed_it_user

        # Upload to LDAP
        await dataloader.upload_ldap_object(
            converter.to_ldap(mo_object_dict, json_key), json_key
        )

        # Load IT users belonging to this employee
        it_users_in_mo = await dataloader.load_mo_employee_it_users(
            changed_employee.uuid, it_system_type_uuid
        )

        cleanup(json_key, "user_key", "mo_it_user", it_users_in_mo)


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

    return fastramqpi


def encode_result(result):
    # This removes all bytes objects from the result. for example images
    json_compatible_result = jsonable_encoder(
        result, custom_encoder={bytes: lambda v: None}
    )
    return json_compatible_result


def get_matching_address_uuid(
    lookup_value: str, addresses_in_mo_dict: dict[UUID, Address]
):
    """
    Returns the address uuid belonging to an address value.

    Parameters
    ---------------
    lookup_value: str
        Address value to look for
    address_values_in_mo: dict
        Dictionary where keys are MO address UUIDs and values are the values belonging
        to the addresses

    Notes
    ------
    If multiple addresses match this value, returns the first match.
    """
    for uuid, address in addresses_in_mo_dict.items():
        value = address.value
        if value == lookup_value:
            return uuid


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    context = fastramqpi._context
    user_context = context["user_context"]
    converter = user_context["converter"]
    dataloader = user_context["dataloader"]

    accepted_json_keys = tuple(converter.get_accepted_json_keys())
    detected_json_keys = converter.get_ldap_to_mo_json_keys()

    # Load all users from LDAP, and import them into MO
    @app.get("/Import/all", status_code=202, tags=["Import"])
    async def import_all_objects_from_LDAP(
        test_on_first_20_entries: bool = False,
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
    async def import_single_user_from_LDAP(cpr: str) -> Any:
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
                continue

            mo_object_class = converter.find_mo_object_class(json_key).split(".")[-1]
            if mo_object_class == "Address":
                # Load addresses already in MO
                addresses_in_mo = await dataloader.load_mo_employee_addresses(
                    employee_uuid, converted_objects[0].address_type.uuid
                )
                addresses_in_mo_dict = {a[0].uuid: a[0] for a in addresses_in_mo}

                mo_attributes = converter.get_mo_attributes(json_key)

                # Set uuid if a matching one is found. so an address gets updated
                # instead of duplicated
                converted_objects_uuid_checked = []
                for converted_object in converted_objects:
                    values_in_mo = [a.value for a in addresses_in_mo_dict.values()]
                    if converted_object.value in values_in_mo:
                        logger.info(
                            (
                                f"Found matching MO '{json_key}' address with "
                                f"value='{converted_object.value}'"
                            )
                        )
                        matching_address_uuid = get_matching_address_uuid(
                            converted_object.value, addresses_in_mo_dict
                        )
                        matching_address = addresses_in_mo_dict[matching_address_uuid]
                        converted_address_dict = converted_object.dict()

                        address_dict = matching_address.dict()
                        for key in mo_attributes:
                            if (
                                key not in ["validity", "uuid", "objectClass"]
                                and key in converted_address_dict.keys()
                            ):
                                address_dict[key] = converted_address_dict[key]

                        mo_class = converter.import_mo_object_class(json_key)
                        converted_objects_uuid_checked.append(mo_class(**address_dict))
                    else:
                        converted_objects_uuid_checked.append(converted_object)

                converted_objects = converted_objects_uuid_checked

            elif mo_object_class == "ITUser":
                # If an ITUser already exists, MO throws an error
                it_users_in_mo = await dataloader.load_mo_employee_it_users(
                    employee_uuid, converted_objects[0].itsystem.uuid
                )
                user_keys_in_mo = [a.user_key for a in it_users_in_mo]

                converted_objects = [
                    converted_object
                    for converted_object in converted_objects
                    if converted_object.user_key not in user_keys_in_mo
                ]

            logger.info(f"Importing {converted_objects}")

            for mo_object in converted_objects:
                uuids_to_ignore.append(mo_object.uuid)
            await dataloader.upload_mo_objects(converted_objects)

    # Get all objects from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/converted", status_code=202, tags=["LDAP"])
    async def convert_all_objects_from_ldap(
        json_key: Literal[accepted_json_keys],  # type: ignore
    ) -> Any:
        result = await dataloader.load_ldap_objects(json_key)
        converted_results = []
        for r in result:
            try:
                converted_results.extend(converter.from_ldap(r, json_key))
            except ValidationError as e:
                logger.error(f"Cannot convert {r} to MO {json_key}: {e}")
        return converted_results

    # Get a specific cpr-indexed object from LDAP
    @app.get("/LDAP/{json_key}/{cpr}", status_code=202, tags=["LDAP"])
    async def load_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str,
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str,
        response: Response,
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        try:
            return converter.from_ldap(result, json_key)
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
    ) -> Any:
        result = await dataloader.load_ldap_objects(json_key)
        return encode_result(result)

    # Modify a person in LDAP
    @app.post("/LDAP/{json_key}", tags=["LDAP"])
    async def post_object_to_LDAP(
        json_key: Literal[accepted_json_keys], ldap_object: LdapObject  # type: ignore
    ) -> Any:
        await dataloader.upload_ldap_object(ldap_object, json_key)

    # Post an object to MO
    @app.post("/MO/{json_key}", tags=["MO"])
    async def post_object_to_MO(
        json_key: Literal[accepted_json_keys], mo_object_json: dict  # type: ignore
    ) -> None:
        mo_object = converter.import_mo_object_class(json_key)
        logger.info(f"Posting {mo_object} = {mo_object_json} to MO")
        await dataloader.upload_mo_objects([mo_object(**mo_object_json)])

    # Get a speficic address from MO
    @app.get("/MO/Address/{uuid}", status_code=202, tags=["MO"])
    async def load_address_from_MO(uuid: UUID, request: Request) -> Any:
        result = await dataloader.load_mo_address(uuid)
        return result

    # Get a speficic person from MO
    @app.get("/MO/Employee/{uuid}", status_code=202, tags=["MO"])
    async def load_employee_from_MO(uuid: UUID, request: Request) -> Any:
        result = await dataloader.load_mo_employee(uuid)
        return result

    # Get LDAP overview
    @app.get("/LDAP_overview", status_code=202, tags=["LDAP"])
    async def load_overview_from_LDAP() -> Any:
        result = dataloader.load_ldap_overview()
        return result

    # Get populated LDAP overview
    @app.get("/LDAP_overview/populated", status_code=202, tags=["LDAP"])
    async def load_populated_overview_from_LDAP() -> Any:
        result = dataloader.load_ldap_populated_overview()
        return result

    # Get MO address types
    @app.get("/MO/Address_types", status_code=202, tags=["MO"])
    async def load_address_types_from_MO() -> Any:
        result = dataloader.load_mo_address_types()
        return result

    # Get MO IT system types
    @app.get("/MO/IT_systems", status_code=202, tags=["MO"])
    async def load_it_systems_from_MO() -> Any:
        result = dataloader.load_mo_it_systems()
        return result

    return app
