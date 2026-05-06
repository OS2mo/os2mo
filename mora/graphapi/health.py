# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Endpoints for health checks."""

from collections.abc import Callable

import aiohttp
from fastramqpi.os2mo_dar_client import AsyncDARClient
from structlog import get_logger

from mora.exceptions import HTTPException
from mora.service.org import ConfiguredOrganisation

logger = get_logger()

health_map = {}


def register_health_endpoint(func: Callable) -> Callable:
    health_map[func.__name__] = func
    return func


@register_health_endpoint
async def dataset() -> bool:
    """Check if LoRa contains data.

    This is done by determining if an organisation is properly configured in the system.

    Returns:
        bool: True if data. False if not.
    """
    try:
        await ConfiguredOrganisation.validate()
    except HTTPException:
        logger.warning("Failure in LoRa dataset:", exc_info=True)
    except aiohttp.ClientError:
        logger.warning("Error fetching data from LoRa", exc_info=True)
    return ConfiguredOrganisation.valid


@register_health_endpoint
async def dar() -> bool:
    """Check whether DAR can be reached.

    Returns:
        bool: True if reachable. False if not.
    """
    adarclient = AsyncDARClient(timeout=5)
    async with adarclient:
        return await adarclient.healthcheck()
    return False
