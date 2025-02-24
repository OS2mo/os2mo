# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import UTC
from datetime import datetime

import pytest
from fastramqpi.context import Context
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from mo_ldap_import_export.ldap_event_generator import LastRun
from mo_ldap_import_export.ldap_event_generator import update_timestamp


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

    for count, search_base in enumerate(["dc=ad0", "dc=ad1", "dc=ad2"]):
        assert await num_last_run_entries(sessionmaker) == count

        last_run = await get_last_run(sessionmaker, search_base)
        assert last_run is None

        async with update_timestamp(sessionmaker, search_base):
            last_run = await get_last_run(sessionmaker, search_base)
            assert last_run is not None
            assert last_run == datetime.min.replace(tzinfo=UTC)
        assert await num_last_run_entries(sessionmaker) == count + 1

        async with update_timestamp(sessionmaker, search_base):
            last_run = await get_last_run(sessionmaker, search_base)
            assert last_run is not None
            assert last_run > test_start
        assert await num_last_run_entries(sessionmaker) == count + 1
