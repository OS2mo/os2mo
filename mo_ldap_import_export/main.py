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
from ramqp.mo import MORouter
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import RequestType
from ramqp.utils import RejectMessage

from .config import Settings
from .converters import LdapConverter
from .converters import read_mapping_json
from .dataloaders import DataLoader
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


def reject_on_failure(func):
    """
    Decorator to turn message into dead letter in case of exceptions.
    """

    async def modified_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except:  # noqa
            raise RejectMessage()

    return modified_func


@amqp_router.register("employee.*.*")
@reject_on_failure
async def listen_to_changes_in_employees(
    context: Context, payload: PayloadType, **kwargs: Any
) -> None:

    routing_key = kwargs["mo_routing_key"]
    logger.info("[MO] Registered change in the employee model")
    logger.info(f"[MO] Routing key: {routing_key}")
    logger.info(f"Payload: {payload}")

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

        # Get all addresses for this user in LDAP (note that LDAP can contain multiple
        # addresses in one object.)
        loaded_ldap_address = await dataloader.load_ldap_cpr_object(
            changed_employee.cpr_no, json_key
        )

        # Convert to MO so the two are easy to compare
        addresses_in_ldap = converter.from_ldap(loaded_ldap_address, json_key)

        # Get all CURRENT addresses of this type for this user from MO
        addresses_in_mo = await dataloader.load_mo_employee_addresses(
            changed_employee.uuid, changed_address.address_type.uuid
        )

        # Format as lists
        address_values_in_ldap = sorted([a.value for a in addresses_in_ldap])
        address_values_in_mo = sorted([a[0].value for a in addresses_in_mo])

        logger.info(f"Found the following addresses in LDAP: {address_values_in_ldap}")
        logger.info(f"Found the following addresses in MO: {address_values_in_mo}")
        if address_values_in_ldap == address_values_in_mo:
            logger.info("No synchronization required")

        # Clean from LDAP as needed
        ldap_addresses_to_clean = []
        for address in addresses_in_ldap:
            if address.value not in address_values_in_mo:
                ldap_addresses_to_clean.append(
                    converter.to_ldap(
                        {
                            "mo_employee": changed_employee,
                            "mo_address": address,
                        },
                        json_key,
                        dn=loaded_ldap_address.dn,
                    )
                )
        dataloader.cleanup_attributes_in_ldap(ldap_addresses_to_clean)


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
    mappings_folder = os.path.join(os.path.dirname(__file__), "mappings")
    mappings_file = os.path.join(mappings_folder, "default.json")
    fastramqpi.add_context(mapping=read_mapping_json(mappings_file))

    logger.info("Initializing dataloader")
    context = fastramqpi.get_context()
    dataloader = DataLoader(context)
    fastramqpi.add_context(dataloader=dataloader)

    logger.info("Initializing converters")
    context = fastramqpi.get_context()
    converter = LdapConverter(context)
    fastramqpi.add_context(cpr_field=converter.cpr_field)
    fastramqpi.add_context(converter=converter)

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

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    context = fastramqpi._context
    user_context = context["user_context"]
    converter = user_context["converter"]
    dataloader = user_context["dataloader"]

    accepted_json_keys = tuple(converter.get_accepted_json_keys())

    # Get all objects from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/converted", status_code=202, tags=["LDAP"])
    async def convert_all_org_persons_from_ldap(
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
        request: Request,
    ) -> Any:

        result = await dataloader.load_ldap_cpr_object(cpr, json_key)
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @app.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str,
        request: Request,
        response: Response,
    ) -> Any:

        result = await dataloader.load_ldap_cpr_object(cpr, json_key)
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

    return app
