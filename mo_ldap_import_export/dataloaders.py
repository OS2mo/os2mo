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

from .exceptions import NoObjectsReturnedException
from .ldap import get_ldap_attributes
from .ldap import get_ldap_schema
from .ldap import get_ldap_superiors
from .ldap import paged_search
from .ldap import single_object_search
from .ldap_classes import GenericLdapObject
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
    ldap_overview_loader: DataLoader
    ldap_populated_overview_loader: DataLoader


def is_dn(value):
    if type(value) is not str:
        return False
    elif ("CN=" in value) and ("OU=" in value) and ("DC=" in value):
        return True
    else:
        return False


def make_ldap_object(response: dict, context: Context, nest=True) -> Any:
    """
    Takes an ldap response and formats it as a class
    """
    logger = structlog.get_logger()
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]
    attributes = list(response["attributes"].keys())
    cpr_field = user_context["cpr_field"]

    ldap_dict = {"dn": response["dn"]}

    object_class: Any
    if cpr_field in attributes:
        object_class = LdapEmployee

        # The employee class must contain a cpr number field
        cpr_number = response["attributes"][cpr_field]

        # TODO: Add a cpr number check here?
        ldap_dict["cpr"] = str(cpr_number)

    else:
        object_class = GenericLdapObject

    def get_ldap_object(dn):

        if nest is False:
            return dn

        searchParameters = {
            "search_base": dn,
            "search_filter": "(objectclass=*)",
            "attributes": ["*"],
        }
        search_result = single_object_search(searchParameters, ldap_connection)
        logger.info("[make_ldap_object] Found %s" % search_result["dn"])

        return make_ldap_object(search_result, context, nest=False)

    def is_other_dn(value):
        return is_dn(value) & (value != response["dn"])

    for attribute in attributes:
        value = response["attributes"][attribute]
        if value == []:
            ldap_dict[attribute] = None
        elif is_other_dn(value):
            ldap_dict[attribute] = get_ldap_object(value)
        elif type(value) is list:
            ldap_dict[attribute] = [
                get_ldap_object(v) if is_other_dn(v) else v for v in value
            ]
        else:
            ldap_dict[attribute] = value

    return object_class(**ldap_dict)


async def load_ldap_employee(keys: list[str], context: Context) -> list[LdapEmployee]:

    logger = structlog.get_logger()
    user_context = context["user_context"]
    search_base = user_context["settings"].ldap_search_base
    user_class = user_context["settings"].ldap_user_class
    ldap_connection = user_context["ldap_connection"]
    output = []

    for cpr in keys:
        searchParameters = {
            "search_base": search_base,
            "search_filter": "(&(objectclass=%s)(%s=%s))"
            % (user_class, user_context["cpr_field"], cpr),
            "attributes": ["*"],
        }
        search_result = single_object_search(searchParameters, ldap_connection)

        employee: LdapEmployee = make_ldap_object(search_result, context)

        logger.info("Found %s" % employee.dn)
        output.append(employee)

    return output


async def load_ldap_employees(key: int, context: Context) -> list[list[LdapEmployee]]:
    """
    Returns list with all employees
    """

    user_class = context["user_context"]["settings"].ldap_user_class
    searchParameters = {
        "search_filter": "(objectclass=%s)" % user_class,
        "attributes": ["*"],
    }

    responses = paged_search(context, searchParameters)

    output: list[LdapEmployee] = [
        make_ldap_object(r, context, nest=False) for r in responses
    ]

    return [output]


async def upload_ldap_employee(
    keys: list[LdapEmployee],
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
                ldap_connection.add(dn, user_class)
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
            "search_filter": "(objectclass=%s)" % ldap_class,
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
