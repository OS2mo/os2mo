#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Endpoints for health checks."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from collections.abc import Callable
from typing import Optional

import aiohttp
from httpx import HTTPStatusError
from os2mo_dar_client import AsyncDARClient
from structlog import get_logger

from mora import config
from mora import lora
from mora.exceptions import HTTPException
from mora.service.org import ConfiguredOrganisation
from mora.triggers.internal.amqp_trigger import amqp_system

# --------------------------------------------------------------------------------------
# Health endpoints
# --------------------------------------------------------------------------------------


logger = get_logger()

health_map = {}


def register_health_endpoint(func: Callable) -> Callable:
    health_map[func.__name__] = func
    return func


@register_health_endpoint
async def amqp() -> Optional[bool]:
    """Check if AMQP connection is open.

    Returns:
        Optional[bool]: True if open, False if not open or an error occurs.
            None if AMQP support is disabled.
    """
    if not config.get_settings().amqp_enable:
        return None

    return amqp_system.healthcheck()


@register_health_endpoint
async def oio_rest() -> bool:
    """Check if the configured oio_rest can be reached.

    Returns:
        bool: True if reachable. False if not.
    """
    settings = config.get_settings()
    if settings.enable_internal_lora:
        return True
    try:
        r = await lora.client.get(url="site-map")  # type: ignore
        r.raise_for_status()
        return True
    except HTTPStatusError as err:
        logger.critical("Problem contacting lora", exception=str(err))
        return False
    except Exception as err:
        logger.critical("HTTPX client error", exception=str(err))
        return False
    return False


@register_health_endpoint
async def dataset() -> bool:
    """Check if LoRa contains data.

    This is done by determining if an organisation is properly configured in the system.

    Returns:
        bool: True if data. False if not.
    """
    try:
        await ConfiguredOrganisation.validate()
    except HTTPException as e:
        logger.exception("Failure in LoRa dataset:", exception=e)
    except aiohttp.ClientError as e:
        logger.exception("Error fetching data from LoRa", exception=e)
    return ConfiguredOrganisation.valid


@register_health_endpoint
async def dar() -> bool:
    """Check whether DAR can be reached.

    Returns:
        bool: True if reachable. False if not.
    """
    adarclient = AsyncDARClient(timeout=2)
    async with adarclient:
        return await adarclient.healthcheck()
    return False


@register_health_endpoint
async def keycloak() -> bool:
    """Check nothing.

    Keycloak healthchecking has been removed completely, as we only communicate
    with Keycloak once on startup when we fetch the JWKS.

    Returns:
        bool: True always
    """
    return True
