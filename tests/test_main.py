# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
import asyncio
import datetime
import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from fastramqpi.context import Context
from fastramqpi.main import FastRAMQPI
from ramodels.mo.details.address import Address
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import ServiceType
from ramqp.utils import RejectMessage
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.main import create_app
from mo_ldap_import_export.main import create_fastramqpi
from mo_ldap_import_export.main import format_converted_objects
from mo_ldap_import_export.main import listen_to_changes
from mo_ldap_import_export.main import listen_to_changes_in_employees
from mo_ldap_import_export.main import listen_to_changes_in_org_units
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
        "ADMIN_PASSWORD": "admin",
        "AUTHENTICATION_SECRET": "foo",
        "DEFAULT_ORG_UNIT_LEVEL": "foo",
        "DEFAULT_ORG_UNIT_TYPE": "foo",
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
def load_settings_overrides_incorrect_mapping(
    settings_overrides: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings,
       but pointing to a nonexistent mapping file

    Yields:
        Minimal set of overrides.
    """
    overrides = {**settings_overrides, "CONVERSION_MAP": "nonexisting_file"}
    for key, value in overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield overrides


@pytest.fixture
def load_settings_overrides_not_listening(
    settings_overrides: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings,
       but with listen_to_changes equal to False

    Yields:
        Minimal set of overrides.
    """
    overrides = {**settings_overrides, "LISTEN_TO_CHANGES_IN_MO": "False"}
    for key, value in overrides.items():
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield overrides


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
def test_mo_address() -> Address:
    test_mo_address = Address.from_simplified_fields(
        "foo@bar.dk", uuid4(), "2021-01-01"
    )
    return test_mo_address


@pytest.fixture
def test_mo_objects() -> list:
    return [
        {
            "uuid": uuid4(),
            "service_type": ServiceType.EMPLOYEE,
            "payload": PayloadType(
                uuid=uuid4(), object_uuid=uuid4(), time=datetime.datetime.now()
            ),
            "object_type": ObjectType.EMPLOYEE,
            "validity": {
                "from": datetime.datetime.today().strftime("%Y-%m-%d"),
                "to": None,
            },
        },
        {
            "uuid": uuid4(),
            "service_type": ServiceType.EMPLOYEE,
            "payload": PayloadType(
                uuid=uuid4(), object_uuid=uuid4(), time=datetime.datetime.now()
            ),
            "object_type": ObjectType.EMPLOYEE,
            "validity": {
                "from": "2021-01-01",
                "to": datetime.datetime.today().strftime("%Y-%m-%d"),
            },
        },
        {
            "uuid": uuid4(),
            "service_type": ServiceType.EMPLOYEE,
            "payload": PayloadType(
                uuid=uuid4(), object_uuid=uuid4(), time=datetime.datetime.now()
            ),
            "object_type": ObjectType.EMPLOYEE,
            "validity": {
                "from": "2021-01-01",
                "to": "2021-05-01",
            },
        },
    ]


@pytest.fixture
def dataloader(
    sync_dataloader: MagicMock, test_mo_address: Address, test_mo_objects: list
) -> AsyncMock:

    test_ldap_object = LdapObject(
        name="Tester", Department="QA", dn="someDN", EmployeeID="0101012002"
    )
    test_mo_employee = Employee(cpr_no="1212121234")

    test_mo_it_user = ITUser.from_simplified_fields("foo", uuid4(), "2021-01-01")

    load_ldap_cpr_object = MagicMock()
    load_ldap_cpr_object.return_value = test_ldap_object

    dataloader = AsyncMock()
    dataloader.load_ldap_object = sync_dataloader
    dataloader.load_ldap_populated_overview = sync_dataloader
    dataloader.load_ldap_overview = sync_dataloader
    dataloader.load_ldap_cpr_object = load_ldap_cpr_object
    dataloader.load_ldap_objects.return_value = [test_ldap_object] * 3
    dataloader.load_mo_employee.return_value = test_mo_employee
    dataloader.load_mo_address.return_value = test_mo_address
    dataloader.load_mo_it_user.return_value = test_mo_it_user
    dataloader.load_mo_address_types = sync_dataloader
    dataloader.load_mo_it_systems = sync_dataloader
    dataloader.load_mo_primary_types = sync_dataloader
    dataloader.cleanup_attributes_in_ldap = sync_dataloader
    dataloader.load_mo_employee_addresses.return_value = [test_mo_address] * 2
    dataloader.load_all_mo_objects.return_value = test_mo_objects

    return dataloader


@pytest.fixture
def converter() -> MagicMock:
    converter = MagicMock()
    converter.get_accepted_json_keys.return_value = [
        "Employee",
        "Address",
        "EmailEmployee",
    ]
    converter.cpr_field = "EmployeeID"
    return converter


@pytest.fixture
def internal_amqpsystem() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def fastramqpi(
    disable_metrics: None,
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: AsyncMock,
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
    ), patch(
        "mo_ldap_import_export.main.get_attribute_types", return_value={"foo": {}}
    ), patch(
        "mo_ldap_import_export.main.AMQPSystem", return_value=internal_amqpsystem
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


@pytest.fixture
def headers(test_client: TestClient) -> dict:
    response = test_client.post(
        "/login", data={"username": "admin", "password": "admin"}
    )
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    return headers


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


def test_ldap_get_all_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get(
        "/LDAP/Employee", headers=headers, params={"entries_to_return": 20}
    )
    assert response.status_code == 202


def test_ldap_get_all_converted_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/Employee/converted", headers=headers)
    assert response.status_code == 202


def test_ldap_get_converted_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/Employee/foo/converted", headers=headers)
    assert response.status_code == 202


def test_ldap_post_ldap_employee_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get-all endpoint on our app."""

    ldap_person_to_post = {
        "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        "cpr": "0101121234",
        "name": "Lars Peter Thomsen",
        "Department": None,
    }
    response = test_client.post(
        "/LDAP/Employee", json=ldap_person_to_post, headers=headers
    )
    assert response.status_code == 200


def test_mo_get_employee_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the MO get-all endpoint on our app."""

    uuid = uuid4()

    response = test_client.get(f"/MO/Employee/{uuid}", headers=headers)
    assert response.status_code == 202


def test_mo_post_employee_endpoint(test_client: TestClient, headers: dict) -> None:
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

    response = test_client.post("/MO/Employee", json=employee_to_post, headers=headers)
    assert response.status_code == 200


def test_ldap_get_organizationalUser_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/Employee/foo", headers=headers)
    assert response.status_code == 202


async def test_listen_to_changes_in_org_units(converter: MagicMock):

    org_unit_info = {uuid4(): {"name": "Magenta Aps"}}

    dataloader = MagicMock()
    dataloader.load_mo_org_units.return_value = org_unit_info

    payload = MagicMock()
    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    mo_routing_key = MORoutingKey.build("org_unit.org_unit.edit")

    await listen_to_changes_in_org_units(
        context, payload, mo_routing_key=mo_routing_key
    )
    assert converter.org_unit_info == org_unit_info


async def test_listen_to_change_in_org_unit_address(
    dataloader: AsyncMock, load_settings_overrides: dict[str, str], converter: MagicMock
):
    mo_routing_key = MORoutingKey.build("org_unit.address.edit")

    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")
    employee1 = Employee(cpr_no="0101011234")
    employee2 = Employee(cpr_no="0101011235")

    dataloader = MagicMock()

    load_mo_address = AsyncMock()
    load_mo_employees_in_org_unit = AsyncMock()
    load_mo_org_unit_addresses = AsyncMock()
    upload_ldap_object = AsyncMock()

    load_mo_address.return_value = address
    load_mo_employees_in_org_unit.return_value = [employee1, employee2]
    load_mo_org_unit_addresses.return_value = [address]

    dataloader.upload_ldap_object = upload_ldap_object
    dataloader.load_mo_address = load_mo_address
    dataloader.load_mo_employees_in_org_unit = load_mo_employees_in_org_unit
    dataloader.load_mo_org_unit_addresses = load_mo_org_unit_addresses

    converter.find_ldap_object_class.return_value = "user"

    payload = MagicMock()
    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    await listen_to_changes_in_org_units(
        context, payload, mo_routing_key=mo_routing_key
    )

    # Assert that an address was uploaded to two ldap objects.
    assert upload_ldap_object.await_count == 2


async def test_listen_to_change_in_org_unit_address_not_supported(
    dataloader: AsyncMock, load_settings_overrides: dict[str, str], converter: MagicMock
):
    mo_routing_key = MORoutingKey.build("org_unit.address.edit")
    payload = MagicMock()
    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")

    def find_ldap_object_class(json_key):
        d = {"Employee": "user", "LocationUnit": "address"}
        return d[json_key]

    converter.find_ldap_object_class.side_effect = find_ldap_object_class

    load_mo_address = AsyncMock()
    load_mo_address.return_value = address
    dataloader.load_mo_address = load_mo_address

    converter.address_type_info = {
        str(address.address_type.uuid): {"user_key": "LocationUnit"}
    }

    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    with pytest.raises(NotSupportedException):
        await listen_to_changes_in_org_units(
            context, payload, mo_routing_key=mo_routing_key
        )


async def test_listen_to_changes_in_employees(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
) -> None:

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "bar"

    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )

    converter = MagicMock()
    converter.cpr_field = "EmployeeID"
    converted_ldap_object = LdapObject(dn="Foo")
    converter.to_ldap.return_value = converted_ldap_object
    converter.mapping = {"mo_to_ldap": {"EmailEmployee": 2}}
    converter.get_it_system_user_key.return_value = "AD"

    address_type_user_key = "EmailEmployee"
    converter.get_address_type_user_key.return_value = address_type_user_key

    it_system_type_name = "AD"

    context = Context(
        {
            "user_context": {
                "settings": settings_mock,
                "mapping": mapping,
                "converter": converter,
                "dataloader": dataloader,
            }
        }
    )
    payload = MagicMock()
    payload.uuid = uuid4()
    payload.object_uuid = uuid4()

    settings = MagicMock()
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
    converter.from_ldap.return_value = [
        Address.from_simplified_fields("street1", uuid4(), "2021-01-01"),
        Address.from_simplified_fields("street2", uuid4(), "2021-01-01"),
    ]

    mo_routing_key = MORoutingKey.build("employee.address.create")
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.load_mo_address.called
    dataloader.upload_ldap_object.assert_called_with(
        converted_ldap_object, address_type_user_key
    )

    # Simulate a created IT user
    converter.from_ldap.return_value = [
        ITUser.from_simplified_fields("foo", uuid4(), "2021-01-01"),
        ITUser.from_simplified_fields("bar", uuid4(), "2021-01-01"),
    ]

    mo_routing_key = MORoutingKey.build("employee.it.create")
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.load_mo_it_user.called
    dataloader.upload_ldap_object.assert_called_with(
        converted_ldap_object, it_system_type_name
    )

    # Simulate a created engagement
    converter.from_ldap.return_value = [
        Engagement.from_simplified_fields(
            org_unit_uuid=uuid4(),
            person_uuid=uuid4(),
            job_function_uuid=uuid4(),
            engagement_type_uuid=uuid4(),
            user_key="foo",
            from_date="2021-01-01",
        ),
    ]

    mo_routing_key = MORoutingKey.build("employee.engagement.create")
    await asyncio.gather(
        listen_to_changes_in_employees(context, payload, mo_routing_key=mo_routing_key),
    )
    assert dataloader.load_mo_engagement.called
    dataloader.upload_ldap_object.assert_called_with(
        converted_ldap_object, "Engagement"
    )

    # Simulate case where no cleanup is needed
    converter.from_ldap.return_value = [
        Address.from_simplified_fields("foo@bar.dk", uuid4(), "2021-01-01"),
        Address.from_simplified_fields("foo@bar.dk", uuid4(), "2021-01-01"),
    ]

    mo_routing_key = MORoutingKey.build("employee.address.create")
    context = {
        "user_context": {
            "settings": settings_mock,
            "mapping": mapping,
            "converter": converter,
            "dataloader": dataloader,
        }
    }

    with capture_logs() as cap_logs:
        await asyncio.gather(
            listen_to_changes_in_employees(
                context, payload, mo_routing_key=mo_routing_key
            ),
        )

        log_messages = [log for log in cap_logs if log["log_level"] == "info"]
        assert re.match(
            "No synchronization required",
            log_messages[-1]["event"],
        )

    # Simulate an uuid which should be skipped
    # And an uuid which is too old, so it will be removed from the list
    old_uuid = uuid4()
    uuid_which_should_remain = uuid4()

    uuids_to_ignore = {
        # This uuid should be ignored (once)
        payload.object_uuid: [datetime.datetime.now(), datetime.datetime.now()],
        # This uuid has been here for too long, and should be removed
        old_uuid: [datetime.datetime(2020, 1, 1)],
        # This uuid should remain in the list
        uuid_which_should_remain: [datetime.datetime.now()],
    }

    with patch("mo_ldap_import_export.main.uuids_to_ignore", uuids_to_ignore):
        with capture_logs() as cap_logs:
            await asyncio.gather(
                listen_to_changes(context, payload, mo_routing_key=mo_routing_key),
            )

            entries = [w for w in cap_logs if w["log_level"] == "info"]

            assert re.match(
                f"Removing timestamp belonging to {old_uuid} from uuids_to_ignore.",
                entries[0]["event"],
            )
            assert re.match(f".*Ignoring .*{payload.object_uuid}", entries[1]["event"])
            assert len(uuids_to_ignore) == 3
            assert len(uuids_to_ignore[old_uuid]) == 0
            assert len(uuids_to_ignore[uuid_which_should_remain]) == 1
            assert len(uuids_to_ignore[payload.object_uuid]) == 1


def test_ldap_get_overview_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview", headers=headers)
    assert response.status_code == 202


def test_ldap_get_populated_overview_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview/populated", headers=headers)
    assert response.status_code == 202


def test_ldap_get_attribute_details_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview/attribute/foo", headers=headers)
    assert response.status_code == 202


def test_ldap_get_object_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP_overview/object/CN=foo,DC=bar", headers=headers)
    assert response.status_code == 202


async def test_listen_to_changes(load_settings_overrides: dict[str, str]):

    listen_to_changes_in_employees_mock = AsyncMock()
    listen_to_changes_in_org_units_mock = AsyncMock()

    with patch(
        "mo_ldap_import_export.main.listen_to_changes_in_employees",
        listen_to_changes_in_employees_mock,
    ), patch(
        "mo_ldap_import_export.main.listen_to_changes_in_org_units",
        listen_to_changes_in_org_units_mock,
    ):

        context = None
        payload = MagicMock()
        payload.uuid = uuid4()
        payload.object_uuid = uuid4()

        mo_routing_key = MORoutingKey.build("employee.*.*")
        await listen_to_changes(context, payload, mo_routing_key=mo_routing_key)
        listen_to_changes_in_employees_mock.assert_awaited_once()

        mo_routing_key = MORoutingKey.build("org_unit.*.*")
        await listen_to_changes(context, payload, mo_routing_key=mo_routing_key)
        listen_to_changes_in_org_units_mock.assert_awaited_once()


async def test_listen_to_changes_not_supported(
    load_settings_overrides: dict[str, str]
) -> None:

    # Terminating a user is currently not supported
    mo_routing_key = MORoutingKey.build("employee.employee.terminate")
    context: dict = {}
    payload = MagicMock()

    original_function = listen_to_changes.__wrapped__

    # Which means the message should be rejected
    with pytest.raises(NotSupportedException):
        await asyncio.gather(
            original_function(context, payload, mo_routing_key=mo_routing_key),
        )

    with pytest.raises(RejectMessage):
        await asyncio.gather(
            listen_to_changes(context, payload, mo_routing_key=mo_routing_key),
        )


async def test_listen_to_changes_not_listening(
    load_settings_overrides_not_listening: dict[str, str]
) -> None:

    mo_routing_key = MORoutingKey.build("employee.employee.edit")
    context: dict = {}
    payload = MagicMock()

    with pytest.raises(RejectMessage):
        await asyncio.gather(
            listen_to_changes(context, payload, mo_routing_key=mo_routing_key),
        )


def test_ldap_get_all_converted_endpoint_failure(
    test_client: TestClient, converter: MagicMock, headers: dict
) -> None:
    def from_ldap(ldap_object, json_key, employee_uuid=None):
        # This will raise a validationError because the ldap_object is not converted
        return Employee(**ldap_object.dict())

    converter.from_ldap = from_ldap
    with patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
        response1 = test_client.get("/LDAP/Employee/converted", headers=headers)
        response2 = test_client.get("/LDAP/Employee/foo/converted", headers=headers)

    assert response1.status_code == 202
    assert response2.status_code == 404


def test_load_address_from_MO_endpoint(test_client: TestClient, headers: dict):
    uuid = uuid4()
    response = test_client.get(f"/MO/Address/{uuid}", headers=headers)
    assert response.status_code == 202


def test_load_address_types_from_MO_endpoint(test_client: TestClient, headers: dict):
    response = test_client.get("/MO/Address_types", headers=headers)
    assert response.status_code == 202


def test_load_it_systems_from_MO_endpoint(test_client: TestClient, headers: dict):
    response = test_client.get("/MO/IT_systems", headers=headers)
    assert response.status_code == 202


def test_reload_info_dicts_endpoint(test_client: TestClient, headers: dict):
    response = test_client.post("/reload_info_dicts", headers=headers)
    assert response.status_code == 202


def test_load_primary_types_from_MO_endpoint(test_client: TestClient, headers: dict):
    response = test_client.get("/MO/Primary_types", headers=headers)
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP_first_20(
    test_client: TestClient, headers: dict
) -> None:
    response = test_client.get(
        "/Import/all?test_on_first_20_entries=true", headers=headers
    )
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP(
    test_client: TestClient, headers: dict
) -> None:
    response = test_client.get("/Import/all", headers=headers)
    assert response.status_code == 202


async def test_import_single_object_from_LDAP(
    test_client: TestClient, headers: dict
) -> None:
    response = test_client.get("/Import/0101011234", headers=headers)
    assert response.status_code == 202


async def test_import_single_object_from_LDAP_ignore_twice(
    test_client: TestClient, headers: dict, converter: MagicMock
) -> None:
    """
    When an uuid already is in the uuids_to_ignore dict, it should be added once more
    so it is ignored twice.
    """

    uuid = uuid4()
    mo_object_mock = MagicMock
    mo_object_mock.uuid = uuid
    converter.from_ldap.return_value = [mo_object_mock]

    uuids_to_ignore = {uuid: [datetime.datetime.now()]}
    with patch("mo_ldap_import_export.main.uuids_to_ignore", uuids_to_ignore):
        response = test_client.get("/Import/0101011234", headers=headers)
        assert response.status_code == 202
        assert len(uuids_to_ignore[uuid]) == 2


async def test_import_single_object_from_LDAP_non_existing_employee(
    test_client: TestClient, dataloader: AsyncMock, headers: dict
) -> None:
    dataloader.find_mo_employee_uuid.return_value = None
    response = test_client.get("/Import/0101011234", headers=headers)
    assert response.status_code == 202


async def test_import_single_object_from_LDAP_multiple_employees(
    test_client: TestClient, dataloader: AsyncMock, headers: dict
) -> None:
    dataloader.load_ldap_cpr_object.return_value = None
    dataloader.load_ldap_cpr_object.side_effect = MultipleObjectsReturnedException(
        "foo"
    )

    with capture_logs() as cap_logs:
        response = test_client.get("/Import/0101011234", headers=headers)
        warnings = [w for w in cap_logs if w["log_level"] == "warning"]

        assert re.match(
            ".*Could not upload .* object.*",
            warnings[0]["event"],
        )

    assert response.status_code == 202


async def test_import_address_objects(
    test_client: TestClient, converter: MagicMock, dataloader: AsyncMock, headers: dict
):
    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.Address"
    converter.import_mo_object_class.return_value = Address
    converter.get_mo_attributes.return_value = ["value", "uuid", "validity"]

    address_type_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        Address.from_simplified_fields(
            "foo@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        Address.from_simplified_fields(
            "foo2@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        Address.from_simplified_fields(
            "foo3@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    converter.from_ldap.return_value = converted_objects

    with patch(
        "mo_ldap_import_export.main.format_converted_objects",
        return_value=converted_objects,
    ):
        response = test_client.get("/Import/0101011234", headers=headers)
        assert response.status_code == 202

        dataloader.upload_mo_objects.assert_called_with(converted_objects)


async def test_import_it_user_objects(
    test_client: TestClient, converter: MagicMock, dataloader: AsyncMock, headers: dict
):
    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.ITUser"
    converter.import_mo_object_class.return_value = ITUser
    converter.get_mo_attributes.return_value = ["user_key", "validity"]

    it_system_type1_uuid = uuid4()
    it_system_type2_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_type2_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username3", it_system_type2_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    converter.from_ldap.return_value = converted_objects

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
    )

    it_users_in_mo = [it_user_in_mo]

    dataloader.load_mo_employee_it_users.return_value = it_users_in_mo

    response = test_client.get("/Import/0101011234", headers=headers)
    assert response.status_code == 202

    non_existing_converted_objects = [
        converted_objects[1],
        converted_objects[2],
    ]

    dataloader.upload_mo_objects.assert_called_with(non_existing_converted_objects)


async def test_load_mapping_file_environment(
    load_settings_overrides_incorrect_mapping: dict[str, str],
    disable_metrics: None,
    converter: MagicMock,
) -> None:

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=converter
    ), pytest.raises(
        FileNotFoundError
    ):
        fastramqpi = create_fastramqpi()
        assert isinstance(fastramqpi, FastRAMQPI)


async def test_load_faulty_username_generator(
    disable_metrics: None,
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    dataloader: AsyncMock,
    converter: MagicMock,
) -> None:

    usernames_mock = MagicMock()
    usernames_mock.UserNameGenerator.return_value = "foo"

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.construct_gql_client",
        return_value=gql_client,
    ), patch(
        "mo_ldap_import_export.main.DataLoader", return_value=dataloader
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=converter
    ), patch(
        "mo_ldap_import_export.main.usernames", usernames_mock
    ), pytest.raises(
        AttributeError
    ):
        fastramqpi = create_fastramqpi()
        assert isinstance(fastramqpi, FastRAMQPI)


def test_invalid_credentials(test_client: TestClient):
    response = test_client.post(
        "/login", data={"username": "admin", "password": "wrong_password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_invalid_username(test_client: TestClient):
    response = test_client.post(
        "/login", data={"username": "wrong_username", "password": "admin"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement1 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2020-01-01",
    )

    engagement2 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="foo",
        from_date="2021-01-01",
    )

    # We do not expect this one the be uploaded, because its user_key exists twice in MO
    engagement3 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    engagement1_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
    )

    engagement2_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    engagement3_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    dataloader.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
        engagement3_in_mo,
    ]

    user_context = {"converter": converter, "dataloader": dataloader}

    json_key = "Engagement"

    converted_objects = [engagement1, engagement2, engagement3]

    formatted_objects = await format_converted_objects(
        converted_objects, json_key, user_context
    )

    assert len(formatted_objects) == 2
    assert engagement3 not in formatted_objects
    assert formatted_objects[1] == engagement2
    assert formatted_objects[0].uuid == engagement1_in_mo.uuid
    assert formatted_objects[0].user_key == engagement1.user_key


async def test_format_converted_employee_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.find_mo_object_class.return_value = "Employee"
    user_context = {"converter": converter, "dataloader": dataloader}

    employee1 = Employee(cpr_no="1212121234")
    employee2 = Employee(cpr_no="1212121235")

    converted_objects = [employee1, employee2]

    formatted_objects = await format_converted_objects(
        converted_objects, "Employee", user_context
    )

    assert formatted_objects[0] == employee1
    assert formatted_objects[1] == employee2


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}

    person_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", person_uuid=person_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", uuid4(), "2021-01-01", person_uuid=person_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", person_uuid=person_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_employee_addresses.return_value = [address1_in_mo]

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}
    org_unit_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


async def test_format_converted_org_unit_address_objects_identical_to_mo(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}
    org_unit_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    # This one is identical to the one which we are trying to upload
    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[0].value == "bar"
    assert len(formatted_objects) == 1


async def test_format_converted_address_objects_without_person_or_org_unit(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}

    # These addresses have neither an org unit uuid or person uuid. we cannot convert
    # them
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields("foo", address_type_uuid, "2021-01-01")
    address2 = Address.from_simplified_fields("bar", address_type_uuid, "2021-01-01")

    converted_objects = [address1, address2]

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert len(formatted_objects) == 0


async def test_format_converted_primary_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    employee_uuid = uuid4()
    primary_uuid = uuid4()
    engagement1_in_mo_uuid = uuid4()
    engagement2_in_mo_uuid = uuid4()

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    def is_primary(uuid):
        if uuid == engagement1_in_mo_uuid:
            return True
        else:
            return False

    dataloader.is_primary.side_effect = is_primary

    engagement1 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2020-01-01",
    )

    engagement1_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
        primary_uuid=primary_uuid,
        uuid=engagement1_in_mo_uuid,
    )

    # Engagement with the same user key. We should not update this one because it is
    # not primary.
    engagement2_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
        primary_uuid=None,
        uuid=engagement2_in_mo_uuid,
    )

    dataloader.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
    ]

    user_context = {"converter": converter, "dataloader": dataloader}

    json_key = "Engagement"

    converted_objects = [engagement1]

    formatted_objects = await format_converted_objects(
        converted_objects, json_key, user_context
    )

    assert len(formatted_objects) == 1
    assert formatted_objects[0].primary.uuid is not None
    assert formatted_objects[0].user_key == "123"


async def test_synchronize_todays_events(
    test_client: TestClient,
    headers: dict,
    internal_amqpsystem: AsyncMock,
    test_mo_objects: list,
):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    json = {
        "date": today,
        "publish_amqp_messages": True,
    }
    response = test_client.post(
        "/Synchronize_todays_events", headers=headers, json=json
    )
    assert response.status_code == 202

    n = 0
    for mo_object in test_mo_objects:
        payload = jsonable_encoder(mo_object["payload"])

        if str(mo_object["validity"]["from"]).startswith(today):
            routing_key = "employee.employee.refresh"
        elif str(mo_object["validity"]["to"]).startswith(today):
            routing_key = "employee.employee.terminate"
        else:
            routing_key = None

        if routing_key:
            internal_amqpsystem.publish_message.assert_any_await(routing_key, payload)
            n += 1

    assert internal_amqpsystem.publish_message.await_count == n
