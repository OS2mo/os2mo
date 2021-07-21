# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
from typing import Any
from uuid import UUID

from fastapi import Body
from more_itertools import one

from .errors import handle_gql_error
from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.service.configuration import router as config_router
from mora.service.util import get_configuration


@config_router.post("/ou/{unitid}/configuration", status_code=410)
def set_org_unit_configuration(unitid: UUID, configuration: dict = Body(...)) -> bool:
    """Removed configuration setting endpoint."""
    return False


@config_router.post("/configuration", status_code=410)
def set_global_configuration(configuration: dict = Body(...)) -> bool:
    """Removed global configuration setting endpoint."""
    return False


@config_router.get("/navlinks")
async def get_navlinks() -> list[dict[str, Any]]:
    """Retrieve nav links.

    Returns:
        A list of nav links
    """
    query = """
    query NavlinksQuery {
      configuration(identifiers: ["navlinks"]) {
        jsonified_value
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    configurations = response.data["configuration"]
    if not configurations:
        exceptions.ErrorCodes.E_UNKNOWN()
    try:
        configuration: dict[str, Any] = one(configurations)
    except ValueError as err:
        raise ValueError(
            "Wrong number of configurations returned, expected one."
        ) from err
    navlinks = json.loads(configuration["jsonified_value"])
    if not navlinks:
        navlinks = [{}]
    return navlinks


@config_router.get("/ou/{unitid}/configuration")
async def get_org_unit_configuration(unitid: UUID) -> dict[str, str]:
    """Read configuration settings for an ou.

    Args:
        unitid: Unused UUID.

    Returns:
        A dictionary of settings.
    """
    return await get_configuration()


@config_router.get("/configuration")
async def get_global_configuration() -> dict[str, Any]:
    """Read global configuration settings.

    Returns:
        A dictionary of settings.
    """
    return await get_configuration()
