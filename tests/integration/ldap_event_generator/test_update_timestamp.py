# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import UTC
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from mo_ldap_import_export.ldap_event_generator import LastRun
from mo_ldap_import_export.ldap_event_generator import _generate_events


async def get_last_run(
    sessionmaker: async_sessionmaker[AsyncSession], search_base: str
) -> datetime | None:
    async with sessionmaker() as session, session.begin():
        # Get last run time from database for updating
        last_run = await session.scalar(
            select(LastRun).where(LastRun.search_base == search_base)
        )
        if last_run is None:
            return None
        assert last_run.datetime is not None
        return last_run.datetime


async def num_last_run_entries(sessionmaker: async_sessionmaker[AsyncSession]) -> int:
    async with sessionmaker() as session, session.begin():
        result = await session.execute(select(LastRun))
        return len(result.fetchall())


@pytest.mark.integration_test
@pytest.mark.envvar(
    # If we are listening to changes in LDAP it will write concurrently with us
    {"LISTEN_TO_CHANGES_IN_LDAP": "False"}
)
@pytest.mark.usefixtures("test_client")
async def test_update_timestamp_postgres(context: Context) -> None:
    sessionmaker = context["sessionmaker"]

    test_start = datetime.now(UTC)

    async def seeded_poller(
        last_search_time: datetime,
    ) -> tuple[set[UUID], datetime | None]:
        return {uuid4()}, datetime.now()

    for count, search_base in enumerate(["dc=ad0", "dc=ad1", "dc=ad2"]):
        assert await num_last_run_entries(sessionmaker) == count

        last_run = await get_last_run(sessionmaker, search_base)
        assert last_run is None

        await _generate_events(AsyncMock(), search_base, sessionmaker, seeded_poller)
        first_run = await get_last_run(sessionmaker, search_base)
        assert first_run is not None
        assert first_run > test_start
        assert await num_last_run_entries(sessionmaker) == count + 1

        await _generate_events(AsyncMock(), search_base, sessionmaker, seeded_poller)
        last_run = await get_last_run(sessionmaker, search_base)
        assert last_run is not None
        assert last_run > first_run
        assert await num_last_run_entries(sessionmaker) == count + 1


@pytest.mark.integration_test
@pytest.mark.envvar({"LISTEN_TO_CHANGES_IN_LDAP": "False"})
@pytest.mark.usefixtures("test_client")
async def test_update_timestamp_no_changes(context: Context) -> None:
    sessionmaker = context["sessionmaker"]

    test_start = datetime.now(UTC)

    async def seeded_poller(
        last_search_time: datetime,
    ) -> tuple[set[UUID], datetime | None]:
        return {uuid4()}, datetime.now()

    async def seeded_poller_without_results(
        last_search_time: datetime,
    ) -> tuple[set[UUID], datetime | None]:
        return set(), None

    search_base = "dc=ad0"

    last_run = await get_last_run(sessionmaker, search_base)
    assert last_run is None

    await _generate_events(AsyncMock(), search_base, sessionmaker, seeded_poller)
    first_run = await get_last_run(sessionmaker, search_base)
    assert first_run is not None
    assert first_run > test_start

    await _generate_events(
        AsyncMock(), search_base, sessionmaker, seeded_poller_without_results
    )
    last_run = await get_last_run(sessionmaker, search_base)
    assert last_run == first_run
