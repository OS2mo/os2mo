# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""LDAP change event generation."""
import asyncio
from contextlib import suppress
from datetime import datetime
from datetime import timezone
from functools import partial
from typing import Any
from typing import AsyncContextManager
from typing import Self
from typing import cast
from uuid import UUID

import structlog
from fastramqpi.context import Context
from fastramqpi.depends import UserContext
from fastramqpi.ramqp import AMQPSystem
from ldap3 import Connection

from .config import Settings
from .ldap import ldap_search
from .ldap import ldapresponse2entries
from .ldap_emit import publish_uuids
from .utils import combine_dn_strings

logger = structlog.stdlib.get_logger()


class LDAPEventGenerator(AsyncContextManager):
    def __init__(self, context: Context) -> None:
        """Periodically poll LDAP for changes."""
        self._context = context
        self._pollers: set[asyncio.Task] = set()

    async def __aenter__(self) -> Self:
        """Start event generator."""
        user_context: UserContext = self._context["user_context"]
        settings: Settings = user_context["settings"]

        search_bases = {
            combine_dn_strings([ldap_ou_to_scan_for_changes, settings.ldap_search_base])
            for ldap_ou_to_scan_for_changes in settings.ldap_ous_to_search_in
        }

        self._pollers = {
            setup_poller(
                user_context,
                {
                    "search_base": search_base,
                    "attributes": [settings.ldap_unique_id_field],
                },
                datetime.now(timezone.utc),
                settings.poll_time,
            )
            for search_base in search_bases
        }
        return self

    async def __aexit__(
        self, __exc_tpe: object, __exc_value: object, __traceback: object
    ) -> None:
        """Stop event generator."""
        # Signal all pollers to shutdown
        for poller in self._pollers:
            poller.cancel()
        # Wait for all pollers to be shutdown
        for poller in self._pollers:
            with suppress(asyncio.CancelledError):
                await poller

    async def healthcheck(self, context: dict | Context) -> bool:
        return all(not poller.done() for poller in self._pollers)


def setup_poller(
    user_context: UserContext,
    search_parameters: dict,
    init_search_time: datetime,
    poll_time: float,
) -> asyncio.Task:
    def done_callback(future):
        # This ensures exceptions go to the terminal
        future.result()

    handle = asyncio.create_task(
        _poller(user_context, search_parameters, init_search_time, poll_time)
    )
    handle.add_done_callback(done_callback)
    return handle


async def _poll(
    user_context: UserContext,
    search_parameters: dict,
    last_search_time: datetime,
) -> datetime:
    """Pool the LDAP server for changes once.

    Args:
        context:
            The entire settings context.
        search_params:
            LDAP search parameters.
        callback:
            Function to call with all changes since `last_search_time`.
        last_search_time:
            Find events that occured since this time.

    Returns:
        A two-tuple containing a list of events to ignore and the time at
        which the last search was done.

        Should be provided as `last_search_time` in the next iteration.
    """
    ldap_amqpsystem: AMQPSystem = user_context["ldap_amqpsystem"]
    ldap_connection: Connection = user_context["ldap_connection"]
    settings: Settings = user_context["settings"]

    logger.debug(
        "Searching for changes since last search", last_search_time=last_search_time
    )
    # NOTE: I am not convinced that using modifyTimestamp actually works, since it is
    #       a non-replicable attribute, and thus every single domain controller may have
    #       a different value for the same entry, thus if we hit different domain
    #       controllers we may get duplicate (fine) and missed (not fine) events.
    search_filter = f"(modifyTimestamp>={datetime_to_ldap_timestamp(last_search_time)})"
    search_parameters["search_filter"] = search_filter
    last_search_time = datetime.now(timezone.utc)

    response, _ = await ldap_search(ldap_connection, **search_parameters)

    # Filter to only keep search results
    responses = ldapresponse2entries(response)

    def event2uuid(event: dict[str, Any]) -> UUID | None:
        uuid = event.get("attributes", {}).get(settings.ldap_unique_id_field, None)
        if uuid is None:
            logger.warning("Got event without uuid")
            return None
        return UUID(uuid)

    uuids_with_none = {event2uuid(event) for event in responses}
    uuids_with_none.discard(None)
    uuids = cast(set[UUID], uuids_with_none)
    await publish_uuids(ldap_amqpsystem, list(uuids))

    return last_search_time


async def _poller(
    user_context: UserContext,
    search_parameters: dict,
    init_search_time: datetime,
    poll_time: float,
) -> None:
    """Poll the LDAP server continuously every `poll_time` seconds.

    Args:
        context:
            The entire settings context.
        search_params:
            LDAP search parameters.
        callback:
            Function to call with all changes since `last_search_time`.
        init_search_time:
            Find events that occured since this time.
        pool_time:
            The interval with which to poll.
    """
    logger.info("Poller started", search_base=search_parameters["search_base"])

    seeded_poller = partial(
        _poll,
        user_context=user_context,
        search_parameters=search_parameters,
    )

    last_search_time = init_search_time
    while True:
        last_search_time = await seeded_poller(last_search_time=last_search_time)
        await asyncio.sleep(poll_time)


def datetime_to_ldap_timestamp(dt: datetime) -> str:
    assert dt.tzinfo is not None
    # The LDAP Generalized Time ABNF requires century+year to be 4 digits.
    # However strftime %Y only returns a single digit (1) for year 1.
    return dt.strftime("%Y").rjust(4, "0") + dt.strftime("%m%d%H%M%S.%f%z")
