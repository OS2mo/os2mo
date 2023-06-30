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
from gql.transport.exceptions import TransportQueryError
from ramodels.mo.details.address import Address
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import RequestType
from ramqp.mo.models import ServiceType
from ramqp.utils import RejectMessage
from ramqp.utils import RequeueMessage
from structlog.testing import capture_logs

from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.main import construct_gql_client
from mo_ldap_import_export.main import create_app
from mo_ldap_import_export.main import create_fastramqpi
from mo_ldap_import_export.main import get_delete_flag
from mo_ldap_import_export.main import listen_to_changes
from mo_ldap_import_export.main import open_ldap_connection
from mo_ldap_import_export.main import reject_on_failure


@pytest.fixture(scope="module")
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
        "LDAP_OUS_TO_SEARCH_IN": '["OU=bar"]',
        "LDAP_OU_FOR_NEW_USERS": "OU=foo,OU=bar",
    }
    yield overrides


@pytest.fixture(scope="module")
def load_settings_overrides(
    settings_overrides: dict[str, str],
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

    mp = pytest.MonkeyPatch()
    for key, value in settings_overrides.items():
        if os.environ.get(key) is None:
            mp.setenv(key, value)
    yield settings_overrides


@pytest.fixture(scope="module")
def test_mo_address() -> Address:
    test_mo_address = Address.from_simplified_fields(
        "foo@bar.dk", uuid4(), "2021-01-01"
    )
    return test_mo_address


@pytest.fixture(scope="module")
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
        {
            "uuid": uuid4(),
            "service_type": ServiceType.EMPLOYEE,
            "payload": PayloadType(
                uuid=uuid4(), object_uuid=uuid4(), time=datetime.datetime.now()
            ),
            "object_type": ObjectType.EMPLOYEE,
            "validity": {
                "from": datetime.datetime.today().strftime("%Y-%m-%d"),
                "to": datetime.datetime.today().strftime("%Y-%m-%d"),
            },
        },
    ]


@pytest.fixture(scope="module")
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
    dataloader.load_mo_employee_address_types = sync_dataloader
    dataloader.load_mo_org_unit_address_types = sync_dataloader
    dataloader.load_mo_it_systems = sync_dataloader
    dataloader.load_mo_primary_types = sync_dataloader
    dataloader.load_mo_employee_addresses.return_value = [test_mo_address] * 2
    dataloader.load_all_mo_objects.return_value = test_mo_objects
    dataloader.load_mo_object.return_value = test_mo_objects[0]
    dataloader.load_ldap_attribute_values = sync_dataloader
    dataloader.modify_ldap_object.return_value = [{"description": "success"}]
    dataloader.get_ldap_objectGUID = sync_dataloader

    return dataloader


@pytest.fixture(scope="module")
def sync_dataloader() -> MagicMock:

    dataloader = MagicMock()
    return dataloader


@pytest.fixture(scope="module")
def converter() -> MagicMock:
    converter = MagicMock()
    converter.get_accepted_json_keys.return_value = [
        "Employee",
        "Address",
        "EmailEmployee",
    ]
    converter.cpr_field = "EmployeeID"
    converter._import_to_mo_ = MagicMock()
    converter._import_to_mo_.return_value = True

    return converter


@pytest.fixture(scope="module")
def disable_metrics() -> Iterator[None]:
    """Fixture to set the ENABLE_METRICS environmental variable to False.

    Yields:
        None
    """
    mp = pytest.MonkeyPatch()
    mp.setenv("ENABLE_METRICS", "False")
    yield


@pytest.fixture(scope="module")
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture(scope="module")
def internal_amqpsystem() -> MagicMock:
    mock = MagicMock()
    mock.publish_message = AsyncMock()
    return mock


@pytest.fixture(scope="module")
def sync_tool() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(scope="module")
def fastramqpi(
    disable_metrics: None,
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: MagicMock,
    sync_tool: AsyncMock,
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
        "mo_ldap_import_export.main.SyncTool", return_value=sync_tool
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=converter
    ), patch(
        "mo_ldap_import_export.main.get_attribute_types", return_value={"foo": {}}
    ), patch(
        "mo_ldap_import_export.main.AMQPSystem", return_value=internal_amqpsystem
    ), patch(
        "mo_ldap_import_export.main.InitEngine", return_value=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.asyncio.get_event_loop", return_value=None
    ):
        yield create_fastramqpi()


@pytest.fixture(scope="module")
def app(fastramqpi: FastRAMQPI) -> Iterator[FastAPI]:
    """Fixture to construct a FastAPI application.

    Yields:
        FastAPI application.
    """
    yield create_app()


@pytest.fixture(scope="module")
def test_client(app: FastAPI) -> Iterator[TestClient]:
    """Fixture to construct a FastAPI test-client.

    Note:
        The app does not do lifecycle management.

    Yields:
        TestClient for the FastAPI application.
    """
    yield TestClient(app)


@pytest.fixture
def test_client_no_cpr(app: FastAPI, converter: MagicMock) -> Iterator[TestClient]:
    """Fixture to construct a FastAPI test-client. where cpr_field = None

    Note:
        The app does not do lifecycle management.

    Yields:
        TestClient for the FastAPI application.
    """
    converter.cpr_field = None
    yield TestClient(create_app())


@pytest.fixture
def ldap_connection() -> Iterator[MagicMock]:
    """Fixture to construct a mock ldap_connection.

    Yields:
        A mock for ldap_connection.
    """
    yield MagicMock()


@pytest.fixture(scope="module")
def headers(test_client: TestClient) -> dict:
    response = test_client.post(
        "/login", data={"username": "admin", "password": "admin"}
    )
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    return headers


def test_create_app(
    fastramqpi: FastRAMQPI,
) -> None:
    """Test that we can construct our FastAPI application."""

    with patch("mo_ldap_import_export.main.create_fastramqpi", return_value=fastramqpi):
        app = create_app()
    assert isinstance(app, FastAPI)


def test_create_fastramqpi(disable_metrics: None, converter: MagicMock) -> None:
    """Test that we can construct our FastRAMQPI system."""

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch("mo_ldap_import_export.main.LdapConverter", return_value=converter), patch(
        "mo_ldap_import_export.dataloaders.DataLoader.get_root_org",
        return_value=uuid4(),
    ), patch(
        "mo_ldap_import_export.main.InitEngine", return_value=MagicMock()
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
    async with open_ldap_connection(ldap_connection):  # type: ignore
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

    response = test_client.get("/LDAP/Employee/010101-1234/converted", headers=headers)
    assert response.status_code == 202

    response = test_client.get("/LDAP/Employee/invalid_cpr/converted", headers=headers)
    assert response.status_code == 422


def test_ldap_post_ldap_employee_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get-all endpoint on our app."""

    ldap_person_to_post = {
        "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        "cpr": "0101121234",
        "givenname": "Lars Peter",
        "surname": "Thomsen",
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

    response = test_client.get("/LDAP/Employee/010101-1234", headers=headers)
    assert response.status_code == 202

    response = test_client.get("/LDAP/Employee/invalid_cpr", headers=headers)
    assert response.status_code == 422


def test_ldap_get_overview_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/overview", headers=headers)
    assert response.status_code == 202


def test_ldap_get_populated_overview_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/overview/populated", headers=headers)
    assert response.status_code == 202


def test_load_unique_attribute_values_from_LDAP_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/attribute/values/foo", headers=headers)
    assert response.status_code == 202


def test_ldap_get_attribute_details_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/attribute/foo", headers=headers)
    assert response.status_code == 202


def test_ldap_get_object_by_objectGUID_endpoint(
    test_client: TestClient, headers: dict
) -> None:
    """Test the LDAP get endpoint on our app."""

    uuid = uuid4()
    params = {"objectGUID": str(uuid)}
    response = test_client.get(
        "/Inspect/object/objectGUID", headers=headers, params=params
    )
    assert response.status_code == 202


def test_ldap_get_object_by_dn_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    params = {"dn": "CN=foo"}
    response = test_client.get("/Inspect/object/dn", headers=headers, params=params)
    assert response.status_code == 202


def test_ldap_get_objectGUID_endpoint(test_client: TestClient, headers: dict) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/objectGUID/CN=foo", headers=headers)
    assert response.status_code == 202


async def test_listen_to_changes(dataloader: AsyncMock, sync_tool: AsyncMock):

    context = {"user_context": {"dataloader": dataloader, "sync_tool": sync_tool}}
    payload = MagicMock()
    payload.uuid = uuid4()
    payload.object_uuid = uuid4()

    mo_routing_key = MORoutingKey.build("employee.*.*")
    await listen_to_changes(context, payload, mo_routing_key=mo_routing_key)
    sync_tool.listen_to_changes_in_employees.assert_awaited_once()

    mo_routing_key = MORoutingKey.build("org_unit.*.*")
    await listen_to_changes(context, payload, mo_routing_key=mo_routing_key)
    sync_tool.listen_to_changes_in_org_units.assert_awaited_once()


async def test_listen_to_changes_not_listening() -> None:

    mp = pytest.MonkeyPatch()
    mp.setenv("LISTEN_TO_CHANGES_IN_MO", "False")

    mo_routing_key = MORoutingKey.build("employee.employee.edit")
    context: dict = {}
    payload = MagicMock()

    with pytest.raises(RejectMessage):
        await asyncio.gather(
            listen_to_changes(context, payload, mo_routing_key=mo_routing_key),
        )
    mp.setenv("LISTEN_TO_CHANGES_IN_MO", "True")


def test_ldap_get_all_converted_endpoint_failure(
    test_client: TestClient, converter: MagicMock, headers: dict
) -> None:
    def from_ldap(ldap_object, json_key, employee_uuid=None):
        # This will raise a validationError (which is what we want to test)
        return Employee(**{"foo": None})

    converter.from_ldap = from_ldap
    with patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
        response1 = test_client.get("/LDAP/Employee/converted", headers=headers)
        response2 = test_client.get(
            "/LDAP/Employee/010101-1234/converted", headers=headers
        )

    assert response1.status_code == 202
    assert response2.status_code == 404


def test_load_address_from_MO_endpoint(test_client: TestClient, headers: dict):
    uuid = uuid4()
    response = test_client.get(f"/MO/Address/{uuid}", headers=headers)
    assert response.status_code == 202


def test_export_single_user_endpoint(test_client: TestClient, headers: dict):
    uuid = uuid4()
    response = test_client.post(f"/Export/{uuid}", headers=headers)
    assert response.status_code == 202


def test_load_address_types_from_MO_endpoint(test_client: TestClient, headers: dict):
    response = test_client.get("/MO/Address_types_employee", headers=headers)
    assert response.status_code == 202
    response = test_client.get("/MO/Address_types_org_unit", headers=headers)
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
    params = {
        "test_on_first_20_entries": True,
        "delay_in_hours": 0,
        "delay_in_minutes": 0,
        "delay_in_seconds": 0.1,
    }
    response = test_client.get("/Import", headers=headers, params=params)
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP(
    test_client: TestClient, headers: dict
) -> None:
    response = test_client.get("/Import", headers=headers)
    assert response.status_code == 202


async def test_import_one_object_from_LDAP(
    test_client: TestClient, headers: dict
) -> None:
    uuid = uuid4()
    response = test_client.get(f"/Import/{uuid}", headers=headers)
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP_no_cpr_field(
    test_client_no_cpr: TestClient,
    headers: dict,
) -> None:
    response = test_client_no_cpr.get("/Import", headers=headers)
    assert response.status_code == 404


async def test_import_all_objects_from_LDAP_invalid_cpr(
    test_client: TestClient, headers: dict, dataloader: AsyncMock
) -> None:
    dataloader.load_ldap_objects.return_value = [
        LdapObject(name="Tester", Department="QA", dn="someDN", EmployeeID="5001012002")
    ]

    with capture_logs() as cap_logs:
        response = test_client.get("/Import", headers=headers)
        assert response.status_code == 202

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            ".*not a valid cpr number",
            str(messages),
        )


async def test_load_mapping_file_environment() -> None:

    mp = pytest.MonkeyPatch()
    mp.setenv("CONVERSION_MAP", "nonexisting_file")

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=MagicMock()
    ), pytest.raises(
        FileNotFoundError
    ):
        fastramqpi = create_fastramqpi()
        assert isinstance(fastramqpi, FastRAMQPI)

    mp.setenv("CONVERSION_MAP", "")


async def test_incorrect_ous_to_search_in() -> None:

    mp = pytest.MonkeyPatch()
    overrides = {
        "LDAP_OUS_TO_SEARCH_IN": '["OU=bar"]',
        "LDAP_OU_FOR_NEW_USERS": "OU=foo,",
    }
    for key, value in overrides.items():
        mp.setenv(key, value)

    with pytest.raises(ValueError):
        create_fastramqpi()

    overrides = {
        "LDAP_OUS_TO_SEARCH_IN": '["OU=bar"]',
        "LDAP_OU_FOR_NEW_USERS": "OU=foo,OU=bar",
    }
    for key, value in overrides.items():
        mp.setenv(key, value)


async def test_load_faulty_username_generator() -> None:

    usernames_mock = MagicMock()
    usernames_mock.UserNameGenerator.return_value = "foo"

    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.construct_gql_client",
        return_value=MagicMock(),
    ), patch(
        "mo_ldap_import_export.main.DataLoader", return_value=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.LdapConverter", return_value=MagicMock()
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


async def test_synchronize_todays_events(
    test_client: TestClient,
    headers: dict,
    internal_amqpsystem: MagicMock,
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

        from_date = str(mo_object["validity"]["from"])
        to_date = str(mo_object["validity"]["to"])

        if from_date.startswith(today):
            if to_date.startswith(today):
                routing_key = "employee.employee.terminate"
            else:
                routing_key = "employee.employee.refresh"
        elif to_date.startswith(today):
            routing_key = "employee.employee.terminate"
        else:
            routing_key = None

        if routing_key:
            internal_amqpsystem.publish_message.assert_any_await(routing_key, payload)
            n += 1

    assert internal_amqpsystem.publish_message.await_count == n

    # Test that terminations are published before refreshes
    refreshes = 0
    terminations = 0
    for call in internal_amqpsystem.publish_message.mock_calls:
        if "terminate" in call.args[0]:
            terminations += 1
            assert refreshes == 0
        else:
            refreshes += 1


async def test_export_endpoint(
    test_client: TestClient,
    headers: dict,
    internal_amqpsystem: MagicMock,
    test_mo_objects: list,
):

    params: dict = {
        "publish_amqp_messages": True,
        "uuid": str(uuid4()),
        "delay_in_hours": 0,
        "delay_in_minutes": 0,
        "delay_in_seconds": 0.1,
    }

    current_awaits = internal_amqpsystem.publish_message.await_count

    response = test_client.post("/Export", headers=headers, params=params)
    assert response.status_code == 202

    for mo_object in test_mo_objects:
        payload = jsonable_encoder(mo_object["payload"])
        internal_amqpsystem.publish_message.assert_any_await(
            "employee.employee.refresh", payload
        )

    assert (
        internal_amqpsystem.publish_message.await_count
        == len(test_mo_objects) + current_awaits
    )


async def test_reject_on_failure():
    async def not_supported_func():
        raise NotSupportedException("")

    async def incorrect_mapping_func():
        raise IncorrectMapping("")

    async def transport_query_error_func():
        raise TransportQueryError("")

    async def no_objects_returned_func():
        raise NoObjectsReturnedException("")

    async def type_error_func():
        raise TypeError("")

    async def requeue_error_func():
        raise RequeueMessage("")

    # These exceptions should result in rejectMessage exceptions()
    for func in [
        not_supported_func,
        incorrect_mapping_func,
        transport_query_error_func,
        no_objects_returned_func,
    ]:
        with pytest.raises(RejectMessage):
            await reject_on_failure(func)()

    # But not this one
    with patch("mo_ldap_import_export.main.delay_on_error", 0.1):
        with pytest.raises(TypeError):
            await reject_on_failure(type_error_func)()

    # And not this one either
    with patch("mo_ldap_import_export.main.delay_on_requeue", 0.1):
        with pytest.raises(RequeueMessage):
            await reject_on_failure(requeue_error_func)()


async def test_get_delete_flag(dataloader: AsyncMock):

    payload = PayloadType(
        uuid=uuid4(),
        object_uuid=uuid4(),
        time=datetime.datetime.now(),
    )

    # When the routing key != TERMINATE, do not delete anything
    routing_key = MORoutingKey.build(
        service_type=ServiceType.EMPLOYEE,
        object_type=ObjectType.EMPLOYEE,
        request_type=RequestType.REFRESH,
    )
    dataloader.load_mo_object.return_value = None
    context = Context({"user_context": {"dataloader": dataloader}})
    flag = await asyncio.gather(get_delete_flag(routing_key, payload, context))
    assert flag == [False]

    # When there are no matching objects in MO any longer, delete
    routing_key = MORoutingKey.build(
        service_type=ServiceType.EMPLOYEE,
        object_type=ObjectType.EMPLOYEE,
        request_type=RequestType.TERMINATE,
    )
    dataloader.load_mo_object.return_value = None
    context = Context({"user_context": {"dataloader": dataloader}})
    flag = await asyncio.gather(get_delete_flag(routing_key, payload, context))
    assert flag == [True]

    # When there are matching objects in MO, but the to-date is today, delete
    dataloader.load_mo_object.return_value = {
        "validity": {"to": datetime.datetime.today().strftime("%Y-%m-%d")}
    }

    context = Context({"user_context": {"dataloader": dataloader}})
    flag = await asyncio.gather(get_delete_flag(routing_key, payload, context))
    assert flag == [True]

    # When there are matching objects in MO, but the to-date is not today, abort
    dataloader.load_mo_object.return_value = {"validity": {"to": "2200-01-01"}}
    context = Context({"user_context": {"dataloader": dataloader}})
    with pytest.raises(RejectMessage):
        await asyncio.gather(get_delete_flag(routing_key, payload, context))


def test_get_invalid_cpr_numbers_from_LDAP_endpoint(
    test_client: TestClient,
    headers: dict,
    dataloader: AsyncMock,
):
    valid_object = LdapObject(dn="foo", EmployeeID="0101011234")
    invalid_object = LdapObject(dn="bar", EmployeeID="ja")
    dataloader.load_ldap_objects.return_value = [valid_object, invalid_object]
    response = test_client.get("/Inspect/invalid_cpr_numbers", headers=headers)
    assert response.status_code == 202
    result = response.json()
    assert "bar" in result
    assert result["bar"] == "ja"


def test_get_invalid_cpr_numbers_from_LDAP_endpoint_no_cpr_field(
    test_client_no_cpr: TestClient,
    headers: dict,
):
    response = test_client_no_cpr.get("/Inspect/invalid_cpr_numbers", headers=headers)
    assert response.status_code == 404


def test_wraps():
    """
    Test that the decorated listen_to_changes function keeps its name
    """
    assert listen_to_changes.__name__ == "listen_to_changes"


def test_get_duplicate_cpr_numbers_from_LDAP_endpoint_no_cpr_field(
    test_client_no_cpr: TestClient, headers: dict
):
    response = test_client_no_cpr.get("/Inspect/duplicate_cpr_numbers", headers=headers)
    assert response.status_code == 404


def test_get_duplicate_cpr_numbers_from_LDAP_endpoint(
    test_client: TestClient, headers: dict
):

    searchResponse = [
        {"dn": "foo", "attributes": {"EmployeeID": "12"}},
        {"dn": "mucki", "attributes": {"EmployeeID": "123"}},
        {"dn": "bar", "attributes": {"EmployeeID": "123"}},
    ]

    with patch("mo_ldap_import_export.main.paged_search", return_value=searchResponse):

        response = test_client.get("/Inspect/duplicate_cpr_numbers", headers=headers)
        assert response.status_code == 202
        result = response.json()
        assert "123" in result
        assert "mucki" in result["123"]
        assert "bar" in result["123"]


def test_construct_gql_client():

    settings = MagicMock(mo_url="mo-url")

    with patch("mo_ldap_import_export.main.PersistentGraphQLClient", MagicMock):
        gql_client = construct_gql_client(settings)
        gql_client_sync = construct_gql_client(settings, sync=True)

        assert gql_client.sync is False
        assert gql_client_sync.sync is True

        for client in [gql_client, gql_client_sync]:
            assert client.url == "mo-url/graphql/v3"
