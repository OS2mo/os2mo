# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
import time
from functools import partial
from itertools import combinations
from random import randint
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from fastramqpi.ramqp.utils import RequeueMessage
from httpx import HTTPStatusError
from more_itertools import first
from more_itertools import last
from ramodels.mo.details.address import Address
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.customer_specific import JobTitleFromADToMO
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.dataloaders import Verb
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.exceptions import DNNotFound
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.import_export import get_primary_engagement
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.main import handle_org_unit
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import EmployeeUUID
from mo_ldap_import_export.types import OrgUnitUUID
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
def context(
    dataloader: AsyncMock,
    converter: MagicMock,
    export_checks: AsyncMock,
    import_checks: AsyncMock,
    settings: MagicMock,
) -> Context:
    settings.discriminator_field = None
    ldap_connection = AsyncMock()
    context = Context(
        amqpsystem=AsyncMock(),
        user_context={
            "dataloader": dataloader,
            "converter": converter,
            "export_checks": export_checks,
            "import_checks": import_checks,
            "settings": settings,
            "ldap_connection": ldap_connection,
        },
    )
    return context


@pytest.fixture
def sync_tool(context: Context) -> SyncTool:
    user_context = context["user_context"]
    sync_tool = SyncTool(**user_context)
    return sync_tool


@pytest.fixture
def fake_dn() -> DN:
    return DN("CN=foo")


@pytest.fixture
def fake_find_mo_employee_dn(sync_tool: SyncTool, fake_dn: DN) -> None:
    sync_tool.dataloader.find_mo_employee_dn.return_value = {fake_dn}  # type: ignore


async def test_listen_to_changes_in_employee_no_employee(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}
    dataloader.moapi.load_mo_employee.return_value = None

    # Simulate a created employee
    with pytest.raises(RequeueMessage) as exc_info:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Unable to load mo object" in str(exc_info.value)


async def test_listen_to_changes_in_employees_person(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    # Ignore all changes, but person changes
    no_changes_async_mock = AsyncMock()
    no_changes_async_mock.return_value = {}
    sync_tool.mo_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_org_unit_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_ituser_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_engagement_to_ldap = no_changes_async_mock  # type: ignore

    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    # Simulate a created employee
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert dataloader.moapi.load_mo_employee.called
    assert converter.to_ldap.called
    assert dataloader.modify_ldap_object.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Employee", delete=False
    )


async def test_listen_to_changes_in_employees_org_unit_address(
    dataloader: AsyncMock,
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    # Ignore all changes, but address changes
    no_changes_async_mock = AsyncMock()
    no_changes_async_mock.return_value = {}
    sync_tool.mo_person_to_ldap = AsyncMock()  # type: ignore
    sync_tool.mo_person_to_ldap.return_value = LdapObject(dn="CN=foo")
    sync_tool.mo_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_ituser_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_engagement_to_ldap = no_changes_async_mock  # type: ignore

    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    engagement_uuid = uuid4()
    address_type_user_key = "LocationUnit"

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    # Simulate a created address

    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    read_engagements_is_primary_result = {
        "engagements": {
            "objects": [
                {
                    "validities": [
                        {
                            "is_primary": True,
                            "uuid": engagement_uuid,
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }
    read_engagements_is_primary_route = graphql_mock.query(
        "read_engagements_is_primary"
    )
    read_engagements_is_primary_route.result = read_engagements_is_primary_result

    # Mock MO read
    route = graphql_mock.query("read_filtered_addresses")
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                }
            ]
        }
    }

    # Test no mapping configured
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert not route.called

    # Setup mapping configuration
    location_unit_mapping = MagicMock()
    location_unit_mapping.objectClass = "ramodels.mo.details.address.Address"
    sync_tool.settings.conversion_mapping.ldap_to_mo = {  # type: ignore
        "LocationUnit": location_unit_mapping
    }

    # Test happy path
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert read_engagements_is_primary_route.called
    assert route.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, address_type_user_key, delete=False
    )
    dataloader.modify_ldap_object.reset_mock()

    # Test: No (primary) engagement
    read_engagements_is_primary_route.result = {"engagements": {"objects": []}}
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert read_engagements_is_primary_route.called
    dataloader.modify_ldap_object.assert_called_once_with(
        LdapObject(dn="CN=foo"), "Employee", delete=False
    )

    read_engagements_is_primary_route.result = read_engagements_is_primary_result

    # Test: Reading multiple addresses of the same type
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": UUID(int=test_mo_address.uuid.int + 1),
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
            ]
        }
    }
    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Multiple addresses of same type" in [x["event"] for x in cap_logs]

    # Test: When unable to read address details
    dataloader.load_mo_address.return_value = None
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Unable to load mo address" in str(exc.value)


async def test_listen_to_changes_in_employees_address(
    dataloader: AsyncMock,
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    # Ignore all changes, but address changes
    no_changes_async_mock = AsyncMock()
    no_changes_async_mock.return_value = {}
    sync_tool.mo_person_to_ldap = AsyncMock()  # type: ignore
    sync_tool.mo_person_to_ldap.return_value = LdapObject(dn="CN=foo")
    sync_tool.mo_org_unit_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_ituser_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_engagement_to_ldap = no_changes_async_mock  # type: ignore

    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    address_type_user_key = "EmailEmployee"

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    # Simulate a created address

    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    # Mock MO read
    route = graphql_mock.query("read_filtered_addresses")
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                }
            ]
        }
    }

    # Test no mapping configured
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert not route.called

    # Setup mapping configuration
    email_employee_mapping = MagicMock()
    email_employee_mapping.objectClass = "ramodels.mo.details.address.Address"
    del email_employee_mapping.org_unit
    sync_tool.settings.conversion_mapping.ldap_to_mo = {  # type: ignore
        "EmailEmployee": email_employee_mapping
    }

    # Test happy path
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert route.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, address_type_user_key, delete=False
    )

    # Test expected behavior when reading multiple addresses of the same type
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": UUID(int=test_mo_address.uuid.int + 1),
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
            ]
        }
    }
    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Multiple addresses of same type" in [x["event"] for x in cap_logs]

    # Test expected behavior when unable to read address details
    dataloader.load_mo_address.return_value = None
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Unable to load mo address" in str(exc.value)


async def test_listen_to_changes_in_employees_ituser(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    # Ignore all changes, but ituser changes
    no_changes_async_mock = AsyncMock()
    no_changes_async_mock.return_value = {}
    sync_tool.mo_person_to_ldap = AsyncMock()  # type: ignore
    sync_tool.mo_person_to_ldap.return_value = LdapObject(dn="CN=foo")
    sync_tool.mo_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_org_unit_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_engagement_to_ldap = no_changes_async_mock  # type: ignore

    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    ituser_uuid = uuid4()
    it_system_type_name = "AD"

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    # Simulate a created IT user

    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    # Mock MO read
    route = graphql_mock.query("read_filtered_itusers")
    route.result = {
        "itusers": {
            "objects": [
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": ituser_uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                }
            ]
        }
    }

    # Test no mapping configured
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert not route.called

    # Setup mapping configuration
    ad_mapping = MagicMock()
    ad_mapping.objectClass = "ramodels.mo.details.it_system.ITUser"
    sync_tool.settings.conversion_mapping.ldap_to_mo = {"AD": ad_mapping}  # type: ignore

    # Test happy path
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert route.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, it_system_type_name, delete=False
    )

    # Test expected behavior when reading multiple addresses of the same type
    route.result = {
        "itusers": {
            "objects": [
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": ituser_uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": UUID(int=ituser_uuid.int + 1),
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
            ]
        }
    }
    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Multiple itusers with the same itsystem" in [x["event"] for x in cap_logs]

    # Test expected behavior when unable to read itusers
    dataloader.load_mo_it_user.return_value = None
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Unable to load mo it-user" in str(exc.value)


async def test_listen_to_changes_in_employees_engagement(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    # Ignore all changes, but engagement changes
    no_changes_async_mock = AsyncMock()
    no_changes_async_mock.return_value = {}
    sync_tool.mo_person_to_ldap = AsyncMock()  # type: ignore
    sync_tool.mo_person_to_ldap.return_value = LdapObject(dn="CN=foo")
    sync_tool.mo_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_org_unit_address_to_ldap = no_changes_async_mock  # type: ignore
    sync_tool.mo_ituser_to_ldap = no_changes_async_mock  # type: ignore

    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    engagement_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}
    dataloader.load_mo_engagement = partial(  # partial to seed 'self'
        DataLoader.load_mo_engagement, dataloader
    )

    # Simulate a created engagement
    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    route1 = graphql_mock.query("read_engagements_is_primary")
    route1.result = {
        "engagements": {
            "objects": [
                {
                    "validities": [
                        {
                            "is_primary": True,
                            "uuid": engagement_uuid,
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    route2 = graphql_mock.query("read_engagements")
    route2.result = {
        "engagements": {
            "objects": [
                {
                    "validities": [
                        {
                            "user_key": "Depressed Developer",
                            "extension_1": "An",
                            "extension_2": "obscure",
                            "extension_3": "cry",
                            "extension_4": "for",
                            "extension_5": "help",
                            "extension_6": "from",
                            "extension_7": "within",
                            "extension_8": "the",
                            "extension_9": "machine",
                            "extension_10": "!",
                            "leave_uuid": None,
                            "primary_uuid": uuid4(),
                            "job_function_uuid": uuid4(),
                            "org_unit_uuid": uuid4(),
                            "engagement_type_uuid": uuid4(),
                            "employee_uuid": employee_uuid,
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    # Test no mapping configured
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert not route2.called

    # Setup mapping configuration
    sync_tool.settings.conversion_mapping.ldap_to_mo = {"Engagement": MagicMock()}  # type: ignore

    # Test happy path
    await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert route1.called
    assert route2.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Engagement", delete=False
    )

    # Test expected behavior when unable to read any engagements
    old = route1.result
    route1.result = {"engagements": {"objects": []}}
    await sync_tool.listen_to_changes_in_employees(employee_uuid)

    route1.result = old

    # Test expected behavior when unable to read engagement details
    route2.result = {"engagements": {"objects": []}}
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    assert "Unable to load mo engagement" in str(exc.value)


async def test_listen_to_changes_in_employees_no_dn(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    employee_uuid = uuid4()
    dataloader.find_mo_employee_dn.return_value = set()
    dataloader.make_mo_employee_dn.side_effect = DNNotFound("Not found")

    with capture_logs() as cap_logs:
        with pytest.raises(RequeueMessage):
            await sync_tool.listen_to_changes_in_employees(employee_uuid)

        messages = [w["event"] for w in cap_logs]
        assert messages == [
            "Registered change in an employee",
            "Unable to generate DN",
        ]


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

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

    engagement_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
    )

    dataloader.load_mo_employee_engagements.return_value = [
        engagement_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement1, engagement2]

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )
    assert len(operations) == 2
    formatted_objects = [obj for obj, _ in operations]
    assert last(formatted_objects).uuid == engagement_in_mo.uuid
    assert last(formatted_objects).user_key == engagement1.user_key
    assert first(formatted_objects) == engagement2


async def test_format_converted_engagement_duplicate(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement = Engagement.from_simplified_fields(
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
        user_key="duplicate_key",
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

    dataloader.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement]
    with pytest.raises(RequeueMessage) as exc_info:
        await sync_tool.format_converted_objects(converted_objects, json_key)
    assert "Bad mapping: Multiple MO objects" in str(exc_info.value)


async def test_format_converted_multiple_primary_engagements(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
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
        user_key="123",
        from_date="2021-01-01",
    )

    dataloader.load_mo_employee_engagements.return_value = [engagement1, engagement2]

    dataloader.is_primaries.return_value = [True, True]

    converted_objects = [engagement1, engagement2]

    with pytest.raises(RequeueMessage) as exc_info:
        await sync_tool.format_converted_objects(
            converted_objects,
            json_key="Engagement",
        )
    assert "Waiting for multiple primary engagements to be resolved" in str(
        exc_info.value
    )


async def test_format_converted_employee_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.import_mo_object_class.return_value = Employee

    employee1 = Employee(cpr_no="1212121234")
    employee2 = Employee(cpr_no="1212121235")

    converted_objects = [employee1, employee2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects, "Employee"
    )

    assert formatted_objects[0][0] == employee1
    assert formatted_objects[1][0] == employee2


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    person_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_employee_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1][0].uuid == address1_in_mo.uuid
    assert formatted_objects[1][0].value == "foo"  # type: ignore

    # Simulate that a matching employee for this address does not exist
    dataloader.load_mo_employee_addresses.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1][0].uuid == address1_in_mo.uuid
    assert formatted_objects[1][0].value == "foo"  # type: ignore

    # Simulate that a matching org unit for this address does not exist
    dataloader.load_mo_org_unit_addresses.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects_identical_to_mo(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

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

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )
    assert len(operations) == 2
    formatted_objects = [obj for obj, _ in operations]

    assert last(formatted_objects).value == "foo"  # type: ignore
    assert first(formatted_objects).value == "bar"  # type: ignore


async def test_format_converted_address_objects_without_person_or_org_unit(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    # These addresses have neither an org unit uuid or person uuid. we cannot convert
    # them
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields("foo", address_type_uuid, "2021-01-01")
    address2 = Address.from_simplified_fields("bar", address_type_uuid, "2021-01-01")

    converted_objects = [address1, address2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert len(formatted_objects) == 0


async def test_format_converted_it_user_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"ITUser": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "ITUser"
    converter.import_mo_object_class.return_value = ITUser

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", uuid4(), "2021-01-01", person_uuid=uuid4()
    )

    dataloader.load_mo_employee_it_users.return_value = [it_user_in_mo]

    person_uuid = uuid4()
    it_system_uuid = uuid4()
    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "ITUser",
    )

    formatted_user_keys = [f[0].user_key for f in formatted_objects]
    # assert "Username1" not in formatted_user_keys
    assert "Username1" in formatted_user_keys
    assert "Username2" in formatted_user_keys
    assert len(formatted_objects) == 2  # was 1

    # Simulate that a matching employee for this it user does not exist
    dataloader.load_mo_employee_it_users.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "ITUser")


async def test_format_converted_primary_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

    employee_uuid = uuid4()
    primary_uuid = uuid4()
    engagement1_in_mo_uuid = uuid4()
    engagement2_in_mo_uuid = uuid4()

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    async def is_primaries(uuids):
        return [uuid == engagement1_in_mo_uuid for uuid in uuids]

    dataloader.is_primaries = is_primaries

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

    json_key = "Engagement"

    converted_objects = [engagement1]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )

    assert len(formatted_objects) == 1
    assert formatted_objects[0][0].primary.uuid is not None  # type: ignore
    assert formatted_objects[0][0].user_key == "123"

    # Simulate that a matching employee for this engagement does not exist
    dataloader.load_mo_employee_engagements.side_effect = NoObjectsReturnedException(
        "f"
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, json_key)


async def test_import_single_object_no_employee_no_sync(
    sync_tool: SyncTool, minimal_valid_settings: Settings
) -> None:
    # Note that converter.settings and dataloader.settings are still mocked
    sync_tool.settings = minimal_valid_settings
    # Ignore typing since it is actually a mock
    sync_tool.dataloader.find_mo_employee_uuid.return_value = None  # type: ignore

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")

    messages = [w["event"] for w in cap_logs]
    assert messages == [
        "Generating DN",
        "Importing user",
        "Employee not found in MO, and not configured to create it",
    ]


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_from_LDAP_but_import_equals_false(
    sync_tool: SyncTool, minimal_valid_settings: Settings
) -> None:
    # Note that converter.settings and dataloader.settings are still mocked
    sync_tool.settings = minimal_valid_settings

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")
        messages = [w["event"] for w in cap_logs if w["log_level"] == "info"]
        assert "Import to MO filtered" in messages
        assert "Loading object" not in messages


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_forces_json_key_ordering(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    """
    Verify that `import_single_object` visits each "JSON key" in a specific order.
    `Employee` keys must be visited first, then `Engagement` keys, and finally all other
    keys.
    """
    # Arrange: inject a list of JSON keys that have the wrong order
    sync_tool.format_converted_objects = AsyncMock()  # type: ignore
    sync_tool.format_converted_objects.return_value = []

    sync_tool.settings.conversion_mapping.ldap_to_mo.keys.return_value = {  # type: ignore
        "Employee",
        "Engagement",
        "Address",
    }
    converter.from_ldap.return_value = [MagicMock()]  # list of (at least) one item
    # Act: run the method and collect logs
    with (
        capture_logs() as cap_logs,
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user("CN=foo")
        # Assert: verify that we process JSON keys in the expected order, regardless of
        # the original ordering.
        logged_json_keys: list[str] = [
            m["json_key"]
            for m in cap_logs
            if m.get("json_key") and "Loaded object" in m["event"]
        ]
        assert logged_json_keys == ["Employee", "Engagement", "Address"]


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_address_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.mapping = {"ldap_to_mo": {"Employee": {"_mapper_": None}}}

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

    formatted_objects = [
        (converted_object, Verb.CREATE) for converted_object in converted_objects
    ]

    converter.from_ldap.return_value = converted_objects

    with (
        patch(
            "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
            return_value=formatted_objects,
        ),
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user("CN=foo")
        dataloader.create_or_edit_mo_objects.assert_called_with(formatted_objects)

    # Simulate invalid phone number
    # Undo lots and lots of useless mocking
    dataloader.create_or_edit_mo_objects = partial(
        DataLoader.create_or_edit_mo_objects, dataloader
    )
    dataloader.create = partial(DataLoader.create, dataloader)
    dataloader.create_object = partial(DataLoader.create_object, dataloader)
    exception = HTTPStatusError(
        "invalid phone number", request=MagicMock(), response=MagicMock()
    )
    dataloader.create_address.side_effect = exception
    with (
        pytest.raises(ExceptionGroup) as exc_info,
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user("CN=foo")
    assert exc_info.value.exceptions == (exception, exception)


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_it_user_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.mapping = {"ldap_to_mo": {"Employee": {"_mapper_": None}}}

    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.ITUser"
    converter.import_mo_object_class.return_value = ITUser
    converter.get_mo_attributes.return_value = ["user_key", "validity"]

    it_system_type1_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username3", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    converter.from_ldap.return_value = converted_objects

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
    )

    it_users_in_mo = [it_user_in_mo]

    dataloader.load_mo_employee_it_users.return_value = it_users_in_mo

    with patch("mo_ldap_import_export.import_export.get_ldap_object"):
        await sync_tool.import_single_user("CN=foo")

    expected = [
        (converted_objects[1].user_key, converted_objects[1].uuid, Verb.CREATE),
        (converted_objects[2].user_key, converted_objects[2].uuid, Verb.CREATE),
        (converted_objects[0].user_key, it_user_in_mo.uuid, Verb.EDIT),
    ]

    actual = [
        (obj.user_key, obj.uuid, verb)
        for obj, verb in dataloader.create_or_edit_mo_objects.call_args.args[0]
    ]

    assert actual == expected


async def test_import_single_object_from_LDAP_non_existing_employee(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dn = "CN=foo"

    sync_tool.settings.ldap_cpr_attribute = "EmployeeID"  # type: ignore

    sync_tool.format_converted_objects = AsyncMock()  # type: ignore
    sync_tool.format_converted_objects.return_value = []

    ldap_connection = MagicMock()
    ldap_connection.get_response.return_value = (
        [
            {
                "type": "searchResEntry",
                "attributes": {"EmployeeID": "0101011234"},
                "dn": dn,
            }
        ],
        {"type": "test"},
    )
    sync_tool.ldap_connection = ldap_connection
    sync_tool.dataloader.load_ldap_cpr_object.return_value = [LdapObject(dn=dn)]  # type: ignore

    dataloader.find_mo_employee_uuid.return_value = None
    await sync_tool.import_single_user(dn)

    # Even though find_mo_employee_uuid does not return an uuid; it is generated
    assert type(converter.from_ldap.call_args_list[0].kwargs["employee_uuid"]) is UUID


async def test_wait_for_import_to_finish(sync_tool: SyncTool):
    wait_for_import_to_finish = partial(sync_tool.wait_for_import_to_finish)

    @wait_for_import_to_finish
    async def decorated_func(self, dn):
        await asyncio.sleep(0.2)
        return

    async def regular_func(self, dn):
        await asyncio.sleep(0.2)
        return

    dn = "CN=foo"
    different_dn = "CN=bar"

    # Normally this would execute in 0.2 seconds + overhead
    t1 = time.time()
    await asyncio.gather(
        regular_func(sync_tool, dn),
        regular_func(sync_tool, dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3

    # But the decorator will make the second call wait for the first one to complete
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, dn),
        decorated_func(sync_tool, dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.4
    assert elapsed_time < 0.5

    # But only if payload.uuid is the same in both calls
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, dn),
        decorated_func(sync_tool, different_dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_jobtitlefromadtomo_objects(
    context: Context,
    converter: MagicMock,
    sync_tool: SyncTool,
    fake_dn: DN,
) -> None:
    converter.find_mo_object_class.return_value = (
        "mo_ldap_import_export.customer_specific.JobTitleFromADToMO"
    )
    converter.import_mo_object_class.return_value = JobTitleFromADToMO
    converter.get_mo_attributes.return_value = ["user", "uuid", "job_function"]
    sync_tool.settings.conversion_mapping.ldap_to_mo.keys.return_value = {  # type: ignore
        "Custom"
    }

    converted_object = AsyncMock()

    converted_objects = [converted_object]

    formatted_objects = [
        (converted_object, Verb.CREATE) for converted_object in converted_objects
    ]

    converter.from_ldap.return_value = converted_objects

    context["legacy_graphql_session"] = AsyncMock()

    with (
        patch(
            "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
            return_value=formatted_objects,
        ),
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user(fake_dn)
        converted_object.sync_to_mo.assert_called_once()


async def test_move_ldap_object(sync_tool: SyncTool, dataloader: AsyncMock):
    dataloader.move_ldap_object.return_value = True

    # user_context = {"dataloader": dataloader}
    old_dn = "CN=Angus,OU=Auchtertool"
    new_dn = "CN=Angus,OU=Dundee"

    # Attempt to move Angus from OU=Auchtertool to OU=Dundee
    ldap_object = await sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    # Which means we need to create OU=Dundee
    dataloader.ldapapi.create_ou.assert_called_once_with("OU=Dundee")

    # Them move Angus
    dataloader.move_ldap_object.assert_called_once_with(old_dn, new_dn)

    # And delete OU=Auchtertool, which is now empty
    dataloader.delete_ou.assert_called_once_with("OU=Auchtertool")

    assert ldap_object.dn == new_dn


async def test_move_ldap_object_move_failed(sync_tool: SyncTool, dataloader: AsyncMock):
    dataloader.move_ldap_object.return_value = False

    old_dn = "CN=Angus,OU=Auchtertool"
    new_dn = "CN=Angus,OU=Dundee"

    # Attempt to move Angus from OU=Auchtertool to OU=Dundee
    ldap_object = await sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    # The move was not successful so we fall back to the old DN
    assert ldap_object.dn == old_dn
    dataloader.delete_ou.assert_not_called()


async def test_move_ldap_object_nothing_to_move(
    sync_tool: SyncTool, dataloader: AsyncMock
):
    old_dn = "CN=Angus,OU=Dundee"
    new_dn = "CN=Angus,OU=Dundee"

    # The new DN is equal to the old DN. We expect nothing to happen.
    ldap_object = await sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    dataloader.create_ou.assert_not_called()
    dataloader.move_ldap_object.assert_not_called()
    dataloader.delete_ou.assert_not_called()
    assert ldap_object.dn == new_dn
    assert ldap_object.dn == old_dn


async def test_publish_engagements_for_org_unit(dataloader: AsyncMock) -> None:
    amqpsystem = AsyncMock()
    amqpsystem.exchange_name = "my-unique-exchange-name"
    uuid = OrgUnitUUID(uuid4())
    await handle_org_unit(uuid, dataloader.graphql_client, amqpsystem)
    dataloader.graphql_client.org_unit_engagements_refresh.assert_called_with(
        amqpsystem.exchange_name, uuid
    )


async def test_perform_import_checks_noop(sync_tool: SyncTool) -> None:
    """Test that perform_import_checks returns True when nothing is checked."""
    sync_tool.settings.check_holstebro_ou_issue_57426 = False  # type: ignore
    result = await sync_tool.perform_import_checks("CN=foo", "Employee")
    assert result is True


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_holstebro_import_checks(sync_tool: SyncTool, fake_dn: DN) -> None:
    with (
        patch(
            "mo_ldap_import_export.import_export.SyncTool.perform_import_checks",
            return_value=False,
        ),
        capture_logs() as cap_logs,
    ):
        await sync_tool.import_single_user(fake_dn)
        assert "Import checks executed" in str(cap_logs)


async def test_import_single_user_entity(sync_tool: SyncTool) -> None:
    sync_tool.converter.from_ldap.return_value = []  # type: ignore

    json_key = "Engagement"
    dn = "CN=foo"
    employee_uuid = uuid4()
    with (
        capture_logs() as cap_logs,
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user_entity(json_key, dn, employee_uuid)

        assert "No converted objects" in str(cap_logs)


engagement_uuid1 = uuid4()
engagement_uuid2 = uuid4()
engagement_uuid3 = uuid4()

waiting_for_primary = "Waiting for primary engagement to be decided"
waiting_for_multiple = "Waiting for multiple primary engagements to be resolved"

past = {"from": "1970-01-01T00:00:00Z", "to": "1980-01-01T00:00:00Z"}
current = {"from": "1970-01-01T00:00:00Z", "to": None}
future = {"from": "9970-01-01T00:00:00Z", "to": None}


def generate_random_validity() -> dict[str, str | None]:
    # TODO: Actually generate proper random dates?
    # TODO: Generate None in end date?
    start_year = randint(1000, 9999)
    end_year = randint(start_year, 9999)
    return {
        "from": f"{start_year}-01-01T00:00:00Z",
        "to": f"{end_year}-01-02T00:00:00Z",
    }


def construct_validity(is_primary: bool, validity: Any, uuid: UUID) -> dict[str, Any]:
    return {"is_primary": is_primary, "uuid": uuid, "validity": validity}


def generate_object():
    # TODO: Replace this with hypothesis?
    num_validities = randint(1, 5)
    return {
        "validities": [
            construct_validity(False, generate_random_validity(), engagement_uuid1)
            for _ in range(num_validities)
        ]
    }


@pytest.mark.parametrize(
    "objects,expected",
    [
        # No objects, no validities
        ([], None),
    ]
    + [
        # Any number of objects with any number of validities, but no primary
        (
            [generate_object() for _ in range(num_objects)],
            waiting_for_primary,
        )
        for num_objects in range(1, 5)
    ]
    + [
        # One primary, any time
        (
            [{"validities": [construct_validity(True, validity, engagement_uuid1)]}],
            engagement_uuid1,
        )
        for validity in [past, current, future]
    ]
    + [
        # Two validities, non primary and primary, any time
        # Any combination of times should be okay here
        (
            [
                {
                    "validities": [
                        construct_validity(False, val1, engagement_uuid1),
                        construct_validity(True, val2, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        )
        for val1, val2 in combinations([past, current, future], 2)
    ]
    + [
        # Two objects with one validity each, non primary and primary, any time
        # Any combination of times should be okay here
        (
            [
                {"validities": [construct_validity(False, val1, engagement_uuid1)]},
                {"validities": [construct_validity(True, val2, engagement_uuid2)]},
            ],
            engagement_uuid2,
        )
        for val1, val2 in combinations([past, current, future], 2)
    ]
    + [
        # Two validities, both primary, both current
        (
            [
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid1),
                        construct_validity(True, current, engagement_uuid1),
                    ]
                }
            ],
            waiting_for_multiple,
        ),
        # Two object with one validity each, both primary, both current
        (
            [
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid1),
                    ]
                },
                {"validities": [construct_validity(True, current, engagement_uuid1)]},
            ],
            waiting_for_multiple,
        ),
        # Two validities both primary, both past
        # TODO: This should probably fail like the above
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                        construct_validity(True, past, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        ),
        # Two object with one validity each, both primary, both past
        # TODO: This should probably fail like the above
        # NOTE: Whichever comes first wins, is this well-defined in MO?
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                    ]
                },
                {"validities": [construct_validity(True, past, engagement_uuid2)]},
            ],
            engagement_uuid1,
        ),
        # Two validities both primary, both future
        # TODO: This should probably fail like the above
        (
            [
                {
                    "validities": [
                        construct_validity(True, future, engagement_uuid1),
                        construct_validity(True, future, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        ),
        # Two object with one validity each, both primary, both future
        # TODO: This should probably fail like the above
        # NOTE: Whichever comes first wins, is this well-defined in MO?
        (
            [
                {
                    "validities": [
                        construct_validity(True, future, engagement_uuid2),
                    ]
                },
                {"validities": [construct_validity(True, future, engagement_uuid1)]},
            ],
            engagement_uuid2,
        ),
    ]
    + [
        # Two validities both primary, temporally spread
        (
            [
                {
                    "validities": [
                        construct_validity(True, val1, engagement_uuid1),
                        construct_validity(True, val2, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        )
        for val1, val2 in [(past, current), (past, future), (current, future)]
    ]
    + [
        # Two object with one validity each, both primary, temporally spread
        (
            [
                {"validities": [construct_validity(True, val1, engagement_uuid1)]},
                {"validities": [construct_validity(True, val2, engagement_uuid2)]},
            ],
            expected,
        )
        for val1, val2, expected in [
            (past, current, engagement_uuid2),
            (past, future, engagement_uuid2),
            (current, future, engagement_uuid1),
        ]
    ]
    + [
        # Three engagements all primary, all temporally spread
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                        construct_validity(True, current, engagement_uuid2),
                        construct_validity(True, future, engagement_uuid3),
                    ]
                }
            ],
            engagement_uuid2,
        ),
        # Three objects with one validity each, all primary, all temporally spread
        (
            [
                {"validities": [construct_validity(True, past, engagement_uuid1)]},
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid2),
                    ]
                },
                {"validities": [construct_validity(True, future, engagement_uuid3)]},
            ],
            engagement_uuid2,
        ),
    ],
)
async def test_get_primary_engagement(
    graphql_mock: GraphQLMocker,
    objects: list[dict[str, Any]],
    expected: UUID | str | None,
) -> None:
    graphql_client = GraphQLClient("http://example.com/graphql")

    employee_uuid = EmployeeUUID(uuid4())

    route = graphql_mock.query("read_engagements_is_primary")
    route.result = {"engagements": {"objects": objects}}

    if isinstance(expected, str):
        with pytest.raises(RequeueMessage) as exc_info:
            await get_primary_engagement(graphql_client, employee_uuid)
        assert expected in str(exc_info.value)
    else:
        result = await get_primary_engagement(graphql_client, employee_uuid)
        assert result == expected

    assert route.called


async def test_find_best_dn(sync_tool: SyncTool) -> None:
    dn = "CN=foo"
    sync_tool.dataloader.find_mo_employee_dn.return_value = set()  # type: ignore
    sync_tool.dataloader.make_mo_employee_dn.return_value = dn  # type: ignore

    uuid = EmployeeUUID(uuid4())
    result = await sync_tool._find_best_dn(uuid)
    assert result == dn
