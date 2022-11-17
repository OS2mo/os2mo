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
from more_itertools import always_iterable
from more_itertools import flatten
from more_itertools import only
from pydantic import BaseModel
from raclients.modelclient.mo import ModelClient
from ramodels.mo.employee import Employee
from strawberry.dataloader import DataLoader

from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .ldap_classes import LdapEmployee


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


def get_ldap_attributes(ldap_connection, ad_object: Union[str, None]):
    """
    ldap_connection : ldap connection object
    ad_object : ad_object to fetch attributes for. for example "organizationalPerson"
    """

    logger = structlog.get_logger()
    all_attributes = []
    while ad_object is not None:
        schema = ldap_connection.server.schema.object_classes[ad_object]
        if ad_object != "top":
            logger.info("Fetching allowed objects for %s" % ad_object)
            all_attributes += schema.may_contain
        ad_object = only(always_iterable(schema.superior))
    return all_attributes


def make_ldap_object(
    response: dict, object_class: Any, attributes: list, context: Context
) -> Any:
    """
    Takes an ldap response and formats it as a class
    """

    ldap_dict = {"dn": response["dn"]}

    if object_class.__name__ == "LdapEmployee":
        # The employee class must contain a cpr number field
        cpr_field = context["user_context"]["cpr_field"]
        cpr_number = response["attributes"][cpr_field]

        # TODO: Add a cpr number check here?
        ldap_dict["cpr"] = str(cpr_number)

    for attribute in attributes:
        value = response["attributes"][attribute]
        if (value == []) or (type(value) is bytes):
            ldap_dict[attribute] = None
        else:
            ldap_dict[attribute] = value

    return object_class(**ldap_dict)


async def load_ldap_employee(keys: list[str], context: Context) -> list[LdapEmployee]:

    logger = structlog.get_logger()
    user_context = context["user_context"]
    search_base = user_context["settings"].ldap_search_base
    ldap_connection = user_context["ldap_connection"]
    output = []
    attributes = get_ldap_attributes(ldap_connection, "organizationalPerson")

    for cpr in keys:
        searchParameters = {
            "search_base": search_base,
            "search_filter": "(&(objectclass=organizationalPerson)(%s=%s))"
            % (user_context["cpr_field"], cpr),
            "attributes": attributes,
        }

        ldap_connection.search(**searchParameters)
        response = ldap_connection.response

        search_entries = [r for r in response if r["type"] == "searchResEntry"]

        if len(search_entries) > 1:
            logger.info(response)
            raise MultipleObjectsReturnedException(
                "Found multiple entries for cpr=%s" % cpr
            )
        elif len(search_entries) == 0:
            raise NoObjectsReturnedException("Found no entries for cpr=%s" % cpr)

        employee: LdapEmployee = make_ldap_object(
            search_entries[0], LdapEmployee, attributes, context
        )

        logger.info("Found %s" % employee)
        output.append(employee)

    return output


async def load_ldap_employees(key: int, context: Context) -> list[list[LdapEmployee]]:
    """
    Returns list with all organizationalPersons
    """
    logger = structlog.get_logger()
    user_context = context["user_context"]
    search_base = user_context["settings"].ldap_search_base
    ldap_connection = user_context["ldap_connection"]

    responses = []
    attributes = get_ldap_attributes(ldap_connection, "organizationalPerson")

    searchParameters = {
        "search_base": search_base,
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": attributes,
        "paged_size": 500,  # TODO: Find this number from LDAP rather than hard-code it?
    }

    # Max 10_000 pages to avoid eternal loops
    for page in range(0, 10_000):
        logger.info("searching page %d" % page)
        ldap_connection.search(**searchParameters)
        entries = [r for r in ldap_connection.response if r["type"] == "searchResEntry"]
        responses.extend(entries)

        # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
        cookie = ldap_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    output: list[LdapEmployee] = [
        make_ldap_object(r, LdapEmployee, attributes, context) for r in responses
    ]

    return [output]


async def upload_ldap_employee(
    keys: list[LdapEmployee],
    context: Context,
):
    logger = structlog.get_logger()
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]

    all_attributes = get_ldap_attributes(ldap_connection, "organizationalPerson")
    output = []
    success = 0
    failed = 0
    cpr_field = user_context["cpr_field"]
    for key in keys:

        try:
            existing_employee = await load_ldap_employee(
                [key.cpr],
                context=context,
            )
            dn = existing_employee[0].dn
            logger.info("Found existing employee: %s" % dn)
        except NoObjectsReturnedException as e:
            logger.info("Could not find existing employee: %s" % e)

            # Note: it is possible that the employee exists, but that the CPR no.
            # attribute is not set. In that case this function will just set the cpr no.
            # attribute in LDAP.
            dn = key.dn

        parameters_to_upload = list(key.dict().keys())
        parameters_to_upload = [
            p for p in parameters_to_upload if p != "dn" and p in all_attributes
        ]
        results = []
        parameters = key.dict()

        # Add cpr field
        if cpr_field not in parameters_to_upload:
            parameters_to_upload = parameters_to_upload + [cpr_field]
        parameters[cpr_field] = key.cpr

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

    ldap_loader_functions: dict[str, Callable] = {
        "ldap_employees_loader": load_ldap_employees,
        "ldap_employee_loader": load_ldap_employee,
        "ldap_employees_uploader": upload_ldap_employee,
    }

    ldap_dataloaders: dict[str, DataLoader] = {
        key: DataLoader(
            load_fn=partial(
                value,
                # ldap_connection=ldap_connection,
                # search_base=settings.ldap_search_base,
                context=context,
            ),
            cache=False,
        )
        for key, value in ldap_loader_functions.items()
    }

    return Dataloaders(
        **graphql_dataloaders,
        **ldap_dataloaders,
        mo_employee_uploader=mo_employee_uploader,
    )
