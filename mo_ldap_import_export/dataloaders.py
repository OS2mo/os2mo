# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""
import typing
from functools import partial

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
    mo_users_loader: DataLoader


async def load_ad_organizationalPersons(
    key: int,
    ad_connection: Connection,
    search_base: str,
) -> list[list[dict[str, typing.Any]]]:
    """
    Returns list with all organizationalPersons
    """
    logger = structlog.get_logger()
    output = []

    searchParameters = {
        "search_base": search_base,
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["Name", "Department", "objectGUID"],
        "paged_size": 500,  # TODO: Find this number from AD rather than hard-code it?
    }

    page = 0
    while True:
        logger.info("searching page %d" % page)
        page += 1
        ad_connection.search(**searchParameters)
        output.extend(ad_connection.entries)

        # TODO: Skal 1.2.... være Configurerbar?
        cookie = ad_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    output_dict = [
        {
            "guid": o.objectGUID.value,
            "name": o.Name.value,
            "department": o.Department.value,
        }
        for o in output
    ]

    return [output_dict]


# # pylint: disable=too-few-public-methods
# class ITUser(BaseModel):
#     """Submodel for the GraphQL response from load_mo_users."""

#     itsystem_uuid: UUID
#     user_key: str


# # pylint: disable=too-few-public-methods
# class User(BaseModel):
#     """Model for the GraphQL response from load_mo_users."""

#     itusers: list[ITUser]
#     uuid: UUID


async def load_mo_users(
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
        "mo_users_loader": load_mo_users,
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

    return Dataloaders(
        **graphql_dataloaders,
        ad_org_persons_loader=ad_org_persons_loader,
    )
