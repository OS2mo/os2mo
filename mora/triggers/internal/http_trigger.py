# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from functools import partial

import aiohttp
from fastapi.encoders import jsonable_encoder
from os2mo_http_trigger_protocol import MOTriggerPayload
from os2mo_http_trigger_protocol import MOTriggerRegister
from pydantic import parse_obj_as
from structlog import get_logger

from mora import config
from mora.triggers import Trigger

logger = get_logger()


# Consideration: Should this subclass Trigger.Error instead?
class HTTPTriggerException(Exception):
    pass


async def http_sender(
    trigger_url: str, trigger_dict: dict, timeout: int
):  # pragma: no cover
    """Triggers the provided event over HTTP(s).

    Args:
        trigger_url: The URL to send the trigger_dict to (seeded using partial).
        trigger_dict: The event dictionary itself, aka. the payload.
        timeout: The timeout to apply while waiting for the external handler.

    Returns:
        An exception or None:
            An exception if the external service returns a non-200 status-code.

            This will block the change from happening in MO, and the service is
            expected to return a reason for why it is blocking it in a JSON response
            field named 'detail'.

            None is returned if no exceptions occur.
    """
    logger.debug(
        "http_sender called",
        trigger_url=trigger_url,
        trigger_dict=trigger_dict,
        timeout=timeout,
    )
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession() as session:
        # TODO: Consider changing trigger_dict to MOTriggerPayload throughout
        payload = jsonable_encoder(MOTriggerPayload(**trigger_dict).dict())
        async with session.post(
            trigger_url, timeout=client_timeout, json=payload
        ) as response:
            payload = await response.json()
            logger.debug(
                "http_sender received", payload=payload, trigger_url=trigger_url
            )
            if response.status != 200:
                raise HTTPTriggerException(payload["detail"])
            return payload


async def fetch_endpoint_trigger(
    session, endpoint: str, timeout: int = 10
) -> list[MOTriggerRegister]:  # pragma: no cover
    """Fetch the trigger configuration from endpoint.

    Note: Expects the /triggers endpoint to return a JSON list with this format:

    .. code-block:: JSON

        [{
            "event_type": 0,
            "request_type": 0,
            "role_type": "org_unit",
            "url": "/triggers/ou/create",
            "timeout": 10
        }]

    Where:
    * `event_type`, `request_type` and `role_type` define the trigger event.
    * `url` is the `url` to send the `trigger_dict` payload to.
    * `timeout` is the absolute maximum expected runtime.

    Args:
        session: The aiohttp session to utilize for the connection.
        endpoint: The endpoint to fetch /triggers from.
        timeout: The timeout to apply when making the connection.

    Returns:
        list of triggers or None if an error occurs.
    """
    full_url = endpoint + "/triggers"

    logger.debug("Sending request to", full_url=full_url)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with session.get(full_url, timeout=client_timeout) as response:
            try:
                trigger_configuration = parse_obj_as(
                    list[MOTriggerRegister], await response.json()
                )
                return trigger_configuration
            except aiohttp.client_exceptions.ContentTypeError as exc:
                logger.error(
                    "Unable to parse response from (not JSON?)", full_url=full_url
                )
                logger.error(reponse_text=await response.text())
                raise exc
    except asyncio.exceptions.TimeoutError as exc:
        logger.error("Timeout while connecting to", full_url=full_url)
        raise exc


async def fetch_endpoint_triggers(
    endpoints: list[str], timeout: int = 10
) -> dict[str, list[MOTriggerRegister]]:
    """Construct trigger configuration maps from endpoints.

    Args:
        endpoints: The endpoints to fetch /triggers from.
        timeout: The timeout to apply when making the connections.

    Returns:
        dictionary of endpoint to trigger configuration.
    """

    async with aiohttp.ClientSession() as session:
        tasks = map(
            partial(fetch_endpoint_trigger, session, timeout=timeout), endpoints
        )
        # TODO: Could do this as an async generator with `.as_completed()`?
        trigger_configs = await asyncio.gather(*tasks)
        trigger_tuples = zip(endpoints, trigger_configs)
        # Filter out Nones
        trigger_tuples = filter(lambda tup: tup[1] is not None, trigger_tuples)
        return dict(trigger_tuples)


async def register(app) -> bool:
    """Register triggers for what the http trigger handlers need.

    This method:
    * Checks the configuration of the module.
    * Fetches /triggers on all configured http trigger handlers.
    * Registers the http_sender trigger for all the requested events.
    """
    settings = config.get_settings()
    endpoints = settings.http_endpoints
    if not endpoints:
        logger.debug("HTTP Triggers has no endpoints!")
        return False

    # Timeout for fetching endpoint trigger configurations (per endpoint)
    fetch_trigger_timeout = settings.fetch_trigger_timeout
    # Timeout for handling events (per trigger call)
    # Note: This value is a default, and can be overridden by the external service.
    run_trigger_timeout = settings.run_trigger_timeout

    # Fetch configured triggers for all endpoints
    endpoint_trigger_dict = await fetch_endpoint_triggers(
        endpoints, fetch_trigger_timeout
    )
    logger.debug(
        "Got endpoint_trigger_dict", endpoint_trigger_dict=endpoint_trigger_dict
    )

    # Register http_sender for all the events found.
    for endpoint, trigger_configuration in endpoint_trigger_dict.items():
        for trigger in trigger_configuration:
            logger.debug("Registering trigger for", endpoint=endpoint, trigger=trigger)

            trigger_url = endpoint + trigger.url
            timeout = trigger.timeout or run_trigger_timeout

            Trigger.on(trigger.role_type, trigger.request_type, trigger.event_type)(
                partial(http_sender, trigger_url, timeout=timeout)
            )
    return True
