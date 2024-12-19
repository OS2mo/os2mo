# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""LDAP change event generation."""

import asyncio
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from contextlib import asynccontextmanager
from contextlib import suppress
from datetime import UTC
from datetime import datetime
from functools import partial
from typing import Annotated
from typing import Any
from typing import Self
from typing import cast
from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi import Body
from fastramqpi.context import Context
from fastramqpi.ramqp import AMQPSystem
from ldap3 import Connection
from sqlalchemy import TIMESTAMP
from sqlalchemy import Text
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from . import depends
from .config import Settings
from .database import Base
from .ldap import _paged_search
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
        default=datetime.min.replace(tzinfo=UTC),
        nullable=False,
    )


class LDAPEventGenerator(AbstractAsyncContextManager):
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        settings: Settings,
        ldap_amqpsystem: AMQPSystem,
        ldap_connection: Connection,
    ) -> None:
        """Periodically poll LDAP for changes."""
        self.sessionmaker = sessionmaker
        self.settings = settings
        self.ldap_amqpsystem = ldap_amqpsystem
        self.ldap_connection = ldap_connection

        self._pollers: set[asyncio.Task] = set()

    async def __aenter__(self) -> Self:
        """Start event generator."""
        search_bases = {
            combine_dn_strings(
                [ldap_ou_to_scan_for_changes, self.settings.ldap_search_base]
            )
            for ldap_ou_to_scan_for_changes in self.settings.ldap_ous_to_search_in
        }

        self._pollers = {
            setup_poller(
                self.settings,
                self.ldap_amqpsystem,
                self.ldap_connection,
                self.sessionmaker,
                search_base,
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
    settings: Settings,
    ldap_amqpsystem: AMQPSystem,
    ldap_connection: Connection,
    sessionmaker: async_sessionmaker[AsyncSession],
    search_base: str,
) -> asyncio.Task:
    def done_callback(future):
        # Silence CancelledErrors on shutdown
        with suppress(asyncio.CancelledError):
            # This ensures exceptions go to the terminal
            future.result()

    handle = asyncio.create_task(
        _poller(settings, ldap_amqpsystem, ldap_connection, search_base, sessionmaker)
    )
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

    response = await _paged_search(
        ldap_connection,
        {"search_filter": search_filter, "attributes": [ldap_unique_id_field]},
        search_base,
        mute=False,
    )

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


@asynccontextmanager
async def update_timestamp(
    sessionmaker: async_sessionmaker[AsyncSession], search_base: str
) -> AsyncIterator[datetime]:
    """Async context manager to fetch and update last run time from our rundb.

    Args:
        sessionmaker: The sessionmaker used to create our database sessions.
        search_base: The search base to fetch and update time for.

    Yields:
        The last run time as read from the database.
    """
    # Ensure that a last-run row exists for our search_base
    # We do creates separately to support update locks in normal operation
    async with sessionmaker() as session, session.begin():
        last_run = await session.scalar(
            select(LastRun).where(LastRun.search_base == search_base).with_for_update()
        )
        last_run = last_run or LastRun(search_base=search_base)
        session.add(last_run)

    async with sessionmaker() as session, session.begin():
        # Get last run time from database for updating
        last_run = await session.scalar(
            select(LastRun).where(LastRun.search_base == search_base).with_for_update()
        )
        assert last_run is not None
        assert last_run.datetime is not None

        now = datetime.now(UTC)
        yield last_run.datetime
        # Update last run time in database
        last_run.datetime = now
        session.add(last_run)


async def _poller(
    settings: Settings,
    ldap_amqpsystem: AMQPSystem,
    ldap_connection: Connection,
    search_base: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """Poll the LDAP server continuously every `settings.poll_time` seconds.

    Args:
        context:
            The entire settings context.
        search_base:
            LDAP search base to look for changes in.
        sessionmaker:
            Sessionmaker to create database sessions for our rundb.
    """
    logger.info("Poller started", search_base=search_base)

    seeded_poller = partial(
        _poll,
        ldap_connection=ldap_connection,
        search_base=search_base,
        ldap_unique_id_field=settings.ldap_unique_id_field,
    )

    while True:
        await asyncio.shield(
            _generate_events(ldap_amqpsystem, search_base, sessionmaker, seeded_poller)
        )
        # Wait for a while before running again
        await asyncio.sleep(settings.poll_time)


async def _generate_events(
    ldap_amqpsystem: AMQPSystem,
    search_base: str,
    sessionmaker: async_sessionmaker[AsyncSession],
    seeded_poller: Callable[..., Awaitable[set[UUID]]],
) -> None:
    # Fetch the last run time, and update it after running
    async with update_timestamp(sessionmaker, search_base) as last_run:
        # Fetch changes since last-run and emit events for them
        uuids = await seeded_poller(last_search_time=last_run)
        await publish_uuids(ldap_amqpsystem, list(uuids))


def datetime_to_ldap_timestamp(dt: datetime) -> str:
    assert dt.tzinfo is not None
    # The LDAP Generalized Time ABNF requires century+year to be 4 digits.
    # However, strftime %Y only returns a single digit (1) for year 1.
    # For more details see: RFC 4517 section 3.3.13.
    # https://datatracker.ietf.org/doc/html/rfc4517#section-3.3.13
    # https://ldapwiki.com/wiki/Wiki.jsp?page=GeneralizedTime
    # NOTE: modifyTimestamp in LDAP only has second-level precision, so we
    # CANNOT include sub-second level precision in this timestamp, or we may
    # miss objects modified in the same second as the search.
    # NOTE: The ".0" in the below string is REQUIRED in Active Directory's
    # implementation of Generalized-Time, even though it is OPTIONAL in the
    # standard. This was discovered the hard way, as missing the ".0" results
    # in missing events.
    # See: https://learn.microsoft.com/en-us/windows/win32/adschema/s-string-generalized-time
    return dt.strftime("%Y").rjust(4, "0") + dt.strftime("%m%d%H%M%S.0%z")


ldap_event_router = APIRouter(prefix="/ldap_event_generator")


@ldap_event_router.get("/{since}")
async def fetch_changes_since(
    ldap_connection: depends.Connection,
    settings: depends.Settings,
    since: datetime,
    search_base: Annotated[str, Body()],
) -> set[UUID]:
    return await _poll(
        ldap_connection, search_base, settings.ldap_unique_id_field, since
    )
