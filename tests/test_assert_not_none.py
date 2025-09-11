# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest

from mo_ldap_import_export.environments.main import assert_not_none


@pytest.mark.parametrize(
    "x",
    (
        False,
        True,
        69,
        "Hello World",
        object(),
        list(),
        set(),
        dict(),
        tuple(),
        ("Love", ["your"], {"rage"}, {"not": "your cage"}),
    ),
)
async def test_identity(x: Any) -> None:
    assert assert_not_none(x) == x


async def test_none_exception() -> None:
    with pytest.raises(AssertionError) as exc_info:
        assert_not_none(None)
    assert "assert_not_none failed" in str(exc_info.value)
