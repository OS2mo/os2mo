# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""LDAP change event generation."""

import asyncio
from collections.abc import Awaitable
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from contextlib import suppress
from datetime import UTC
from datetime import datetime
from functools import partial
from typing import Annotated
from typing import Any
from typing import Self
from typing import cast

import structlog
from fastapi import APIRouter
from fastapi import Body
from fastramqpi.context import Context
from fastramqpi.ramqp import AMQPSystem
from ldap3 import Connection
from sqlalchemy import ARRAY
from sqlalchemy import TIMESTAMP
from sqlalchemy import Text
from sqlalchemy import Uuid
from sqlalchemy import select
from sqlalchemy import text
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
from .types import LDAPUUID
from .utils import combine_dn_strings

logger = structlog.stdlib.get_logger()

# The Gregorian reform to the Christian calendar went into effect on the 15th
# of October 1582. The reform operates on a 400-year leap-year cycle.
#
# When Windows NT was being designed by Microsoft, 1601 was chosen to be the
# first supported year in its FILETIME value, as it is the first year of the
# 400-year leap-year cycle that was active when it was being designed.
# The argument for this choice seems to be that choosing 1601 instead of 1582
# (as RFC4122 does for UUIDs) simplifies the math for handling leap-years.
#
# This means that the 1st of January 1601 is the date for which all Microsoft
# Windows file times are calculated, and by extension the reference for all
# Active Directory timestamps.
#
# As such to support finding all entries in Active Directory when searching by
# the modifyTimestamp, the initial search must take in a timestamp
# corresponding to midnight on the 1st of January 1601.
# Picking a time before this simply yields no results as Active Directory does
# not handle dates before this, while picking a time after this date runs the
# risk of missing elements whose modifyTimestamp is "NULL", as "NULL" is
# commonly encoded as zero, and thus as midnight on the 1st of January 1601.
#
# It is worth nothing that it is also the date from which ANSI dates are counted
# and was adopted by the American National Standards Institute for its use in
# COBOL.
#
# A point worth mentioning: challenges may arise however if we emit data related
# to email accounts containing dates prior to midnight of the 1st of April 1601,
# as this is the earliest date possible in Microsoft Outlook.
# Additionally we should be careful not to emit data containing dates after
# midnight of the 1st of January 4501, as this is the time that Microsoft Outlook
# uses as "NULL".
MICROSOFT_EPOCH = datetime(1601, 1, 1, tzinfo=UTC)


class LastRun(Base):
    # NOTE: Tablename was changed here to force table recreation in lieu of Alembic
    __tablename__ = "last_run_gregorian"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_base: Mapped[str] = mapped_column(
        Text, index=True, unique=True, nullable=False
    )
    datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=MICROSOFT_EPOCH,
        nullable=False,
    )
    uuids: Mapped[list[LDAPUUID]] = mapped_column(
        ARRAY(Uuid), default=list, nullable=False
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
        # NOTE: The old tables are droppped here in lieu of Alembic
        # TODO: This code can be removed once it has been run for all customers.
        async with self.sessionmaker() as session, session.begin():
            await session.execute(text("DROP TABLE IF EXISTS last_run;"))
        async with self.sessionmaker() as session, session.begin():
            await session.execute(text("DROP TABLE IF EXISTS last_run_with_uuids;"))

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
) -> tuple[set[LDAPUUID], datetime | None]:
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
        {
            "search_filter": search_filter,
            "attributes": [ldap_unique_id_field, "modifyTimestamp"],
        },
        search_base,
        mute=False,
    )

    # Filter to only keep search results
    responses = ldapresponse2entries(response)

    def event2uuid(event: dict[str, Any]) -> LDAPUUID | None:
        uuid = event["attributes"].get(ldap_unique_id_field, None)
        if uuid is None:
            logger.warning("Got event without uuid")
            return None
        return LDAPUUID(uuid)

    def event2timestamp(event: dict[str, Any]) -> datetime | None:
        modify_timestamp = event["attributes"].get("modifyTimestamp", None)
        if modify_timestamp is None:
            logger.warning("Got event without modifyTimestamp")
            return None
        assert isinstance(modify_timestamp, datetime)
        return modify_timestamp

    uuids_with_none = {event2uuid(event) for event in responses}
    uuids_with_none.discard(None)
    uuids = cast(set[LDAPUUID], uuids_with_none)

    timestamps_with_none = {event2timestamp(event) for event in responses}
    timestamps_with_none.discard(None)
    timestamps = cast(set[datetime], timestamps_with_none)

    return uuids, max(timestamps, default=None)


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
    seeded_poller: Callable[..., Awaitable[tuple[set[LDAPUUID], datetime | None]]],
) -> None:
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
        assert last_run.uuids is not None

        # Fetch changes since last-run and emit events for them
        uuids, timestamp = await seeded_poller(last_search_time=last_run.datetime)
        # Only send out events if either the UUIDs or the timestamp have changed
        # Otherwise we will send out the same event over and over, every 'poll_time'
        # seconds effectively spamming the queue, which is a big issue if the UUID
        # that is getting spammed is stuck.
        if uuids != set(last_run.uuids) or timestamp != last_run.datetime:
            await publish_uuids(ldap_amqpsystem, list(uuids))

        # No events found means no timestamps, which means we reuse the old last_run
        if timestamp is None:
            return

        # Update last run time in database
        last_run.uuids = list(uuids)
        last_run.datetime = timestamp
        session.add(last_run)


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
) -> set[LDAPUUID]:
    uuids, _ = await _poll(
        ldap_connection, search_base, settings.ldap_unique_id_field, since
    )
    return uuids
