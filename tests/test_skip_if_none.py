# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest

from mo_ldap_import_export.environments import skip_if_none
from mo_ldap_import_export.exceptions import SkipObject


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
    assert skip_if_none(x) == x


async def test_none_exception() -> None:
    with pytest.raises(SkipObject) as exc_info:
        skip_if_none(None)
    assert "Skipping: Object is None" in str(exc_info.value)
