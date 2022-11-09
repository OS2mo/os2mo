# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from typing import Tuple

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastramqpi.main import FastRAMQPI
from ldap3 import Connection
from raclients.graph.client import PersistentGraphQLClient
from raclients.modelclient.mo import ModelClient
from ramodels.mo.employee import Employee
from ramqp.mo import MORouter
from ramqp.mo.models import PayloadType

from .config import Settings
from .converters import EmployeeConverter
from .dataloaders import configure_dataloaders
from .dataloaders import LdapEmployee
from .ldap import configure_ldap_connection
from .ldap import ldap_healthcheck

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


@amqp_router.register("employee.employee.*")
async def listen_to_changes_in_employees(
    context: dict, payload: PayloadType, **kwargs: Any
) -> None:
    logger.info("[MO] Change registered in the employee model")
    logger.info("Payload: %s" % payload)

    user_context = context["user_context"]

    changed_employee: Employee = await user_context[
        "dataloaders"
    ].mo_employee_loader.load(payload.uuid)

    logger.info("Found Employee in MO: %s" % changed_employee)

    logger.info("Converting MO Employee object to AD object")
    # ldap_employee: LdapEmployee = convert_employee_from_mo_to_ldap(changed_employee)

    cn = "CN=%s," % (changed_employee.givenname + " " + changed_employee.surname)
    ou = "OU=Users,%s," % user_context["app_settings"].ldap_organizational_unit
    dc = user_context["app_settings"].ldap_search_base
    dn = cn + ou + dc
    ldap_employee = LdapEmployee(
        dn=dn, Name=changed_employee.givenname, Department=changed_employee.org
    )

    logger.info("Uploading %s to AD" % ldap_employee)
    await user_context["dataloaders"].ldap_employees_uploader.load(ldap_employee)


@asynccontextmanager
async def open_ldap_connection(ldap_connection: Connection) -> AsyncIterator[None]:
    """Open the AD connection during FastRAMQPI lifespan.

    Yields:
        None
    """
    with ldap_connection:
        yield


@asynccontextmanager
async def seed_dataloaders(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    """Seed dataloaders during FastRAMQPI lifespan.

    Yields:
        None
    """
    logger.info("Seeding dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)
    yield


def construct_gql_client(settings: Settings):
    return PersistentGraphQLClient(
        url=settings.mo_url + "/graphql/v2",
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
) -> Tuple[PersistentGraphQLClient, ModelClient]:
    """Construct clients froms settings.

    Args:
        settings: Integration settings module.

    Returns:
        Tuple with PersistentGraphQLClient and ModelClient.
    """
    gql_client = construct_gql_client(settings)
    model_client = construct_model_client(settings)
    return gql_client, model_client


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
    gql_client, model_client = construct_clients(settings)

    fastramqpi.add_context(model_client=model_client)
    fastramqpi.add_context(gql_client=gql_client)

    logger.info("Configuring AD connection")
    ldap_connection = configure_ldap_connection(settings)
    fastramqpi.add_context(ldap_connection=ldap_connection)
    fastramqpi.add_healthcheck(name="ADConnection", healthcheck=ldap_healthcheck)
    fastramqpi.add_lifespan_manager(open_ldap_connection(ldap_connection), 1500)

    fastramqpi.add_lifespan_manager(seed_dataloaders(fastramqpi), 2000)

    logger.info("Configuring Dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)

    fastramqpi.add_context(app_settings=settings)

    return fastramqpi


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    mappings_folder = os.path.join(os.path.dirname(__file__), "mappings")

    @app.get("/AD/employee/converted", status_code=202)
    async def convert_all_org_persons_from_ldap() -> Any:
        """Request all organizational persons, converted to MO"""
        logger.info("Manually triggered LDAP request of all organizational persons")
        converter = EmployeeConverter(os.path.join(mappings_folder, "default.json"))
        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].ldap_employees_loader.load(1)
        result = [converter.from_ldap(r) for r in result]
        return result

    # Get a specific person from AD
    @app.get("/AD/employee/{dn}", status_code=202)
    async def load_employee_from_LDAP(dn: str, request: Request) -> Any:
        """Request single employee"""
        logger.info("Manually triggered AD request of %s" % dn)

        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].ldap_employee_loader.load(dn)
        return result

    # Get all persons from AD
    @app.get("/AD/employee", status_code=202)
    async def load_all_employees_from_LDAP() -> Any:
        """Request all employees"""
        logger.info("Manually triggered AD request of all employees")

        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].ldap_employees_loader.load(1)
        return result

    # Modify a person in AD
    @app.post("/AD/employee")
    async def post_employee_to_LDAP(employee: LdapEmployee) -> Any:
        logger.info("Posting %s to AD" % employee)

        await fastramqpi._context["user_context"][
            "dataloaders"
        ].ldap_employees_uploader.load(employee)

    # Get all persons from MO
    @app.get("/MO/employee", status_code=202)
    async def load_all_employees_from_MO() -> Any:
        """Request all persons from MO"""
        logger.info("Manually triggered MO request of all employees")

        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].mo_employees_loader.load(1)
        return result

    # Post a person to MO
    @app.post("/MO/employee")
    async def post_employee_to_MO(employee: Employee) -> Any:
        logger.info("Posting %s to MO" % employee)

        await fastramqpi._context["user_context"][
            "dataloaders"
        ].mo_employee_uploader.load(employee)

    # Get a speficic person from MO
    @app.get("/MO/employee/{uuid}", status_code=202)
    async def load_employee_from_MO(uuid: str, request: Request) -> Any:
        """Request single employee"""
        logger.info("Manually triggered MO request of %s" % uuid)

        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].mo_employee_loader.load(uuid)
        return result

    return app
