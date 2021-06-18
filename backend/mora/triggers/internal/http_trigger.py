# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import asyncio
import logging
from functools import partial
from typing import Dict, List

import aiohttp
from mora import settings
from mora.async_util import async_session, async_to_sync, in_separate_thread
from mora.triggers import Trigger
from os2mo_http_trigger_protocol import MOTriggerPayload, MOTriggerRegister
from pydantic import parse_obj_as
from fastapi.encoders import jsonable_encoder


logger = logging.getLogger("http_trigger")


# Consideration: Should this subclass Trigger.Error instead?
class HTTPTriggerException(Exception):
    pass


@in_separate_thread
@async_to_sync
async def http_sender(trigger_url: str, trigger_dict: dict, timeout: int):
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
    logger.debug(f"http_sender called with {trigger_url} {trigger_dict} {timeout}")
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with async_session() as session:
        # TODO: Consider changing trigger_dict to MOTriggerPayload throughout
        payload = jsonable_encoder(MOTriggerPayload(**trigger_dict).dict())
        async with session.post(trigger_url, timeout=timeout, json=payload) as response:
            payload = await response.json()
            logger.debug(f"http_sender received {payload} from {trigger_url}")
            if response.status != 200:
                raise HTTPTriggerException(payload["detail"])
            return payload


async def fetch_endpoint_trigger(
    session, endpoint: str, timeout: int = 10
) -> List[MOTriggerRegister]:
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

    logger.debug(f"Sending request to {full_url}")
    timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with session.get(full_url, timeout=timeout) as response:
            try:
                trigger_configuration = parse_obj_as(
                    List[MOTriggerRegister], await response.json()
                )
                return trigger_configuration
            except aiohttp.client_exceptions.ContentTypeError:
                logger.error(f"Unable to parse response from {full_url} (not JSON?)")
                logger.error(await response.text())
    except asyncio.exceptions.TimeoutError:
        logger.error(f"Timeout while connecting to {full_url}")


@in_separate_thread
@async_to_sync
async def fetch_endpoint_triggers(
    endpoints: List[str], timeout: int = 10
) -> Dict[str, List[MOTriggerRegister]]:
    """Construct trigger configuration maps from endpoints.

    Args:
        endpoints: The endpoints to fetch /triggers from.
        timeout: The timeout to apply when making the connections.

    Returns:
        dictionary of endpoint to trigger configuration.
    """

    async with async_session() as session:
        tasks = map(
            partial(fetch_endpoint_trigger, session, timeout=timeout), endpoints
        )
        # TODO: Could do this as an async generator with `.as_completed()`?
        trigger_configs = await asyncio.gather(*tasks)
        trigger_tuples = zip(endpoints, trigger_configs)
        # Filter out Nones
        trigger_tuples = filter(lambda tup: tup[1] is not None, trigger_tuples)
        return dict(trigger_tuples)


def register(app) -> bool:
    """Register triggers for what the http trigger handlers need.

    This method:
    * Checks the configuration of the module
    * Fetches /triggers on all configured http trigger handlers.
    * Registers the http_sender trigger for all the requested events.
    """
    module_settings = settings.config.get("triggers", {}).get("http_trigger", {})
    enabled = module_settings.get("enabled", False)
    if not enabled:
        logger.warning("Module loaded, but not enabled!")
        return False

    endpoints = module_settings.get("http_endpoints", [])
    if not endpoints:
        logger.warning("Module enabled without endpoints!")
        return False

    # Timeout for fetching endpoint trigger configurations (per endpoint)
    fetch_trigger_timeout = module_settings.get("fetch_trigger_timeout", 5)
    # Timeout for handling events (per trigger call)
    # Note: This value is a default, and can be overridden by the external service.
    run_trigger_timeout = module_settings.get("run_trigger_timeout", 5)

    # Fetch configured triggers for all endpoints
    endpoint_trigger_dict = fetch_endpoint_triggers(endpoints, fetch_trigger_timeout)
    logger.debug(f"Got endpoint_trigger_dict {endpoint_trigger_dict}")

    # Register http_sender for all the events found.
    for endpoint, trigger_configuration in endpoint_trigger_dict.items():
        for trigger in trigger_configuration:
            logger.debug(f"Registering trigger for {endpoint}: {trigger}")

            trigger_url = endpoint + trigger.url
            timeout = trigger.timeout or run_trigger_timeout

            Trigger.on(trigger.role_type, trigger.request_type, trigger.event_type)(
                partial(http_sender, trigger_url, timeout=timeout)
            )
    return True
