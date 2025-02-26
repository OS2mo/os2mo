# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import UTC
from datetime import datetime

import pytest
from fastramqpi.context import Context
from sqlalchemy import select

from mo_ldap_import_export.ldap_event_generator import LastRun


@pytest.mark.integration_test
@pytest.mark.envvar(
    # If we are listening to changes in LDAP it will write concurrently with us
    {"LISTEN_TO_CHANGES_IN_LDAP": "False"}
)
@pytest.mark.usefixtures("test_client")
async def test_last_run_postgres(context: Context) -> None:
    sessionmaker = context["sessionmaker"]

    async with sessionmaker() as session, session.begin():
        result = await session.execute(select(LastRun))
        assert result.fetchall() == []

    async with sessionmaker() as session, session.begin():
        last_run = LastRun(search_base="dc=ad")
        session.add(last_run)
        assert last_run.id is None
        assert last_run.search_base == "dc=ad"
        assert last_run.datetime is None

    async with sessionmaker() as session, session.begin():
        fetched_last_run = await session.scalar(select(LastRun))
        assert fetched_last_run.id is not None
        assert fetched_last_run.search_base == "dc=ad"
        assert fetched_last_run.datetime == datetime.min.replace(tzinfo=UTC)
