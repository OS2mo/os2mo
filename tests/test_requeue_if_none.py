# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest

from mo_ldap_import_export.environments.main import requeue_if_none
from mo_ldap_import_export.exceptions import RequeueException


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
    assert requeue_if_none(x) == x


async def test_none_exception() -> None:
    with pytest.raises(RequeueException) as exc_info:
        requeue_if_none(None)
    assert "Requeueing: Object is None" in str(exc_info.value)
