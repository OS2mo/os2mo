# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""

from fastramqpi.context import Context
from ldap3 import Connection
from pydantic import BaseModel
from strawberry.dataloader import DataLoader
from functools import partial
import structlog


# pylint: disable=too-few-public-methods
class Dataloaders(BaseModel):
    """Collection of program dataloaders.

    Args:
        users_loader: Loads User models from UUIDs.
        itsystems_loader: Loads ITSystem UUIDs from user-keys.
        adguid_loader: Loads AD GUIDs (UUIDs) from CPR numbers.
    """

    class Config:
        """Arbitrary types need to be allowed to have DataLoader members."""

        arbitrary_types_allowed = True

    org_persons_loader: DataLoader


async def load_organizationalPersons(
    key: int,
    ad_connection: Connection,
    search_base: str,
) -> list[dict]:
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
        cookie = ad_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]
        if cookie:
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


def configure_dataloaders(context: Context) -> Dataloaders:
    """Construct our dataloaders from the FastRAMQPI context.

    Args:
        context: The FastRAMQPI context to configure our dataloaders with.

    Returns:
        Dataloaders required for ensure_adguid_itsystem.
    """

    settings = context["user_context"]["settings"]
    ad_connection = context["user_context"]["ad_connection"]
    org_persons_loader = DataLoader(
        load_fn=partial(
            load_organizationalPersons,
            ad_connection=ad_connection,
            search_base=settings.ad_search_base,
        ),
        cache=False,
    )

    return Dataloaders(
        org_persons_loader=org_persons_loader,
    )
