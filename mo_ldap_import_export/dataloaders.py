# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""
from functools import partial
from typing import Any
from typing import Callable
from typing import cast
from typing import Union

import structlog
from fastramqpi.context import Context
from gql import gql
from gql.client import AsyncClientSession
from ldap3 import Connection
from more_itertools import flatten
from pydantic import BaseModel
from raclients.modelclient.mo import ModelClient
from ramodels.mo.employee import Employee
from strawberry.dataloader import DataLoader

from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException


class Dataloaders(BaseModel):
    """Collection of program dataloaders."""

    class Config:
        """Arbitrary types need to be allowed to have DataLoader members."""

        arbitrary_types_allowed = True

    ldap_employees_loader: DataLoader
    ldap_employee_loader: DataLoader
    ldap_employees_uploader: DataLoader
    mo_employees_loader: DataLoader
    mo_employee_uploader: DataLoader
    mo_employee_loader: DataLoader


# TODO: move this placeholder class to its own file and extend properties
class LdapEmployee(BaseModel):
    """Model for an AD employee"""

    dn: str
    Name: str  # TODO: This field cannot be modified in AD. Add a 'protected' flag?
    Department: Union[str, None]
    objectGUID: Union[str, None]
    givenName: Union[str, None]
    sn: Union[str, None]


def get_ldap_attributes() -> list[str]:
    return [a for a in LdapEmployee.schema()["properties"].keys() if a != "dn"]


async def load_ldap_employee(
    keys: list[str], ldap_connection: Connection
) -> list[LdapEmployee]:

    logger = structlog.get_logger()
    output = []

    for dn in keys:
        searchParameters = {
            "search_base": dn,
            "search_filter": "(objectclass=organizationalPerson)",
            "attributes": get_ldap_attributes(),
        }

        ldap_connection.search(**searchParameters)
        response = ldap_connection.response

        if len(response) > 1:
            raise MultipleObjectsReturnedException(
                "Found multiple entries for dn=%s" % dn
            )
        elif len(response) == 0:
            raise NoObjectsReturnedException("Found no entries for dn=%s" % dn)

        for attribute, value in response[0]["attributes"].items():
            if value == []:
                response[0]["attributes"][attribute] = None

        employee = LdapEmployee(
            dn=response[0]["dn"],
            Name=response[0]["attributes"]["name"],
            Department=response[0]["attributes"]["department"],
        )

        logger.info("Found %s" % employee)
        output.append(employee)

    return output


async def load_ldap_employees(
    key: int,
    ldap_connection: Connection,
    search_base: str,
) -> list[list[LdapEmployee]]:
    """
    Returns list with all organizationalPersons
    """
    logger = structlog.get_logger()
    output = []

    searchParameters = {
        "search_base": search_base,
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": get_ldap_attributes(),
        "paged_size": 500,  # TODO: Find this number from AD rather than hard-code it?
    }

    # Max 10_000 pages to avoid eternal loops
    for page in range(0, 10_000):
        logger.info("searching page %d" % page)
        ldap_connection.search(**searchParameters)
        output.extend(ldap_connection.entries)

        # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
        cookie = ldap_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    output_list = [
        LdapEmployee(
            dn=o.entry_dn,
            Name=o.Name.value,
            Department=o.Department.value,
        )
        for o in output
    ]

    return [output_list]


async def upload_ldap_employee(keys: list[LdapEmployee], ldap_connection: Connection):
    logger = structlog.get_logger()
    output = []
    success = 0
    failed = 0
    for key in keys:
        dn = key.dn
        parameters_to_upload = [k for k in key.dict().keys() if k != "dn"]
        results = []
        parameters = key.dict()
        for parameter_to_upload in parameters_to_upload:
            value = parameters[parameter_to_upload]
            value_to_upload = [] if value is None else [value]
            changes = {parameter_to_upload: [("MODIFY_REPLACE", value_to_upload)]}

            logger.info("Uploading the following changes: %s" % changes)
            ldap_connection.modify(dn, changes)
            response = ldap_connection.result

            # If the user does not exist, create him/her/hir
            if response["description"] == "noSuchObject":
                logger.info("Creating %s" % dn)
                ldap_connection.add(dn, "organizationalPerson")
                ldap_connection.modify(dn, changes)
                response = ldap_connection.result

            if response["description"] == "success":
                success += 1
            else:
                failed += 1
            logger.info("Response: %s" % response)

            results.append(response)

        output.append(results)

    logger.info("Succeeded MODIFY_REPLACE operations: %d" % success)
    logger.info("Failed MODIFY_REPLACE operations: %d" % failed)
    return output


def get_mo_employee_objects_str():
    """
    Returns object-names-of-interest for the MO employee object
    """
    objects = [
        "uuid",
        "cpr_no",
        "givenname",
        "surname",
        "nickname_givenname",
        "nickname_surname",
    ]
    objects_str = ", ".join(objects)
    return objects_str


def format_employee_output(result):
    output = []
    for entry in list(flatten([r["objects"] for r in result["employees"]])):
        output.append(Employee(**entry))
    return output


async def load_mo_employees(
    key: int, graphql_session: AsyncClientSession
) -> list[list[Employee]]:

    query = gql(
        """
        query AllEmployees {
          employees {
            objects {
              %s
            }
          }
        }
        """
        % get_mo_employee_objects_str()
    )

    result = await graphql_session.execute(query)

    # Note: Output is a list of list; The dataloader expects a single object as output
    return [format_employee_output(result)]


async def load_mo_employee(
    keys: list[str], graphql_session: AsyncClientSession
) -> list[Employee]:
    output = []
    for uuid in keys:
        query = gql(
            """
            query SinlgeEmployee {
              employees(uuids:"{%s}") {
                objects {
                  %s
                }
              }
            }
            """
            % (uuid, get_mo_employee_objects_str())
        )

        result = await graphql_session.execute(query)
        output.extend(format_employee_output(result))

    return output


async def upload_mo_employee(
    keys: list[Employee],
    model_client: ModelClient,
):
    # return await model_client.upload(keys)
    return cast(list[Any | None], await model_client.upload(keys))


def configure_dataloaders(context: Context) -> Dataloaders:
    """Construct our dataloaders from the FastRAMQPI context.

    Args:
        context: The FastRAMQPI context to configure our dataloaders with.

    Returns:
        Dataloaders required
    """

    graphql_loader_functions: dict[str, Callable] = {
        "mo_employees_loader": load_mo_employees,
        "mo_employee_loader": load_mo_employee,
    }

    user_context = context["user_context"]
    graphql_session = user_context["gql_client"]
    graphql_dataloaders: dict[str, DataLoader] = {
        key: DataLoader(
            load_fn=partial(value, graphql_session=graphql_session), cache=False
        )
        for key, value in graphql_loader_functions.items()
    }

    model_client = user_context["model_client"]
    mo_employee_uploader = DataLoader(
        load_fn=partial(upload_mo_employee, model_client=model_client),
        cache=False,
    )

    settings = user_context["settings"]
    ldap_connection = user_context["ldap_connection"]
    ldap_employees_loader = DataLoader(
        load_fn=partial(
            load_ldap_employees,
            ldap_connection=ldap_connection,
            search_base=settings.ldap_search_base,
        ),
        cache=False,
    )

    ldap_employee_loader = DataLoader(
        load_fn=partial(load_ldap_employee, ldap_connection=ldap_connection),
        cache=False,
    )

    ldap_employees_uploader = DataLoader(
        load_fn=partial(upload_ldap_employee, ldap_connection=ldap_connection),
        cache=False,
    )

    return Dataloaders(
        **graphql_dataloaders,
        ldap_employees_loader=ldap_employees_loader,
        ldap_employee_loader=ldap_employee_loader,
        ldap_employees_uploader=ldap_employees_uploader,
        mo_employee_uploader=mo_employee_uploader,
    )
