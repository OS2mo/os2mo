# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""Test conftest fixtures."""
import os
from collections.abc import Iterator

import pytest
from pytest import MonkeyPatch


@pytest.fixture(scope="session")
def monkeysession() -> Iterator[pytest.MonkeyPatch]:
    mpatch = pytest.MonkeyPatch()
    with mpatch.context() as mpc:
        yield mpc


@pytest.mark.envvar({"VAR1": "1", "VAR2": "2"})
@pytest.mark.envvar({"VAR3": "3"})
def test_load_marked_envvars() -> None:
    assert os.environ.get("VAR1") == "1"
    assert os.environ.get("VAR2") == "2"
    assert os.environ.get("VAR3") == "3"
    assert os.environ.get("VAR4") is None


@pytest.mark.parametrize(
    "key,expected",
    [
        pytest.param("VAR1", None, marks=pytest.mark.envvar({})),
        pytest.param("VAR1", "1", marks=pytest.mark.envvar({"VAR1": "1"})),
        pytest.param("VAR1", "2", marks=pytest.mark.envvar({"VAR1": "2"})),
        pytest.param("VAR2", None, marks=pytest.mark.envvar({"VAR1": "2"})),
        pytest.param("VAR2", "2", marks=pytest.mark.envvar({"VAR1": "2", "VAR2": "2"})),
    ],
)
def test_parametrized_envvar_marks(key: str, expected: str) -> None:
    assert os.environ.get(key) == expected


@pytest.fixture
def overrider(monkeysession: MonkeyPatch) -> Iterator[None]:
    with monkeysession.context() as mpc:
        mpc.setenv("VAR1", "overrider")
        yield


@pytest.fixture(scope="session")
def overrider_session(monkeysession: MonkeyPatch) -> Iterator[None]:
    with monkeysession.context() as mpc:
        mpc.setenv("VAR1", "overrider_session")
        yield


@pytest.mark.envvar({"VAR1": "1"})
def test_envvar_order_direct_dependency(overrider: None) -> None:
    assert os.environ.get("VAR1") == "overrider"


@pytest.mark.usefixtures("overrider")
@pytest.mark.envvar({"VAR1": "1"})
def test_envvar_order_usefixtures_first() -> None:
    assert os.environ.get("VAR1") == "overrider"


@pytest.mark.envvar({"VAR1": "1"})
@pytest.mark.usefixtures("overrider")
def test_envvar_order_usefixtures_second() -> None:
    assert os.environ.get("VAR1") == "overrider"


@pytest.mark.envvar({"VAR1": "1"})
def test_envvar_order_session_direct_dependency(overrider_session: None) -> None:
    assert os.environ.get("VAR1") == "1"


@pytest.mark.usefixtures("overrider_session")
@pytest.mark.envvar({"VAR1": "1"})
def test_envvar_order_session_usefixtures_first() -> None:
    assert os.environ.get("VAR1") == "1"


@pytest.mark.envvar({"VAR1": "1"})
@pytest.mark.usefixtures("overrider_session")
def test_envvar_order_session_usefixtures_second() -> None:
    assert os.environ.get("VAR1") == "1"
