# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
import asyncio
import os
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastramqpi.main import FastRAMQPI
from ramodels.mo.employee import Employee
from strawberry.dataloader import DataLoader

from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import Dataloaders
from mo_ldap_import_export.ldap_classes import LdapEmployee
from mo_ldap_import_export.main import create_app
from mo_ldap_import_export.main import create_fastramqpi
from mo_ldap_import_export.main import listen_to_changes_in_employees
from mo_ldap_import_export.main import open_ldap_connection
from mo_ldap_import_export.main import seed_dataloaders


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    overrides = {
        "CLIENT_ID": "Foo",
        "CLIENT_SECRET": "bar",
        "LDAP_CONTROLLERS": '[{"host": "localhost"}]',
        "LDAP_DOMAIN": "LDAP",
        "LDAP_USER": "foo",
        "LDAP_PASSWORD": "foo",
        "LDAP_SEARCH_BASE": "DC=ad,DC=addev",
        "LDAP_ORGANIZATIONAL_UNIT": "OU=Magenta",
    }
    yield overrides


@pytest.fixture
def load_settings_overrides(
    settings_overrides: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[dict[str, str]]:
    """Fixture to set happy-path settings overrides as environmental variables.

    Note:
        Only loads environmental variables, if variables are not already set.

    Args:
        settings_overrides: The list of settings to load in.
        monkeypatch: Pytest MonkeyPatch instance to set environmental variables.

    Yields:
        Minimal set of overrides.
    """
    for key, value in settings_overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield settings_overrides


@pytest.fixture
def disable_metrics(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Fixture to set the ENABLE_METRICS environmental variable to False.

    Yields:
        None
    """
    monkeypatch.setenv("ENABLE_METRICS", "False")
    yield


@pytest.fixture
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def empty_dataloaders() -> Dataloaders:
    async def empty_fn(keys):
        return ["foo"] * len(keys)

    dlDict = {}
    for dl in Dataloaders.schema()["required"]:
        dlDict[dl] = DataLoader(load_fn=empty_fn, cache=False)

    return Dataloaders(**dlDict)


@pytest.fixture
def fastramqpi(
    disable_metrics: None,
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    empty_dataloaders: Dataloaders,
) -> Iterator[FastRAMQPI]:
    """Fixture to construct a FastRAMQPI system.

    Yields:
        FastRAMQPI system.
    """
    with patch(
        "mo_ldap_import_export.main.configure_dataloaders",
        return_value=empty_dataloaders,
    ), patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock
    ), patch(
        "mo_ldap_import_export.main.construct_gql_client",
        return_value=gql_client,
    ):
        yield create_fastramqpi()


@pytest.fixture
def app(fastramqpi: FastRAMQPI) -> Iterator[FastAPI]:
    """Fixture to construct a FastAPI application.

    Yields:
        FastAPI application.
    """
    yield create_app()


@pytest.fixture
def test_client(app: FastAPI) -> Iterator[TestClient]:
    """Fixture to construct a FastAPI test-client.

    Note:
        The app does not do lifecycle management.

    Yields:
        TestClient for the FastAPI application.
    """
    yield TestClient(app)


@pytest.fixture
def ldap_connection() -> Iterator[MagicMock]:
    """Fixture to construct a mock ldap_connection.

    Yields:
        A mock for ldap_connection.
    """
    yield MagicMock()


def test_create_app(
    load_settings_overrides: dict[str, str],
) -> None:
    """Test that we can construct our FastAPI application."""

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock
    ):
        app = create_app()
    assert isinstance(app, FastAPI)


def test_create_fastramqpi(
    load_settings_overrides: dict[str, str], disable_metrics: None
) -> None:
    """Test that we can construct our FastRAMQPI system."""

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock
    ):
        fastramqpi = create_fastramqpi()
    assert isinstance(fastramqpi, FastRAMQPI)


async def test_open_ldap_connection() -> None:
    """Test the open_ldap_connection."""
    state = []

    @contextmanager
    def manager() -> Iterator[None]:
        state.append(1)
        yield
        state.append(2)

    ldap_connection = manager()

    assert not state
    async with open_ldap_connection(ldap_connection):
        assert state == [1]
    assert state == [1, 2]


async def test_seed_dataloaders(fastramqpi: FastRAMQPI) -> None:
    """Test the seed_dataloaders asynccontextmanager."""

    fastramqpi.add_context(ldap_connection=MagicMock)

    user_context = fastramqpi.get_context()["user_context"]
    assert user_context.get("dataloaders") is not None

    async with seed_dataloaders(fastramqpi):
        dataloaders = user_context.get("dataloaders")

    assert dataloaders is not None
    assert isinstance(dataloaders, Dataloaders)


def test_ldap_get_all_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/employee")
    assert response.status_code == 202


def test_ldap_get_all_converted_endpoint(
    test_client: TestClient, empty_dataloaders: Dataloaders
) -> None:
    """Test the LDAP get-all endpoint on our app."""

    async def loader(x):
        return [
            [
                LdapEmployee(
                    name="Tester", Department="QA", dn="someDN", cpr="0101011234"
                )
            ]
        ]

    empty_dataloaders.ldap_employees_loader = DataLoader(load_fn=loader, cache=False)

    response = test_client.get("/LDAP/employee/converted")
    assert response.status_code == 202


def test_ldap_get_all_converted_endpoint_failure(
    test_client: TestClient, empty_dataloaders: Dataloaders
) -> None:
    """Test the LDAP get-all endpoint on our app."""

    async def loader(x):
        return [
            [LdapEmployee(name="Tester", Department="QA", dn="someDN", cpr="invalid")]
        ]

    empty_dataloaders.ldap_employees_loader = DataLoader(load_fn=loader, cache=False)

    response = test_client.get("/LDAP/employee/converted")
    assert response.status_code == 202


def test_ldap_get_converted_endpoint(
    test_client: TestClient, empty_dataloaders: Dataloaders
) -> None:
    """Test the LDAP get endpoint on our app."""

    async def loader(x):
        return [
            LdapEmployee(name="Tester", Department="QA", dn="someDN", cpr="0101011234")
        ]

    empty_dataloaders.ldap_employee_loader = DataLoader(load_fn=loader, cache=False)

    response = test_client.get("/LDAP/employee/foo/converted")
    assert response.status_code == 202


def test_ldap_get_converted_endpoint_failure(
    test_client: TestClient, empty_dataloaders: Dataloaders
) -> None:
    """Test the LDAP get endpoint on our app."""

    async def loader(x):
        return [
            LdapEmployee(name="Tester", Department="QA", dn="someDN", cpr="invalid")
        ]

    empty_dataloaders.ldap_employee_loader = DataLoader(load_fn=loader, cache=False)

    response = test_client.get("/LDAP/employee/foo/converted")

    assert response.status_code == 404


def test_ldap_post_ldap_employee_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    ldap_person_to_post = {
        "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        "cpr": "0101121234",
        "name": "Lars Peter Thomsen",
        "Department": None,
    }
    response = test_client.post("/LDAP/employee", json=ldap_person_to_post)
    assert response.status_code == 200


def test_mo_get_all_employees_endpoint(test_client: TestClient) -> None:
    """Test the MO get-all endpoint on our app."""

    response = test_client.get("/MO/employee")
    assert response.status_code == 202


def test_mo_get_employee_endpoint(test_client: TestClient) -> None:
    """Test the MO get-all endpoint on our app."""

    response = test_client.get("/MO/employee/foo")
    assert response.status_code == 202


def test_mo_post_employee_endpoint(test_client: TestClient) -> None:
    """Test the MO get-all endpoint on our app."""

    employee_to_post = {
        "uuid": "ff5bfef4-6459-4ba2-9571-10366ead6f5f",
        "user_key": "ff5bfef4-6459-4ba2-9571-10366ead6f5f",
        "type": "employee",
        "givenname": "Jens Pedersen Munch",
        "surname": "Bisgaard",
        "name": None,
        "cpr_no": "0910443755",
        "seniority": None,
        "org": None,
        "nickname_givenname": "Man who can do 6571 push ups",
        "nickname_surname": "Superman",
        "nickname": None,
        "details": None,
    }

    response = test_client.post("/MO/employee", json=employee_to_post)
    assert response.status_code == 200


def test_ldap_get_organizationalUser_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/employee/foo")
    assert response.status_code == 202


async def test_listen_to_changes_in_employees() -> None:
    async def employee_fn(keys):
        return [Employee(uuid=uuid4(), givenname="Clark", surname="Kent")]

    async def empty_fn(keys):
        return ["foo"] * len(keys)

    dataloader_mock = MagicMock()
    dataloader_mock.mo_employee_loader = DataLoader(load_fn=employee_fn, cache=False)

    dataloader_mock.ldap_employees_uploader = DataLoader(load_fn=empty_fn, cache=False)

    settings_mock = MagicMock()
    settings_mock.ldap_organizational_unit = "foo"
    settings_mock.ldap_search_base = "bar"

    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )

    converter_mock = MagicMock()
    converter_mock.cpr_field = "EmployeeID"

    context = {
        "user_context": {
            "dataloaders": dataloader_mock,
            "settings": settings_mock,
            "mapping": mapping,
            "converter": converter_mock,
        }
    }
    payload = MagicMock()
    payload.uuid = uuid4()

    settings = MagicMock()
    settings.ldap_organizational_unit = "OU=foo"
    settings.ldap_search_base = "DC=bar"

    output = await asyncio.gather(
        listen_to_changes_in_employees(context, payload),
    )

    assert output == [None]
