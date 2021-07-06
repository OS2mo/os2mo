# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0


import requests
from fastapi import APIRouter
from pika.exceptions import AMQPError
from requests.exceptions import RequestException
from structlog import get_logger

import mora.async_util
from mora import conf_db, lora, config
from mora.exceptions import HTTPException
from mora.triggers.internal import amqp_trigger

router = APIRouter()

logger = get_logger()

HEALTH_ENDPOINTS = []


def register_health_endpoint(func):
    HEALTH_ENDPOINTS.append(func)

    url = "/" + func.__name__
    restricted_args_func = func  # util.restrictargs()(func)
    endpoint_func = router.get(url)(restricted_args_func)
    return endpoint_func


@register_health_endpoint
def amqp():
    """Check if AMQP connection is open.

    Return `True` if open. `False` if not open or an error occurs.
    `None` if AMQP support is disabled.
    """
    if not config.get_settings().amqp_enable:
        return None
    connection = amqp_trigger.get_connection()

    try:
        conn = connection.get("conn")
    except AMQPError as e:
        logger.exception("AMQP health check error", e=e)
        return False

    if not conn:
        logger.critical("AMQP connection not found")
        return False

    if not conn.is_open:
        logger.critical("AMQP connection is closed")
        return False

    return True


@register_health_endpoint
def oio_rest():
    """
    Check if the configured oio_rest can be reached
    :return: True if reachable. False if not
    """
    url = config.get_settings().lora_url + "site-map"
    try:
        r = requests.get(url)

        if r.status_code == 200:
            return True
        else:
            logger.critical("oio_rest returned status code",
                            request_status_code=r.status_code)
            return False
    except RequestException as e:
        logger.exception("oio_rest returned", exception=e)
        return False


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
@mora.async_util.async_to_sync  # needs to be sync, flask blueprint endpoint
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
def dar():
    """
    Check whether DAR can be reached
    :return: True if reachable. False if not.
    """
    url = "https://dawa.aws.dk/autocomplete"
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            return True
        else:
            return False
    except RequestException:
        return False


@router.get("/")
# @util.restrictargs()
def root():
    health = {func.__name__: func() for func in HEALTH_ENDPOINTS}
    return health


def register_routes():
    for func in HEALTH_ENDPOINTS:
        url = f"/{func.__name__}"
        router.add_api_route(url, func)
