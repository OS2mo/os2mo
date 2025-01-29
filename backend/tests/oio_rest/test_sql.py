# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pathlib

import pytest
from mora.db import AsyncSession
from more_itertools import one
from sqlalchemy import text
from tap.parser import Parser

from tests.oio_rest import util


@pytest.mark.integration_test
@pytest.mark.parametrize("dbfile", pathlib.Path(util.TESTS_DIR).glob("sql/*.sql"))
async def test_pgsql(subtests, empty_db: AsyncSession, dbfile):
    await empty_db.execute(text('CREATE EXTENSION IF NOT EXISTS "pgtap"'))
    await empty_db.execute(text("CREATE SCHEMA test"))
    # Run the actual test
    await empty_db.execute(text(dbfile.read_text()))
    # Fetch results in TAP format
    r = await empty_db.execute(text("SELECT * FROM runtests ('test'::name)"))
    assert r.returns_rows
    taptext = "\n".join(map(one, r.all()))

    # Parse tap test-results and very if that all tests passed
    tests = Parser().parse_text(taptext)
    tests = filter(lambda result: result.category == "test", tests)
    for test in tests:
        with subtests.test(test.description):
            if test.skip:
                pytest.skip()
            elif not test.ok:
                pytest.fail(test.diagnostics or test.description)
