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
from aio_pika.exceptions import AMQPError
from httpx import HTTPStatusError
from os2mo_dar_client import AsyncDARClient
from pydantic import AnyUrl
from pydantic import parse_obj_as
from structlog import get_logger

from mora import conf_db
from mora import config
from mora.exceptions import HTTPException
from mora.http import clients
from mora.service.org import ConfiguredOrganisation

# --------------------------------------------------------------------------------------
# Health endpoints
# --------------------------------------------------------------------------------------


logger = get_logger()

health_map = {}


def register_health_endpoint(func: Callable) -> Callable:
    health_map[func.__name__] = func
    return func


async def _is_endpoint_reachable(url: AnyUrl) -> bool:
    """Check if a given endpoint is reachable.

    Args:
        url (AnyUrl): The endpoint to check.

    Returns:
        bool: True if reachable. False if not.
    """
    try:
        r = await clients.mo.get(url)
        r.raise_for_status()
        return True
    except HTTPStatusError as err:
        logger.critical(f"Problem contacting {url}", exception=str(err))
        return False
    except Exception as err:
        logger.critical("HTTPX client error", exception=str(err))
        return False


@register_health_endpoint
async def amqp() -> Optional[bool]:
    """Check if AMQP connection is open.

    Returns:
        Optional[bool]: True if open, False if not open or an error occurs.
            None if AMQP support is disabled.
    """
    if not config.get_settings().amqp_enable:
        return None

    return True


@register_health_endpoint
async def oio_rest() -> bool:
    """Check if the configured oio_rest can be reached.

    Returns:
        bool: True if reachable. False if not.
    """
    url = config.get_settings().lora_url + "site-map"
    parsed_url: AnyUrl = parse_obj_as(AnyUrl, url)
    return await _is_endpoint_reachable(parsed_url)


@register_health_endpoint
async def configuration_database() -> bool:
    """Check if configuration database is reachable and initialized with default data.

    Returns:
        bool: True if reachable and initialized. False if not.
    """
    healthy, msg = conf_db.health_check()
    if not healthy:
        logger.critical("health critical", msg=msg)
    return healthy


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


@register_health_endpoint
async def keycloak() -> bool:
    """Check if Keycloak is running.

    Returns:
        bool: True if reachable. False if not.
    """
    settings = config.get_settings()
    url = (
        f"{settings.keycloak_schema}://{settings.keycloak_host}"
        f":{settings.keycloak_port}/auth/"
    )
    parsed_url: AnyUrl = parse_obj_as(AnyUrl, url)
    return await _is_endpoint_reachable(parsed_url)
