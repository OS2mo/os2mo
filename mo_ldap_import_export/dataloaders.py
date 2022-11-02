# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""
from functools import partial
from typing import Union

import structlog
from fastramqpi.context import Context
from gql import gql
from gql.client import AsyncClientSession
from ldap3 import Connection
from more_itertools import flatten
from pydantic import BaseModel
from strawberry.dataloader import DataLoader


# pylint: disable=too-few-public-methods
class Dataloaders(BaseModel):
    """Collection of program dataloaders."""

    class Config:
        """Arbitrary types need to be allowed to have DataLoader members."""

        arbitrary_types_allowed = True

    ad_org_persons_loader: DataLoader
    ad_org_person_loader: DataLoader
    ad_org_persons_uploader: DataLoader
    mo_users_loader: DataLoader


class OrganizationalPerson(BaseModel):
    """Model for an AD organizationalperson"""

    dn: str
    Name: str  # TODO: This field cannot be modified in AD. Add a 'protected' flag?
    Department: Union[str, None]


def get_ad_attributes() -> list[str]:
    return [a for a in OrganizationalPerson.schema()["properties"].keys() if a != "dn"]


async def load_ad_organizationalPerson(
    keys: list[str], ad_connection: Connection
) -> list[OrganizationalPerson]:

    logger = structlog.get_logger()
    output = []

    for dn in keys:
        searchParameters = {
            "search_base": dn,
            "search_filter": "(objectclass=organizationalPerson)",
            "attributes": get_ad_attributes(),
        }

        ad_connection.search(**searchParameters)
        response = ad_connection.response

        if len(response) > 1:
            raise Exception("Found multiple entries for dn=%s" % dn)
        elif len(response) == 0:
            raise Exception("Found no entries for dn=%s" % dn)

        organizationalPerson = OrganizationalPerson(
            dn=response[0]["dn"],
            Name=response[0]["attributes"]["name"],
            Department=response[0]["attributes"]["department"],
        )

        logger.info("Found %s" % organizationalPerson)
        output.append(organizationalPerson)

    return output


async def load_ad_organizationalPersons(
    key: int,
    ad_connection: Connection,
    search_base: str,
) -> list[list[OrganizationalPerson]]:
    """
    Returns list with all organizationalPersons
    """
    logger = structlog.get_logger()
    output = []

    searchParameters = {
        "search_base": search_base,
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": get_ad_attributes(),
        "paged_size": 500,  # TODO: Find this number from AD rather than hard-code it?
    }

    page = 0
    while True:
        logger.info("searching page %d" % page)
        page += 1
        ad_connection.search(**searchParameters)
        output.extend(ad_connection.entries)

        # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
        cookie = ad_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    output_list = [
        OrganizationalPerson(
            dn=o.entry_dn,
            Name=o.Name.value,
            Department=o.Department.value,
        )
        for o in output
    ]

    return [output_list]


async def upload_ad_organizationalPerson(
    keys: list[OrganizationalPerson], ad_connection: Connection
):
    logger = structlog.get_logger()
    output = []
    success = 0
    failed = 0
    for key in keys:
        dn = key.dn
        parameters_to_upload = [k for k in key.dict().keys() if k != "dn"]
        results = []
        for parameter_to_upload in parameters_to_upload:
            value = key.dict()[parameter_to_upload]
            value_to_upload = [] if value is None else [value]
            changes = {parameter_to_upload: [("MODIFY_REPLACE", value_to_upload)]}

            logger.info("Uploading the following changes: %s" % changes)
            ad_connection.modify(dn, changes)
            response = ad_connection.result

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


async def load_mo_employees(
    key: int, graphql_session: AsyncClientSession
) -> list[list[dict[str, str]]]:
    """Loads User models from UUIDs.

    Args:
        keys: List of user UUIDs.
        graphql_session: The GraphQL session to run queries on.

    Return:
        List of User models.
    """
    query = gql(
        """
        query AllEmployees {
          employees {
            objects {
              cpr_no
              givenname
              name
            }
          }
        }
        """
    )

    result = await graphql_session.execute(query)
    output = list(flatten([r["objects"] for r in result["employees"]]))

    return [output]


def configure_dataloaders(context: Context) -> Dataloaders:
    """Construct our dataloaders from the FastRAMQPI context.

    Args:
        context: The FastRAMQPI context to configure our dataloaders with.

    Returns:
        Dataloaders required for ensure_adguid_itsystem.
    """

    graphql_loader_functions = {
        "mo_users_loader": load_mo_employees,
    }

    graphql_session = context["user_context"]["gql_client"]
    graphql_dataloaders = {
        key: DataLoader(
            load_fn=partial(value, graphql_session=graphql_session), cache=False
        )
        for key, value in graphql_loader_functions.items()
    }

    settings = context["user_context"]["settings"]
    ad_connection = context["user_context"]["ad_connection"]
    ad_org_persons_loader = DataLoader(
        load_fn=partial(
            load_ad_organizationalPersons,
            ad_connection=ad_connection,
            search_base=settings.ad_search_base,
        ),
        cache=False,
    )

    ad_org_person_loader = DataLoader(
        load_fn=partial(load_ad_organizationalPerson, ad_connection=ad_connection),
        cache=False,
    )

    ad_org_persons_uploader = DataLoader(
        load_fn=partial(upload_ad_organizationalPerson, ad_connection=ad_connection),
        cache=False,
    )

    return Dataloaders(
        **graphql_dataloaders,
        ad_org_persons_loader=ad_org_persons_loader,
        ad_org_person_loader=ad_org_person_loader,
        ad_org_persons_uploader=ad_org_persons_uploader
    )
