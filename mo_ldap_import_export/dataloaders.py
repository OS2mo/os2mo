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
from more_itertools import flatten
from pydantic import BaseModel
from raclients.modelclient.mo import ModelClient
from ramodels.mo.employee import Employee
from strawberry.dataloader import DataLoader

from .exceptions import CprNoNotFound
from .exceptions import NoObjectsReturnedException
from .ldap import get_ldap_attributes
from .ldap import get_ldap_schema
from .ldap import get_ldap_superiors
from .ldap import make_ldap_object
from .ldap import paged_search
from .ldap import single_object_search
from .ldap_classes import LdapObject


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
    ldap_overview_loader: DataLoader
    ldap_populated_overview_loader: DataLoader


async def load_ldap_employee(keys: list[str], context: Context) -> list[LdapObject]:

    logger = structlog.get_logger()
    user_context = context["user_context"]

    ldap_connection = user_context["ldap_connection"]
    cpr_field = user_context["cpr_field"]
    settings = user_context["settings"]

    search_base = settings.ldap_search_base
    user_class = settings.ldap_user_class

    object_class_filter = f"objectclass={user_class}"
    output = []

    for cpr in keys:
        cpr_filter = f"{cpr_field}={cpr}"

        searchParameters = {
            "search_base": search_base,
            "search_filter": f"(&({object_class_filter})({cpr_filter}))",
            "attributes": ["*"],
        }
        search_result = single_object_search(searchParameters, ldap_connection)

        employee: LdapObject = make_ldap_object(search_result, context)

        logger.info(f"Found {employee.dn}")
        output.append(employee)

    return output


async def load_ldap_employees(key: int, context: Context) -> list[list[LdapObject]]:
    """
    Returns list with all employees
    """

    user_class = context["user_context"]["settings"].ldap_user_class
    searchParameters = {
        "search_filter": f"(objectclass={user_class})",
        "attributes": ["*"],
    }

    responses = paged_search(context, searchParameters)

    output: list[LdapObject]
    output = [make_ldap_object(r, context, nest=False) for r in responses]

    return [output]


async def upload_ldap_employee(
    keys: list[LdapObject],
    context: Context,
):
    logger = structlog.get_logger()
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]
    user_class = user_context["settings"].ldap_user_class

    all_attributes = get_ldap_attributes(ldap_connection, user_class)
    output = []
    success = 0
    failed = 0
    cpr_field = user_context["cpr_field"]
    for key in keys:

        parameters_to_upload = list(key.dict().keys())

        # Check if the cpr field is present
        if cpr_field not in parameters_to_upload:
            raise CprNoNotFound(f"cpr field '{cpr_field}' not found in ldap object")

        try:
            existing_employee = await load_ldap_employee(
                [key.dict()[cpr_field]],
                context=context,
            )
            dn = existing_employee[0].dn
            logger.info(f"Found existing employee: {dn}")
        except NoObjectsReturnedException as e:
            logger.info(f"Could not find existing employee: {e}")

            # Note: it is possible that the employee exists, but that the CPR no.
            # attribute is not set. In that case this function will just set the cpr no.
            # attribute in LDAP.
            dn = key.dn

        parameters_to_upload = [
            p for p in parameters_to_upload if p != "dn" and p in all_attributes
        ]
        results = []
        parameters = key.dict()

        for parameter_to_upload in parameters_to_upload:
            value = parameters[parameter_to_upload]
            value_to_upload = [] if value is None else [value]
            changes = {parameter_to_upload: [("MODIFY_REPLACE", value_to_upload)]}

            logger.info(f"Uploading the following changes: {changes}")
            ldap_connection.modify(dn, changes)
            response = ldap_connection.result

            # If the user does not exist, create him/her/hir
            if response["description"] == "noSuchObject":
                logger.info(f"Creating {dn}")
                ldap_connection.add(dn, user_class)
                ldap_connection.modify(dn, changes)
                response = ldap_connection.result

            if response["description"] == "success":
                success += 1
            else:
                failed += 1
            logger.info(f"Response: {response}")

            results.append(response)

        output.append(results)

    logger.info(f"Succeeded MODIFY_REPLACE operations: {success}")
    logger.info(f"Failed MODIFY_REPLACE operations: {failed}")
    return output


def make_overview_entry(attributes, superiors):
    return {
        "attributes": attributes,
        "superiors": superiors,
    }


async def load_ldap_overview(keys: list[int], context: Context):
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]
    schema = get_ldap_schema(ldap_connection)

    all_object_classes = sorted(list(schema.object_classes.keys()))

    output = {}
    for ldap_class in all_object_classes:
        all_attributes = get_ldap_attributes(ldap_connection, ldap_class)
        superiors = get_ldap_superiors(ldap_connection, ldap_class)
        output[ldap_class] = make_overview_entry(all_attributes, superiors)

    return [output]


async def load_ldap_populated_overview(keys: list[int], context: Context):
    """
    Like load_ldap_overview but only returns fields which actually contain data
    """
    nan_values: list[Union[None, list]] = [None, []]

    output = {}
    overview = (await load_ldap_overview([1], context))[0]

    for ldap_class in overview.keys():
        searchParameters = {
            "search_filter": f"(objectclass={ldap_class})",
            "attributes": overview[ldap_class]["attributes"],
        }

        responses = paged_search(context, searchParameters)

        populated_attributes = []
        for attribute in overview[ldap_class]["attributes"]:
            values = [r["attributes"][attribute] for r in responses]
            values = [v for v in values if v not in nan_values]

            if len(values) > 0:
                populated_attributes.append(attribute)

        if len(populated_attributes) > 0:
            superiors = overview[ldap_class]["superiors"]
            output[ldap_class] = make_overview_entry(populated_attributes, superiors)

    return [output]


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
        "ldap_overview_loader": load_ldap_overview,
        "ldap_populated_overview_loader": load_ldap_populated_overview,
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
