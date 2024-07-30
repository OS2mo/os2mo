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
from ldap3 import Connection
from sqlalchemy import TIMESTAMP
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .config import Settings
from .database import Base
from .ldap import ldap_search
from .ldap import ldapresponse2entries
from .ldap_emit import publish_uuids
from .utils import combine_dn_strings

logger = structlog.stdlib.get_logger()


class LastRun(Base):
    __tablename__ = "last_run"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_base: Mapped[str] = mapped_column(
        Text, index=True, unique=True, nullable=False
    )
    datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.min.replace(tzinfo=timezone.utc),
        nullable=False,
    )


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
            setup_poller(user_context, search_base) for search_base in search_bases
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


def setup_poller(user_context: UserContext, search_base: str) -> asyncio.Task:
    def done_callback(future):
        # This ensures exceptions go to the terminal
        future.result()

    handle = asyncio.create_task(_poller(user_context, search_base))
    handle.add_done_callback(done_callback)
    return handle


async def _poll(
    ldap_connection: Connection,
    search_base: str,
    ldap_unique_id_field: str,
    last_search_time: datetime,
) -> set[UUID]:
    """Pool the LDAP server for changes once.

    Args:
        ldap_connection:
            The LDAP connection to use when searching for changes.
        search_base:
            LDAP search base to look for changes in.
        ldap_unique_id_field:
            The name of the unique entity UUID field.
        last_search_time:
            Find events that occured since this time.

    Returns:
        The set of UUIDs that have changed since last_search_time.
    """
    logger.debug(
        "Searching for changes since last search", last_search_time=last_search_time
    )
    # NOTE: I am not convinced that using modifyTimestamp actually works, since it is
    #       a non-replicable attribute, and thus every single domain controller may have
    #       a different value for the same entry, thus if we hit different domain
    #       controllers we may get duplicate (fine) and missed (not fine) events.
    search_filter = f"(modifyTimestamp>={datetime_to_ldap_timestamp(last_search_time)})"
    search_parameters = {
        "search_base": search_base,
        "search_filter": search_filter,
        "attributes": [ldap_unique_id_field],
    }

    response, _ = await ldap_search(ldap_connection, **search_parameters)

    # Filter to only keep search results
    responses = ldapresponse2entries(response)

    def event2uuid(event: dict[str, Any]) -> UUID | None:
        uuid = event.get("attributes", {}).get(ldap_unique_id_field, None)
        if uuid is None:
            logger.warning("Got event without uuid")
            return None
        return UUID(uuid)

    uuids_with_none = {event2uuid(event) for event in responses}
    uuids_with_none.discard(None)
    uuids = cast(set[UUID], uuids_with_none)
    return uuids


async def _poller(user_context: UserContext, search_base: str) -> None:
    """Poll the LDAP server continuously every `settings.poll_time` seconds.

    Args:
        context:
            The entire settings context.
        search_base:
            LDAP search base to look for changes in.
    """
    settings: Settings = user_context["settings"]
    logger.info("Poller started", search_base=search_base)

    ldap_amqpsystem = user_context["ldap_amqpsystem"]

    seeded_poller = partial(
        _poll,
        ldap_connection=user_context["ldap_connection"],
        search_base=search_base,
        ldap_unique_id_field=settings.ldap_unique_id_field,
    )

    last_search_time = datetime.now(timezone.utc)
    while True:
        now = datetime.now(timezone.utc)
        uuids = await seeded_poller(last_search_time=last_search_time)
        last_search_time = now

        await publish_uuids(ldap_amqpsystem, list(uuids))
        await asyncio.sleep(settings.poll_time)


def datetime_to_ldap_timestamp(dt: datetime) -> str:
    assert dt.tzinfo is not None
    # The LDAP Generalized Time ABNF requires century+year to be 4 digits.
    # However strftime %Y only returns a single digit (1) for year 1.
    return dt.strftime("%Y").rjust(4, "0") + dt.strftime("%m%d%H%M%S.%f%z")
