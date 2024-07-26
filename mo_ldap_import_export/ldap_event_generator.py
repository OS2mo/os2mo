# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""LDAP change event generation."""
import asyncio
from contextlib import suppress
from datetime import datetime
from datetime import timezone
from functools import partial
from typing import Any
from typing import cast
from uuid import UUID

import structlog
from fastramqpi.context import Context
from fastramqpi.depends import UserContext
from fastramqpi.ramqp import AMQPSystem
from ldap3 import Connection

from .dataloaders import DataLoader
from .exceptions import NoObjectsReturnedException
from .ldap import ldap_search
from .ldap import ldapresponse2entries
from .ldap_emit import publish_uuids
from .utils import combine_dn_strings

logger = structlog.stdlib.get_logger()


def setup_listener(context: Context) -> set[asyncio.Task]:
    user_context = context["user_context"]

    # Note:
    # We need the dn attribute to trigger sync_tool.import_single_user()
    # We need the modifyTimeStamp attribute to check for duplicate events in _poller()
    settings = user_context["settings"]
    search_bases = {
        combine_dn_strings([ldap_ou_to_scan_for_changes, settings.ldap_search_base])
        for ldap_ou_to_scan_for_changes in settings.ldap_ous_to_search_in
    }

    pollers = {
        setup_poller(
            user_context,
            {
                "search_base": search_base,
                # TODO: Is this actually necessary compared to just getting DN by default?
                "attributes": ["distinguishedName"],
            },
            datetime.now(timezone.utc),
            settings.poll_time,
        )
        for search_base in search_bases
    }
    return pollers


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
    dataloader: DataLoader = user_context["dataloader"]

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

    # NOTE: We can add message deduplication here if needed for performance later
    #       For now we do not care about duplicates, we prefer simplicity
    #       See: !499 for details

    def event2dn(event: dict[str, Any]) -> str | None:
        dn = event.get("attributes", {}).get("distinguishedName", None)
        dn = dn or event.get("dn", None)
        if dn is None:
            logger.warning("Got event without dn")
        return cast(str | None, dn)

    async def dn2uuid(dn: str) -> UUID | None:
        uuid = None
        with suppress(NoObjectsReturnedException):
            uuid = await dataloader.get_ldap_unique_ldap_uuid(dn)
        return uuid

    dns_with_none = [event2dn(event) for event in responses]
    dns = [dn for dn in dns_with_none if dn is not None]

    # TODO: Simply lookup LDAP UUID in the first query saving this transformation
    uuids_with_none = [await dn2uuid(dn) for dn in dns]
    uuids = [uuid for uuid in uuids_with_none if uuid is not None]

    if uuids:
        await publish_uuids(ldap_amqpsystem, uuids)

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


async def poller_healthcheck(
    pollers: set[asyncio.Task], context: dict | Context
) -> bool:
    return all(not poller.done() for poller in pollers)


def datetime_to_ldap_timestamp(dt: datetime) -> str:
    assert dt.tzinfo is not None
    return dt.strftime("%Y%m%d%H%M%S.%f%z")
