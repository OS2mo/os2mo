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
from ramodels.mo.details.address import Address
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from ramqp.utils import RejectMessage

from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.main import create_app
from mo_ldap_import_export.main import create_fastramqpi
from mo_ldap_import_export.main import listen_to_changes_in_employees
from mo_ldap_import_export.main import open_ldap_connection


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
def sync_dataloader() -> MagicMock:

    dataloader = MagicMock()
    return dataloader


@pytest.fixture
def dataloader(sync_dataloader: MagicMock) -> AsyncMock:

    test_ldap_object = LdapObject(
        name="Tester", Department="QA", dn="someDN", cpr="0101012002"
    )
    test_mo_employee = Employee(cpr_no="1212121234")
    test_mo_address = Address.from_simplified_fields(
        "foo@bar.dk", uuid4(), "2021-01-01"
    )

    dataloader = AsyncMock()
    dataloader.load_ldap_populated_overview = sync_dataloader
    dataloader.load_ldap_overview = sync_dataloader
    dataloader.load_ldap_cpr_object.return_value = test_ldap_object
    dataloader.load_ldap_objects.return_value = [test_ldap_object] * 3
    dataloader.load_mo_employee.return_value = test_mo_employee
    dataloader.load_mo_address.return_value = (
        test_mo_address,
        {"address_type_name": "Email"},
    )
    dataloader.load_mo_address_types = sync_dataloader
    dataloader.load_mo_employee_addresses.return_value = [
        (test_mo_address, {"address_type_name": "Email"})
    ] * 2

    return dataloader


@pytest.fixture
def converter() -> MagicMock:
    converter = MagicMock()
    converter.get_accepted_json_keys.return_value = ["Employee", "Address", "Email"]
    converter.cpr_field = "EmployeeID"
    return converter


@pytest.fixture
def fastramqpi(
    disable_metrics: None,
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    dataloader: AsyncMock,
    converter: MagicMock,
) -> Iterator[FastRAMQPI]:
    """Fixture to construct a FastRAMQPI system.

    Yields:
        FastRAMQPI system.
    """
    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.construct_gql_client",
        return_value=gql_client,
    ), patch(
        "mo_ldap_import_export.main.DataLoader", return_value=dataloader
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=converter
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
    fastramqpi: FastRAMQPI,
    load_settings_overrides: dict[str, str],
) -> None:
    """Test that we can construct our FastAPI application."""

    with patch("mo_ldap_import_export.main.create_fastramqpi", return_value=fastramqpi):
        app = create_app()
    assert isinstance(app, FastAPI)


def test_create_fastramqpi(
    load_settings_overrides: dict[str, str], disable_metrics: None, converter: MagicMock
) -> None:
    """Test that we can construct our FastRAMQPI system."""

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
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


def test_ldap_get_all_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/Employee")
    assert response.status_code == 202


def test_ldap_get_all_converted_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/Employee/converted")
    assert response.status_code == 202


def test_ldap_get_converted_endpoint(
    test_client: TestClient,
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/Employee/foo/converted")
    assert response.status_code == 202


def test_ldap_post_ldap_employee_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    ldap_person_to_post = {
        "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        "cpr": "0101121234",
        "name": "Lars Peter Thomsen",
        "Department": None,
    }
    response = test_client.post("/LDAP/Employee", json=ldap_person_to_post)
    assert response.status_code == 200


def test_mo_get_employee_endpoint(test_client: TestClient) -> None:
    """Test the MO get-all endpoint on our app."""

    uuid = uuid4()

    response = test_client.get(f"/MO/Employee/{uuid}")
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

    response = test_client.post("/MO/Employee", json=employee_to_post)
    assert response.status_code == 200


def test_ldap_get_organizationalUser_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/Employee/foo")
    assert response.status_code == 202


async def test_listen_to_changes_in_employees(dataloader: AsyncMock) -> None:

    settings_mock = MagicMock()
    settings_mock.ldap_organizational_unit = "foo"
    settings_mock.ldap_search_base = "bar"

    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )

    converter = MagicMock()
    converter.cpr_field = "EmployeeID"
    converted_ldap_object = LdapObject(dn="Foo")
    converter.to_ldap.return_value = converted_ldap_object
    converter.mapping = {"mo_to_ldap": {"Email": 2}}

    converter.from_ldap.return_value = [
        LdapObject(dn="foo", value="street 1"),
        LdapObject(dn="bar", value="street 2"),
    ]

    address_type_name = "Email"

    context = {
        "user_context": {
            "settings": settings_mock,
            "mapping": mapping,
            "converter": converter,
            "dataloader": dataloader,
        }
    }
    payload = MagicMock()
    payload.uuid = uuid4()

    settings = MagicMock()
    settings.ldap_organizational_unit = "OU=foo"
    settings.ldap_search_base = "DC=bar"

    # Simulate a created employee
    mo_routing_key = MORoutingKey.build("employee.employee.create")
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.load_mo_employee.called
    assert converter.to_ldap.called
    assert dataloader.upload_ldap_object.called
    dataloader.upload_ldap_object.assert_called_with(
        converted_ldap_object, "Employee", overwrite=True
    )
    assert not dataloader.load_mo_address.called

    # Simulate a created address
    mo_routing_key = MORoutingKey.build("employee.address.create")
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.load_mo_address.called
    dataloader.upload_ldap_object.assert_called_with(
        converted_ldap_object, address_type_name
    )

    # Simulate case where no cleanup is needed
    converter.from_ldap.return_value = [
        LdapObject(dn="foo", value="foo@bar.dk"),
        LdapObject(dn="bar", value="foo@bar.dk"),
    ]

    context = {
        "user_context": {
            "settings": settings_mock,
            "mapping": mapping,
            "converter": converter,
            "dataloader": dataloader,
        }
    }
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.cleanup_attributes_in_ldap.called_with([], "Email")


def test_ldap_get_overview_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview")
    assert response.status_code == 202


def test_ldap_get_populated_overview_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview/populated")
    assert response.status_code == 202


async def test_listen_to_changes_in_employees_not_supported() -> None:

    # Terminating a user is currently not supported
    mo_routing_key = MORoutingKey.build("employee.employee.terminate")
    context: dict = {}
    payload = None

    # Which means the message should be rejected
    with pytest.raises(RejectMessage):
        await asyncio.gather(
            listen_to_changes_in_employees(
                context, payload, mo_routing_key=mo_routing_key
            ),
        )


def test_ldap_get_all_converted_endpoint_failure(
    test_client: TestClient, converter: MagicMock
) -> None:
    def from_ldap(ldap_object, json_key):
        # This will raise a validationError because the ldap_object is not converted
        return Employee(**ldap_object.dict())

    converter.from_ldap = from_ldap
    with patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
        response1 = test_client.get("/LDAP/Employee/converted")
        response2 = test_client.get("/LDAP/Employee/foo/converted")

    assert response1.status_code == 202
    assert response2.status_code == 404


def test_load_address_from_MO_endpoint(test_client: TestClient):
    uuid = uuid4()
    response = test_client.get(f"/MO/Address/{uuid}")
    assert response.status_code == 202


def test_load_address_types_from_MO_endpoint(test_client: TestClient):
    response = test_client.get("/MO/Address_types")
    assert response.status_code == 202
