# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
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
from fastapi.testclient import TestClient
from fastramqpi.main import FastRAMQPI
from gql.transport.exceptions import TransportQueryError
from ramodels.mo.details.address import Address
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
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
from mo_ldap_import_export.main import initialize_converters
from mo_ldap_import_export.main import initialize_export_checks
from mo_ldap_import_export.main import initialize_init_engine
from mo_ldap_import_export.main import initialize_sync_tool
from mo_ldap_import_export.main import open_ldap_connection
from mo_ldap_import_export.main import process_address
from mo_ldap_import_export.main import process_engagement
from mo_ldap_import_export.main import process_ituser
from mo_ldap_import_export.main import process_org_unit
from mo_ldap_import_export.main import process_person
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
        "DEFAULT_ORG_UNIT_LEVEL": "foo",
        "DEFAULT_ORG_UNIT_TYPE": "foo",
        "LDAP_OUS_TO_SEARCH_IN": '["OU=bar"]',
        "LDAP_OU_FOR_NEW_USERS": "OU=foo,OU=bar",
        "FASTRAMQPI__AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
        "INTERNAL_AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
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
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": datetime.datetime.today().strftime("%Y-%m-%d"),
                "to": None,
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": "2021-01-01",
                "to": datetime.datetime.today().strftime("%Y-%m-%d"),
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": "2021-01-01",
                "to": "2021-05-01",
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
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
    dataloader.get_ldap_it_system_uuid = sync_dataloader
    dataloader.supported_object_types = ["address", "person"]

    return dataloader


@pytest.fixture(scope="module")
def sync_dataloader() -> MagicMock:

    dataloader = MagicMock()
    return dataloader


@pytest.fixture(scope="module")
def converter() -> MagicMock:
    converter = MagicMock()
    converter.get_mo_to_ldap_json_keys.return_value = [
        "Employee",
        "Address",
        "EmailEmployee",
    ]
    converter.cpr_field = "EmployeeID"
    converter.ldap_it_system = "ADGUID"
    converter._import_to_mo_ = MagicMock()
    converter._import_to_mo_.return_value = True

    converter.to_ldap = AsyncMock()
    converter.from_ldap = AsyncMock()
    converter.from_ldap.return_value = Employee(name="Angus")

    converter.load_info_dicts = AsyncMock()
    converter._init = AsyncMock()

    return converter


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
def patch_modules(
    load_settings_overrides: dict[str, str],
    gql_client: AsyncMock,
    dataloader: AsyncMock,
    internal_amqpsystem: MagicMock,
    sync_tool: AsyncMock,
) -> Iterator[None]:
    """
    Fixture to patch modules needed in main.py
    """
    with patch(
        "mo_ldap_import_export.main.configure_ldap_connection", new_callable=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.construct_gql_client",
        return_value=gql_client,
    ), patch(
        "mo_ldap_import_export.main.DataLoader", return_value=dataloader
    ), patch(
        "mo_ldap_import_export.main.get_attribute_types", return_value={"foo": {}}
    ), patch(
        "mo_ldap_import_export.main.AMQPSystem", return_value=internal_amqpsystem
    ), patch(
        "mo_ldap_import_export.main.InitEngine", return_value=MagicMock()
    ), patch(
        "mo_ldap_import_export.main.asyncio.get_event_loop", return_value=None
    ):
        yield


@pytest.fixture(scope="module")
def fastramqpi(
    patch_modules: None,
    sync_tool: AsyncMock,
    converter: MagicMock,
) -> FastRAMQPI:
    fastramqpi = create_fastramqpi()
    fastramqpi.add_context(sync_tool=sync_tool)
    fastramqpi.add_context(converter=converter)
    fastramqpi.add_context(cpr_field=converter.cpr_field)
    fastramqpi.add_context(ldap_it_system_user_key=converter.ldap_it_system)

    return fastramqpi


@pytest.fixture(scope="module")
def app(fastramqpi: FastRAMQPI) -> Iterator[FastAPI]:
    """Fixture to construct a FastAPI application.

    Yields:
        FastAPI application.
    """
    with patch("mo_ldap_import_export.main.create_fastramqpi", return_value=fastramqpi):
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


# Note: The modules patched by this test are used by all other tests
def test_create_fastramqpi(patch_modules: None) -> None:
    """Test that we can construct our FastRAMQPI system."""
    fastramqpi = create_fastramqpi()
    assert isinstance(fastramqpi, FastRAMQPI)


def test_create_app() -> None:
    """Test that we can construct our FastAPI application."""
    app = create_app()
    assert isinstance(app, FastAPI)


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


def test_ldap_get_all_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/Employee", params={"entries_to_return": 20})
    assert response.status_code == 202


def test_ldap_get_all_converted_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    response = test_client.get("/LDAP/Employee/converted")
    assert response.status_code == 202


def test_ldap_get_converted_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/LDAP/Employee/010101-1234/converted")
    assert response.status_code == 202

    response = test_client.get("/LDAP/Employee/invalid_cpr/converted")
    assert response.status_code == 422


def test_ldap_post_ldap_employee_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get-all endpoint on our app."""

    ldap_person_to_post = {
        "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        "cpr": "0101121234",
        "givenname": "Lars Peter",
        "surname": "Thomsen",
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

    response = test_client.get("/LDAP/Employee/010101-1234")
    assert response.status_code == 202

    response = test_client.get("/LDAP/Employee/invalid_cpr")
    assert response.status_code == 422


def test_ldap_get_overview_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/overview")
    assert response.status_code == 202


def test_ldap_get_populated_overview_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/overview/populated")
    assert response.status_code == 202


def test_load_unique_attribute_values_from_LDAP_endpoint(
    test_client: TestClient,
) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/attribute/values/foo")
    assert response.status_code == 202


def test_ldap_get_attribute_details_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/Inspect/attribute/foo")
    assert response.status_code == 202


def test_ldap_get_object_by_objectGUID_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    uuid = uuid4()
    params = {"objectGUID": str(uuid)}
    response = test_client.get("/Inspect/object/objectGUID", params=params)
    assert response.status_code == 202


def test_ldap_get_object_by_dn_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    params = {"dn": "CN=foo"}
    response = test_client.get("/Inspect/object/dn", params=params)
    assert response.status_code == 202


def test_ldap_get_objectGUID_endpoint(test_client: TestClient) -> None:
    """Test the LDAP get endpoint on our app."""

    response = test_client.get("/objectGUID/CN=foo")
    assert response.status_code == 202


async def test_listen_to_changes(dataloader: AsyncMock, sync_tool: AsyncMock):

    context = {"user_context": {"dataloader": dataloader, "sync_tool": sync_tool}}
    payload = uuid4()

    dataloader.load_mo_object.return_value = {
        "service_type": "employee",
        "validity": {"to": None},
        "parent_uuid": uuid4(),
    }

    await process_address(context, payload, "address", _=None)
    sync_tool.listen_to_changes_in_employees.assert_awaited_once()

    dataloader.load_mo_object.return_value = {
        "service_type": "org_unit",
        "validity": {"to": None},
        "parent_uuid": uuid4(),
    }

    sync_tool.reset_mock()
    await process_address(context, payload, "address", _=None)
    sync_tool.listen_to_changes_in_org_units.assert_awaited_once()

    sync_tool.reset_mock()
    await process_engagement(context, payload, "engagement", _=None)
    sync_tool.listen_to_changes_in_employees.assert_awaited_once()
    sync_tool.export_org_unit_addresses_on_engagement_change.assert_awaited_once()

    sync_tool.reset_mock()
    await process_ituser(context, payload, "ituser", _=None)
    sync_tool.listen_to_changes_in_employees.assert_awaited_once()

    sync_tool.reset_mock()
    await process_person(context, payload, "person", _=None)
    sync_tool.listen_to_changes_in_employees.assert_awaited_once()

    sync_tool.reset_mock()
    await process_org_unit(context, payload, "org_unit", _=None)
    sync_tool.listen_to_changes_in_org_units.assert_awaited_once()


async def test_listen_to_changes_not_listening() -> None:

    mp = pytest.MonkeyPatch()
    mp.setenv("LISTEN_TO_CHANGES_IN_MO", "False")

    mo_routing_key = "person"
    context: dict = {}
    payload = uuid4()

    with pytest.raises(RejectMessage):
        await process_person(context, payload, mo_routing_key, _=None)
    mp.setenv("LISTEN_TO_CHANGES_IN_MO", "True")


def test_ldap_get_all_converted_endpoint_failure(
    test_client: TestClient,
    converter: MagicMock,
) -> None:
    async def from_ldap(ldap_object, json_key, employee_uuid=None):
        # This will raise a validationError (which is what we want to test)
        return Employee(**{"foo": None})

    converter.from_ldap = from_ldap
    with patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
        response1 = test_client.get("/LDAP/Employee/converted")
        response2 = test_client.get("/LDAP/Employee/010101-1234/converted")

    assert response1.status_code == 202
    assert response2.status_code == 404


def test_load_address_from_MO_endpoint(test_client: TestClient):
    uuid = uuid4()
    response = test_client.get(f"/MO/Address/{uuid}")
    assert response.status_code == 202


def test_export_single_user_endpoint(test_client: TestClient):
    uuid = uuid4()
    response = test_client.post(f"/Export/{uuid}")
    assert response.status_code == 202


def test_load_address_types_from_MO_endpoint(test_client: TestClient):
    response = test_client.get("/MO/Address_types_employee")
    assert response.status_code == 202
    response = test_client.get("/MO/Address_types_org_unit")
    assert response.status_code == 202


def test_load_it_systems_from_MO_endpoint(test_client: TestClient):
    response = test_client.get("/MO/IT_systems")
    assert response.status_code == 202


def test_reload_info_dicts_endpoint(test_client: TestClient):
    response = test_client.post("/reload_info_dicts")
    assert response.status_code == 202


def test_load_primary_types_from_MO_endpoint(test_client: TestClient):
    response = test_client.get("/MO/Primary_types")
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP_first_20(test_client: TestClient) -> None:
    params = {
        "test_on_first_20_entries": True,
        "delay_in_hours": 0,
        "delay_in_minutes": 0,
        "delay_in_seconds": 0.1,
    }
    response = test_client.get("/Import", params=params)
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP(test_client: TestClient) -> None:
    response = test_client.get("/Import")
    assert response.status_code == 202


async def test_import_one_object_from_LDAP(test_client: TestClient) -> None:
    uuid = uuid4()
    response = test_client.get(f"/Import/{uuid}")
    assert response.status_code == 202


async def test_import_all_objects_from_LDAP_no_cpr_field(
    test_client: TestClient, converter: MagicMock
) -> None:
    converter.cpr_field = None
    response = test_client.get("/Import?cpr_indexed_entries_only=True")
    assert response.status_code == 404
    converter.cpr_field = "EmployeeID"


async def test_import_all_objects_from_LDAP_invalid_cpr(
    test_client: TestClient, dataloader: AsyncMock
) -> None:
    dataloader.load_ldap_objects.return_value = [
        LdapObject(name="Tester", Department="QA", dn="someDN", EmployeeID="5001012002")
    ]

    with capture_logs() as cap_logs:
        response = test_client.get("/Import")
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
    ):
        with pytest.raises(AttributeError):
            usernames_mock.UserNameGenerator.return_value = "foo"
            create_fastramqpi()

        with pytest.raises(TypeError):
            mock = MagicMock()
            mock.generate_dn = lambda a: a
            usernames_mock.UserNameGenerator.return_value = mock
            create_fastramqpi()


async def test_synchronize_todays_events(
    test_client: TestClient,
    internal_amqpsystem: MagicMock,
    test_mo_objects: list,
):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    json = {
        "date": today,
        "publish_amqp_messages": True,
    }
    response = test_client.post("/Synchronize_todays_events", json=json)
    assert response.status_code == 202

    n = 0
    for mo_object in test_mo_objects:
        payload = mo_object["payload"]

        from_date = str(mo_object["validity"]["from"])
        to_date = str(mo_object["validity"]["to"])

        if from_date.startswith(today):
            routing_key = "person"
        elif to_date.startswith(today):
            routing_key = "person"
        else:
            routing_key = None

        if routing_key:
            internal_amqpsystem.publish_message.assert_any_await(routing_key, payload)
            n += 1

    assert internal_amqpsystem.publish_message.await_count == n


async def test_export_endpoint(
    test_client: TestClient,
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

    response = test_client.post("/Export", params=params)
    assert response.status_code == 202

    for mo_object in test_mo_objects:
        payload = mo_object["payload"]
        internal_amqpsystem.publish_message.assert_any_await("person", payload)

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
    with patch("mo_ldap_import_export.main.delay_on_requeue", 0.1):
        t1 = datetime.datetime.now()
        with pytest.raises(RequeueMessage):
            await reject_on_failure(requeue_error_func)()
        t2 = datetime.datetime.now()
        assert (t2 - t1).total_seconds() >= 0.1


async def test_get_delete_flag(dataloader: AsyncMock):

    # When there are matching objects in MO, but the to-date is today, delete
    mo_object = {"validity": {"to": datetime.datetime.today().strftime("%Y-%m-%d")}}

    flag = get_delete_flag(mo_object)
    assert flag is True

    # When there are matching objects in MO, but the to-date is tomorrow, do not delete
    mo_object = {
        "validity": {
            "to": (datetime.datetime.today() + datetime.timedelta(1)).strftime(
                "%Y-%m-%d"
            )
        }
    }

    flag = get_delete_flag(mo_object)
    assert flag is False


def test_get_invalid_cpr_numbers_from_LDAP_endpoint(
    test_client: TestClient,
    dataloader: AsyncMock,
):
    valid_object = LdapObject(dn="foo", EmployeeID="0101011234")
    invalid_object = LdapObject(dn="bar", EmployeeID="ja")
    dataloader.load_ldap_objects.return_value = [valid_object, invalid_object]
    response = test_client.get("/Inspect/invalid_cpr_numbers")
    assert response.status_code == 202
    result = response.json()
    assert "bar" in result
    assert result["bar"] == "ja"


def test_get_invalid_cpr_numbers_from_LDAP_endpoint_no_cpr_field(
    test_client: TestClient, converter: MagicMock
):
    converter.cpr_field = None
    response = test_client.get("/Inspect/invalid_cpr_numbers")
    assert response.status_code == 404
    converter.cpr_field = "EmployeeID"


def test_wraps():
    """
    Test that the decorated listen_to_changes function keeps its name
    """
    assert process_address.__name__ == "process_address"
    assert process_engagement.__name__ == "process_engagement"
    assert process_ituser.__name__ == "process_ituser"
    assert process_person.__name__ == "process_person"
    assert process_org_unit.__name__ == "process_org_unit"


def test_get_duplicate_cpr_numbers_from_LDAP_endpoint_no_cpr_field(
    test_client: TestClient, converter: MagicMock
):
    converter.cpr_field = None
    response = test_client.get("/Inspect/duplicate_cpr_numbers")
    assert response.status_code == 404
    converter.cpr_field = "EmployeeID"


def test_get_duplicate_cpr_numbers_from_LDAP_endpoint(
    test_client: TestClient,
):

    searchResponse = [
        {"dn": "foo", "attributes": {"EmployeeID": "12"}},
        {"dn": "mucki", "attributes": {"EmployeeID": "123"}},
        {"dn": "bar", "attributes": {"EmployeeID": "123"}},
    ]

    with patch("mo_ldap_import_export.main.paged_search", return_value=searchResponse):

        response = test_client.get("/Inspect/duplicate_cpr_numbers")
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
            assert client.url == "mo-url/graphql/v7"


async def test_get_non_existing_objectGUIDs_from_MO(
    dataloader: AsyncMock,
    test_client: TestClient,
) -> None:
    it_users = [
        {"employee_uuid": str(uuid4()), "user_key": str(uuid4())},
        {"employee_uuid": str(uuid4()), "user_key": str(uuid4())},
        {"employee_uuid": str(uuid4()), "user_key": "foo"},
    ]
    dataloader.load_all_current_it_users.return_value = it_users
    dataloader.load_ldap_attribute_values.return_value = [
        it_users[0]["user_key"],
        str(uuid4()),
    ]
    employee = Employee(givenname="Jim", surname="")
    dataloader.load_mo_employee.return_value = employee

    response = test_client.get("/Inspect/non_existing_objectGUIDs")
    assert response.status_code == 202

    result = response.json()
    assert len(result) == 2
    assert result[0]["MO employee uuid"] == str(employee.uuid)
    assert result[0]["name"] == "Jim"
    assert result[0]["objectGUID in MO"] == it_users[1]["user_key"]
    assert result[1]["objectGUID in MO"] == it_users[2]["user_key"]


async def test_get_non_existing_objectGUIDs_from_MO_404(
    dataloader: AsyncMock,
    test_client: TestClient,
) -> None:
    dataloader.get_ldap_it_system_uuid.return_value = None
    response = test_client.get("/Inspect/non_existing_objectGUIDs")
    assert response.status_code == 404


async def test_initialize_sync_tool(
    fastramqpi: FastRAMQPI, sync_tool: AsyncMock
) -> None:
    fastramqpi._context["user_context"].pop("sync_tool")

    user_context = fastramqpi.get_context()["user_context"]
    assert user_context.get("sync_tool") is None

    with patch("mo_ldap_import_export.main.SyncTool", return_value=sync_tool):
        async with initialize_sync_tool(fastramqpi):
            assert user_context.get("sync_tool") is not None


async def test_initialize_export_checks(fastramqpi: FastRAMQPI) -> None:
    user_context = fastramqpi.get_context()["user_context"]
    assert user_context.get("export_checks") is None

    with patch("mo_ldap_import_export.main.ExportChecks", return_value=MagicMock()):
        async with initialize_export_checks(fastramqpi):
            assert user_context.get("export_checks") is not None


async def test_initialize_converter(
    fastramqpi: FastRAMQPI, converter: MagicMock
) -> None:

    fastramqpi._context["user_context"].pop("converter")
    fastramqpi._context["user_context"].pop("ldap_it_system_user_key")
    fastramqpi._context["user_context"].pop("cpr_field")

    user_context = fastramqpi.get_context()["user_context"]
    assert user_context.get("converter") is None
    assert user_context.get("ldap_it_system_user_key") is None
    assert user_context.get("cpr_field") is None

    with patch("mo_ldap_import_export.main.LdapConverter", return_value=converter):
        async with initialize_converters(fastramqpi):
            assert user_context.get("converter") is not None
            assert user_context.get("ldap_it_system_user_key") == "ADGUID"
            assert user_context.get("cpr_field") == "EmployeeID"


async def test_initialize_init_engine(fastramqpi: FastRAMQPI) -> None:
    user_context = fastramqpi.get_context()["user_context"]
    assert user_context.get("init_engine") is None

    init_engine = MagicMock()

    with patch("mo_ldap_import_export.main.InitEngine", return_value=init_engine):
        async with initialize_init_engine(fastramqpi):
            assert user_context.get("init_engine") is not None
            init_engine.create_facets.assert_called_once()
            init_engine.create_it_systems.assert_called_once()
