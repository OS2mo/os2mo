# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio

from aio_pika.exceptions import AMQPError
from fastapi import APIRouter
from httpx import HTTPStatusError
from os2mo_dar_client import AsyncDARClient
from pydantic import AnyUrl
from requests.exceptions import RequestException
from structlog import get_logger

from mora import conf_db
from mora import config
from mora import lora
from mora.exceptions import HTTPException
from mora.http import client
from mora.triggers.internal.amqp_trigger import pools

router = APIRouter()

logger = get_logger()

HEALTH_ENDPOINTS = []


def register_health_endpoint(func):
    HEALTH_ENDPOINTS.append(func)

    url = "/" + func.__name__
    restricted_args_func = func  # util.restrictargs()(func)
    endpoint_func = router.get(url)(restricted_args_func)
    return endpoint_func


async def _is_endpoint_reachable(url: AnyUrl) -> bool:
    """
    Check if the url can be reached

    :param url: the endpoint to check
    :return: True if reachable. False if not
    """

    try:
        r = await client.get(url)
        r.raise_for_status()
        return True
    except HTTPStatusError as err:
        logger.critical(f"Problem contacting {url}", exception=str(err))
        return False
    except Exception as err:
        logger.critical("HTTPX client error", exception=str(err))
        return False


@register_health_endpoint
async def amqp():
    """Check if AMQP connection is open.

    Return `True` if open. `False` if not open or an error occurs.
    `None` if AMQP support is disabled.
    """
    if not config.get_settings().amqp_enable:
        return None

    try:
        async with pools.connection_pool.acquire() as connection:
            if not connection:
                logger.critical("AMQP connection not found")
                return False

            if connection.is_closed:
                logger.critical("AMQP connection is closed")
                return False
    except AMQPError:
        return False

    return True


@register_health_endpoint
async def oio_rest():
    """
    Check if the configured oio_rest can be reached
    :return: True if reachable. False if not
    """
    url = config.get_settings().lora_url + "site-map"
    return await _is_endpoint_reachable(url)


@register_health_endpoint
def configuration_database():
    """
    Check if configuration database is reachable and initialized with default data
    :return: True if reachable and initialized. False if not.
    """
    healthy, msg = conf_db.health_check()
    if not healthy:
        logger.critical("health critical", msg=msg)
    return healthy


@register_health_endpoint
async def dataset():
    """
    Check if LoRa contains data. We check this by determining if an organisation
    exists in the system
    :return: True if data. False if not.
    """
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    try:
        org = await c.organisation.fetch(bvn="%")
        if not org:
            logger.critical("No dataset found in LoRa")
            return False
    except HTTPException as e:
        logger.exception(
            "Fetching data from oio_rest responded with status code", status_code=e.code
        )
        return False
    except RequestException as e:
        logger.exception("Fetching data from oio_rest responded with", exception=e)
        return False
    return True


@register_health_endpoint
async def dar():
    """
    Check whether DAR can be reached
    :return: True if reachable. False if not.
    """
    adarclient = AsyncDARClient(timeout=2)
    async with adarclient:
        return await adarclient.healthcheck()


@register_health_endpoint
async def keycloak():
    """
    Check if Keycloak is running
    """
    settings = config.get_settings()
    url = (
        f"{settings.keycloak_schema}://{settings.keycloak_host}"
        f":{settings.keycloak_port}/auth/"
    )
    return await _is_endpoint_reachable(url)


@router.get("/")
async def root():
    health = {
        func.__name__: await func() if asyncio.iscoroutinefunction(func) else func()
        for func in HEALTH_ENDPOINTS
    }
    return health


def register_routes():
    for func in HEALTH_ENDPOINTS:
        url = f"/{func.__name__}"
        router.add_api_route(url, func)
