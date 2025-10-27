# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest

from mo_ldap_import_export.environments.main import construct_default_environment
from mo_ldap_import_export.environments.main import skip_if_exception
from mo_ldap_import_export.exceptions import SkipObject


async def raiser(should_raise: bool) -> int:
    if should_raise:
        raise ValueError("BOOM")
    return 1


async def test_skip_if_exception() -> None:
    result = await skip_if_exception(raiser)(False)
    assert result == 1


async def test_skip_if_exception_raises() -> None:
    with pytest.raises(SkipObject) as exc_info:
        await skip_if_exception(raiser)(True)
    assert "Skipping due to: 'BOOM'" in str(exc_info.value)
    assert "BOOM" in str(exc_info.value.__cause__)


async def test_skip_if_exception_jinja() -> None:
    environment = construct_default_environment()
    environment.globals["__raiser"] = raiser
    template = environment.from_string("{{ skip_if_exception(__raiser)(False) }}")
    result = await template.render_async()
    assert result == "1"


async def test_skip_if_exception_jinja_raises() -> None:
    environment = construct_default_environment()
    environment.globals["__raiser"] = raiser
    template = environment.from_string("{{ skip_if_exception(__raiser)(True) }}")
    with pytest.raises(SkipObject) as exc_info:
        await template.render_async()
    assert "Skipping due to: 'BOOM'" in str(exc_info.value)
    assert "BOOM" in str(exc_info.value.__cause__)
