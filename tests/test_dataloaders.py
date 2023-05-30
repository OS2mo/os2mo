# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
import asyncio
import datetime
import re
from collections.abc import Iterator
from typing import Collection
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from gql import gql
from gql.transport.exceptions import TransportQueryError
from graphql import print_ast
from ldap3.core.exceptions import LDAPInvalidValueError
from ramodels.mo.details.address import Address
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from ramqp.mo.models import ObjectType
from ramqp.mo.models import ServiceType
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import AttributeNotFound
from mo_ldap_import_export.exceptions import DNNotFound
from mo_ldap_import_export.exceptions import InvalidChangeDict
from mo_ldap_import_export.exceptions import InvalidQueryResponse
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import UUIDNotFoundException
from mo_ldap_import_export.import_export import IgnoreMe


@pytest.fixture()
def ldap_attributes() -> dict:
    return {
        "department": None,
        "name": "John",
        "employeeID": "0101011234",
        "postalAddress": "foo",
    }


@pytest.fixture
def cpr_field() -> str:
    return "employeeID"


@pytest.fixture
def ldap_connection(ldap_attributes: dict) -> Iterator[MagicMock]:
    """Fixture to construct a mock ldap_connection.

    Yields:
        A mock for ldap_connection.
    """

    with patch(
        "mo_ldap_import_export.dataloaders.get_ldap_attributes",
        return_value=ldap_attributes.keys(),
    ):
        ldap_connection = MagicMock()
        ldap_connection.compare.return_value = False
        yield ldap_connection


@pytest.fixture
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def gql_client_sync() -> Iterator[MagicMock]:
    gql_client_sync = MagicMock()
    gql_client_sync.execute.return_value = {"org": {"uuid": str(uuid4())}}
    yield gql_client_sync


@pytest.fixture
def model_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLIENT_ID", "foo")
    monkeypatch.setenv("client_secret", "bar")
    monkeypatch.setenv("LDAP_CONTROLLERS", '[{"host": "0.0.0.0"}]')
    monkeypatch.setenv("LDAP_DOMAIN", "LDAP")
    monkeypatch.setenv("LDAP_USER", "foo")
    monkeypatch.setenv("LDAP_PASSWORD", "bar")
    monkeypatch.setenv("LDAP_SEARCH_BASE", "DC=ad,DC=addev")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin")
    monkeypatch.setenv("AUTHENTICATION_SECRET", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_LEVEL", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_TYPE", "foo")
    monkeypatch.setenv("LDAP_OUS_TO_WRITE_TO", '[""]')

    return Settings()


@pytest.fixture
def converter() -> MagicMock:
    converter_mock = MagicMock()
    converter_mock.find_ldap_object_class.return_value = "user"
    converter_mock._export_to_ldap_ = MagicMock()
    converter_mock._export_to_ldap_.return_value = True
    return converter_mock


@pytest.fixture
def username_generator() -> MagicMock:
    return MagicMock()


@pytest.fixture
def sync_tool() -> AsyncMock:
    sync_tool = AsyncMock()
    sync_tool.dns_to_ignore = IgnoreMe()
    return sync_tool


@pytest.fixture
def context(
    ldap_connection: MagicMock,
    gql_client: AsyncMock,
    model_client: AsyncMock,
    settings: Settings,
    cpr_field: str,
    converter: MagicMock,
    gql_client_sync: MagicMock,
    sync_tool: AsyncMock,
    username_generator: MagicMock,
) -> Context:

    return {
        "user_context": {
            "settings": settings,
            "ldap_connection": ldap_connection,
            "gql_client": gql_client,
            "model_client": model_client,
            "cpr_field": cpr_field,
            "converter": converter,
            "gql_client_sync": gql_client_sync,
            "sync_tool": sync_tool,
            "username_generator": username_generator,
            "ldap_it_system_user_key": "Active Directory",
        },
    }


@pytest.fixture
def get_attribute_types() -> dict:

    attr1_mock = MagicMock()
    attr2_mock = MagicMock()
    attr1_mock.single_value = False
    attr2_mock.single_value = True
    attr1_mock.syntax = "1.3.6.1.4.1.1466.115.121.1.7"  # Boolean
    attr2_mock.syntax = "1.3.6.1.4.1.1466.115.121.1.27"  # Integer
    return {
        "attr1": attr1_mock,
        "attr2": attr2_mock,
        "department": MagicMock(),
        "name": MagicMock(),
        "employeeID": MagicMock(),
        "postalAddress": MagicMock(),
        "objectClass": MagicMock(),
    }


@pytest.fixture
def dataloader(context: Context, get_attribute_types: dict) -> DataLoader:
    """Fixture to construct a dataloaders object using fixture mocks.

    Yields:
        Dataloaders with mocked clients.
    """
    with patch(
        "mo_ldap_import_export.dataloaders.get_attribute_types",
        return_value=get_attribute_types,
    ):
        return DataLoader(context)


def mock_ldap_response(ldap_attributes: dict, dn: str) -> dict[str, Collection[str]]:

    expected_attributes = ldap_attributes.keys()
    inner_dict = ldap_attributes

    for attribute in expected_attributes:
        if attribute not in inner_dict.keys():
            inner_dict[attribute] = None

    response = {"dn": dn, "type": "searchResEntry", "attributes": inner_dict}

    return response


async def test_load_ldap_cpr_object(
    ldap_connection: MagicMock, dataloader: DataLoader, ldap_attributes: dict
) -> None:
    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_result = LdapObject(dn=dn, **ldap_attributes)
    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    output = dataloader.load_ldap_cpr_object("0101012002", "Employee")
    assert output == expected_result

    with pytest.raises(NoObjectsReturnedException):
        dataloader.load_ldap_cpr_object("None", "Employee")

    with pytest.raises(NoObjectsReturnedException):
        dataloader.user_context["cpr_field"] = None
        dataloader.load_ldap_cpr_object("0101012002", "Employee")


async def test_load_ldap_objects(
    ldap_connection: MagicMock, dataloader: DataLoader, ldap_attributes: dict
) -> None:

    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"
    expected_result = [LdapObject(dn=dn, **ldap_attributes)] * 2
    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)] * 2

    output = await asyncio.gather(
        dataloader.load_ldap_objects("Employee"),
    )

    assert output[0] == expected_result


async def test_modify_ldap_employee(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    ldap_attributes: dict,
) -> None:

    employee = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        **ldap_attributes,
    )

    bad_response = {
        "result": 67,
        "description": "notAllowedOnRDN",
        "dn": "",
        "message": (
            "000020B1: UpdErr: DSID-030F1357,"
            " problem 6004 (CANT_ON_RDN), data 0\n\x00"
        ),
        "referrals": None,
        "type": "modifyResponse",
    }
    good_response = {
        "result": 0,
        "description": "success",
        "dn": "",
        "message": "",
        "referrals": None,
        "type": "modifyResponse",
    }

    # LDAP does not allow one to change the 'name' attribute and throws a bad response
    not_allowed_on_RDN = ["name"]
    parameters_to_upload = [k for k in employee.dict().keys() if k not in ["dn", "cpr"]]
    allowed_parameters_to_upload = [
        p for p in parameters_to_upload if p not in not_allowed_on_RDN
    ]
    disallowed_parameters_to_upload = [
        p for p in parameters_to_upload if p not in allowed_parameters_to_upload
    ]

    results = iter(
        [good_response] * len(allowed_parameters_to_upload)
        + [bad_response] * len(disallowed_parameters_to_upload)
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    # Every time a modification is performed, point to the next page.
    ldap_connection.modify.side_effect = set_new_result

    # Get result from dataloader
    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_cpr_object",
        return_value=employee,
    ):
        output = await asyncio.gather(
            dataloader.modify_ldap_object(employee, "user"),
        )

    assert output == [
        [good_response] * len(allowed_parameters_to_upload)
        + [bad_response] * len(disallowed_parameters_to_upload)
    ]


async def test_append_data_to_ldap_object(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    ldap_attributes: dict,
    cpr_field: str,
):

    address = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        postalAddress="foo",
        **{cpr_field: "123"},
    )

    dataloader.single_value = {"postalAddress": False, cpr_field: True}

    await asyncio.gather(
        dataloader.modify_ldap_object(address, "user"),
    )

    changes = {"postalAddress": [("MODIFY_ADD", "foo")]}
    dn = address.dn
    assert ldap_connection.modify.called_once_with(dn, changes)


async def test_delete_data_from_ldap_object(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    ldap_attributes: dict,
    cpr_field: str,
):

    address = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        postalAddress="foo",
        sharedValue="bar",
        **{cpr_field: "123"},
    )

    dataloader.single_value = {"postalAddress": False, cpr_field: True}

    # Note: 'sharedValue' won't be deleted because it is shared with another ldap object
    dataloader._mo_to_ldap_attributes = [
        "postalAddress",
        cpr_field,
        cpr_field,
        "sharedValue",
        "sharedValue",
    ]

    await asyncio.gather(
        dataloader.modify_ldap_object(address, "user", delete=True),
    )

    changes = {"postalAddress": [("MODIFY_DELETE", "foo")]}
    dn = address.dn
    assert ldap_connection.modify.called_once_with(dn, changes)


async def test_upoad_ldap_object_invalid_value(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    cpr_field: str,
):
    ldap_object = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        postalAddress="foo",
        **{cpr_field: "123"},
    )

    ldap_connection.modify.side_effect = LDAPInvalidValueError("Invalid value")

    with capture_logs() as cap_logs:
        await asyncio.gather(
            dataloader.modify_ldap_object(ldap_object, "user"),
        )

        warnings = [w for w in cap_logs if w["log_level"] == "warning"]
        assert re.match(
            "Invalid value",
            str(warnings[-1]["event"]),
        )


async def test_modify_ldap_object_but_export_equals_false(
    dataloader: DataLoader, converter: MagicMock
):

    converter._export_to_ldap_.return_value = False
    ldap_object = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        postalAddress="foo",
    )

    with capture_logs() as cap_logs:
        await asyncio.gather(
            dataloader.modify_ldap_object(ldap_object, ""),
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            "_export_to_ldap_ == False",
            str(messages[-1]["event"]),
        )


async def test_load_mo_employee(dataloader: DataLoader, gql_client: AsyncMock) -> None:

    cpr_no = "1407711900"
    uuid = uuid4()

    gql_client.execute.return_value = {
        "employees": [
            {"objects": [{"cpr_no": cpr_no, "uuid": uuid}]},
        ]
    }

    expected_result = [Employee(**{"cpr_no": cpr_no, "uuid": uuid})]

    output = await asyncio.gather(
        dataloader.load_mo_employee(uuid),
    )

    assert output == expected_result


async def test_upload_mo_employee(
    model_client: AsyncMock, dataloader: DataLoader
) -> None:
    """Test that test_upload_mo_employee works as expected."""

    return_values = ["1", None, "3"]
    input_values = [1, 2, 3]
    for input_value, return_value in zip(input_values, return_values):
        model_client.upload.return_value = return_value

        result = await asyncio.gather(
            dataloader.upload_mo_objects([input_value]),
        )
        assert result[0] == return_value
        model_client.upload.assert_called_with([input_value])


async def test_make_overview_entry(dataloader: DataLoader):

    attributes = ["attr1", "attr2"]
    superiors = ["sup1", "sup2"]
    entry = dataloader.make_overview_entry(attributes, superiors)

    assert list(entry["attributes"].keys()) == attributes
    assert entry["superiors"] == superiors

    assert entry["attributes"]["attr1"]["single_value"] is False
    assert entry["attributes"]["attr2"]["single_value"] is True

    assert entry["attributes"]["attr1"]["field_type"] == "Boolean"
    assert entry["attributes"]["attr2"]["field_type"] == "Integer"


async def test_get_overview(dataloader: DataLoader):

    schema_mock = MagicMock()
    schema_mock.object_classes = {"object1": "foo"}

    with patch(
        "mo_ldap_import_export.dataloaders.get_ldap_schema",
        return_value=schema_mock,
    ), patch(
        "mo_ldap_import_export.dataloaders.get_ldap_attributes",
        return_value=["attr1", "attr2"],
    ), patch(
        "mo_ldap_import_export.dataloaders.get_ldap_superiors",
        return_value=["sup1", "sup2"],
    ):
        output = dataloader.load_ldap_overview()

    assert list(output["object1"]["attributes"].keys()) == ["attr1", "attr2"]
    assert output["object1"]["superiors"] == ["sup1", "sup2"]
    assert output["object1"]["attributes"]["attr1"]["single_value"] is False
    assert output["object1"]["attributes"]["attr2"]["single_value"] is True

    assert output["object1"]["attributes"]["attr1"]["field_type"] == "Boolean"
    assert output["object1"]["attributes"]["attr2"]["field_type"] == "Integer"


async def test_get_populated_overview(dataloader: DataLoader):

    overview = {
        "user": {"attributes": ["attr1", "attr2"], "superiors": ["sup1", "sup2"]}
    }

    responses = [
        {
            "attributes": {
                "attr1": "foo",  # We expect this attribute in the output
                "attr2": None,  # But not this one
                "objectClass": ["top", "person", "user"],
            }
        },
        {
            "attributes": {
                "attr1": "foo",
                "attr2": "bar",  # We still do not expect this one; wrong object class
                "objectClass": ["top", "person", "user", "computer"],
            }
        },
    ]

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_overview",
        return_value=overview,
    ), patch(
        "mo_ldap_import_export.dataloaders.paged_search",
        return_value=responses,
    ):
        output = dataloader.load_ldap_populated_overview()

    assert sorted(list(output["user"]["attributes"].keys())) == sorted(
        ["attr1", "objectClass"]
    )
    assert output["user"]["superiors"] == ["sup1", "sup2"]
    assert output["user"]["attributes"]["attr1"]["single_value"] is False


async def test_load_mo_address_types(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "Email"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    assert dataloader.load_mo_employee_address_types()[uuid]["name"] == name
    assert dataloader.load_mo_org_unit_address_types()[uuid]["name"] == name


async def test_load_mo_primary_types(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    value_key = "primary"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "value_key": value_key}]},
        ]
    }

    output = dataloader.load_mo_primary_types()
    assert output[uuid]["value_key"] == value_key


async def test_load_mo_job_functions(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "Manager"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    output = dataloader.load_mo_job_functions()
    assert output[uuid]["name"] == name


async def test_load_mo_visibility(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "Hemmelig"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    output = dataloader.load_mo_visibility()
    assert output[uuid]["name"] == name


async def test_load_mo_engagement_types(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "Ansat"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    output = dataloader.load_mo_engagement_types()
    assert output[uuid]["name"] == name


async def test_load_mo_org_unit_types(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "Direktørområde"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    output = dataloader.load_mo_org_unit_types()
    assert output[uuid]["name"] == name


async def test_load_mo_org_unit_levels(
    dataloader: DataLoader, gql_client_sync: MagicMock
) -> None:

    uuid = uuid4()
    name = "N1"

    gql_client_sync.execute.return_value = {
        "facets": [
            {"classes": [{"uuid": uuid, "name": name}]},
        ]
    }

    output = dataloader.load_mo_org_unit_levels()
    assert output[uuid]["name"] == name


async def test_load_mo_address_no_valid_addresses(
    dataloader: DataLoader, gql_client: AsyncMock
) -> None:
    uuid = uuid4()

    gql_client.execute.return_value = {"addresses": []}

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(dataloader.load_mo_address(uuid))


async def test_load_mo_address(dataloader: DataLoader, gql_client: AsyncMock) -> None:

    uuid = uuid4()

    address_dict: dict = {
        "value": "foo@bar.dk",
        "uuid": uuid,
        "address_type": {"uuid": uuid},
        "validity": {"from": "2021-01-01 01:00", "to": None},
        "person": {"uuid": uuid},
        "org_unit": {"uuid": uuid},
        "visibility": {"uuid": uuid},
    }

    # Note that 'Address' requires 'person' to be a dict
    expected_result = Address(**address_dict.copy())

    # While graphQL returns it as a list with length 1
    address_dict["person"] = [{"cpr_no": "0101012002"}]
    address_dict["address_type"]["user_key"] = "address"
    address_dict["value2"] = None
    address_dict["visibility_uuid"] = uuid
    address_dict["employee_uuid"] = uuid
    address_dict["org_unit_uuid"] = uuid

    gql_client.execute.return_value = {
        "addresses": [
            {"objects": [address_dict]},
        ]
    }

    output = await asyncio.gather(
        dataloader.load_mo_address(uuid),
    )

    assert output[0] == expected_result


def test_load_ldap_object(dataloader: DataLoader):

    make_ldap_object = MagicMock()
    with patch(
        "mo_ldap_import_export.dataloaders.single_object_search",
        return_value="foo",
    ), patch(
        "mo_ldap_import_export.dataloaders.make_ldap_object",
        new_callable=make_ldap_object,
    ):
        dn = "CN=Nikki Minaj"
        output = dataloader.load_ldap_object(dn, ["foo", "bar"])
        assert output.called_once_with("foo", dataloader.context)


def test_cleanup_attributes_in_ldap(dataloader: DataLoader):
    dataloader.single_value = {"value": False}

    dataloader.shared_attribute = MagicMock()  # type: ignore
    dataloader.shared_attribute.return_value = False

    ldap_objects = [
        # LdapObject(dn="foo", value="New address"),
        LdapObject(dn="CN=foo", value="Old address"),
    ]

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(dn="foo", value=["New address", "Old address"]),
    ):
        dataloader.cleanup_attributes_in_ldap(ldap_objects)

        changes = {"value": [("MODIFY_DELETE", "Old address")]}
        assert dataloader.ldap_connection.modify.called_once_with("foo", changes)

    with capture_logs() as cap_logs:

        ldap_objects = [LdapObject(dn="foo")]
        dataloader.cleanup_attributes_in_ldap(ldap_objects)

        infos = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            "No cleanable attributes found",
            infos[-1]["event"],
        )


async def test_load_mo_employee_addresses(
    dataloader: DataLoader, gql_client: AsyncMock
):

    address1_uuid = uuid4()
    address2_uuid = uuid4()

    gql_client.execute.return_value = {
        "employees": [
            {
                "objects": [
                    {
                        "addresses": [
                            {"uuid": address1_uuid},
                            {"uuid": address2_uuid},
                        ]
                    }
                ]
            },
        ]
    }

    employee_uuid = uuid4()
    address_type_uuid = uuid4()

    load_mo_address = AsyncMock()
    dataloader.load_mo_address = load_mo_address  # type: ignore

    await asyncio.gather(
        dataloader.load_mo_employee_addresses(employee_uuid, address_type_uuid),
    )

    load_mo_address.assert_any_call(address1_uuid)
    load_mo_address.assert_any_call(address2_uuid)


async def test_load_mo_employee_addresses_not_found(
    dataloader: DataLoader, gql_client: AsyncMock
):

    gql_client.execute.return_value = {"employees": []}

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(
            dataloader.load_mo_employee_addresses(uuid4(), uuid4()),
        )


async def test_find_mo_employee_uuid(
    dataloader: DataLoader, gql_client: AsyncMock, gql_client_sync: MagicMock
):
    uuid = uuid4()
    objectGUID = uuid4()
    dataloader.user_context["cpr_field"] = "employeeID"
    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(
            dn="CN=foo", employeeID="0101011221", objectGUID=str(objectGUID)
        ),
    ):
        return_value: dict = {
            "employees": [
                {"uuid": uuid},
            ],
            "itusers": [],
        }

        gql_client.execute.return_value = return_value

        output = await asyncio.gather(
            dataloader.find_mo_employee_uuid("CN=foo"),
        )
        assert output[0] == uuid

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(
            dn="CN=foo", employeeID="Ja", objectGUID=str(objectGUID)
        ),
    ):
        return_value = {
            "itusers": [
                {"objects": [{"employee_uuid": uuid}]},
            ]
        }

        gql_client.execute.return_value = return_value

        output = await asyncio.gather(dataloader.find_mo_employee_uuid("CN=foo"))
        assert output[0] == uuid


async def test_find_mo_employee_uuid_not_found(
    dataloader: DataLoader, gql_client: AsyncMock
):

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(
            dn="CN=foo", employeeID="0101011221", objectGUID=str(uuid4())
        ),
    ):
        gql_client.execute.return_value = {"employees": [], "itusers": []}

        output = await asyncio.gather(dataloader.find_mo_employee_uuid("CN=foo"))

        assert output[0] is None


async def test_find_mo_employee_uuid_multiple_matches(
    dataloader: DataLoader, gql_client: AsyncMock
):

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(
            dn="CN=foo", employeeID="0101011221", objectGUID=str(uuid4())
        ),
    ):
        gql_client.execute.return_value = {
            "employees": [{"uuid": uuid4()}, {"uuid": uuid4()}],
            "itusers": [],
        }

        with pytest.raises(MultipleObjectsReturnedException):
            await asyncio.gather(dataloader.find_mo_employee_uuid("CN=foo"))


async def test_load_mo_employee_not_found(
    dataloader: DataLoader, gql_client: AsyncMock
):
    gql_client.execute.return_value = {"employees": []}

    uuid = uuid4()

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(
            dataloader.load_mo_employee(uuid),
        )


async def test_load_mo_address_types_not_found(
    dataloader: DataLoader, gql_client_sync: MagicMock
):
    gql_client_sync.execute.return_value = {"facets": []}

    assert dataloader.load_mo_employee_address_types() == {}
    assert dataloader.load_mo_org_unit_address_types() == {}


def test_load_mo_it_systems(dataloader: DataLoader, gql_client_sync: MagicMock):
    uuid1 = uuid4()
    uuid2 = uuid4()

    return_value = {
        "itsystems": [
            {"user_key": "AD", "uuid": uuid1},
            {"user_key": "Office365", "uuid": uuid2},
        ]
    }

    gql_client_sync.execute.return_value = return_value

    output = dataloader.load_mo_it_systems()
    assert output[uuid1]["user_key"] == "AD"
    assert output[uuid2]["user_key"] == "Office365"


def test_load_mo_org_units(dataloader: DataLoader, gql_client_sync: MagicMock):
    uuid1 = str(uuid4())
    uuid2 = str(uuid4())

    return_value = {
        "org_units": [
            {"objects": [{"name": "Magenta Aps", "uuid": uuid1}]},
            {
                "objects": [
                    {
                        "name": "Magenta Aarhus",
                        "uuid": uuid2,
                        "parent": {"uuid": uuid1, "name": "Magenta Aps"},
                    }
                ]
            },
        ]
    }

    gql_client_sync.execute.return_value = return_value

    output = dataloader.load_mo_org_units()
    assert output[uuid1]["name"] == "Magenta Aps"
    assert output[uuid2]["name"] == "Magenta Aarhus"
    assert output[uuid2]["parent"]["uuid"] == uuid1


def test_load_mo_org_units_empty_response(
    dataloader: DataLoader, gql_client_sync: MagicMock
):

    return_value: dict = {"org_units": []}

    gql_client_sync.execute.return_value = return_value

    output = dataloader.load_mo_org_units()
    assert output == {}


def test_load_mo_it_systems_not_found(
    dataloader: DataLoader, gql_client_sync: MagicMock
):

    return_value: dict = {"itsystems": []}
    gql_client_sync.execute.return_value = return_value

    output = dataloader.load_mo_it_systems()
    assert output == {}


async def test_load_mo_it_user(dataloader: DataLoader, gql_client: AsyncMock):
    uuid1 = uuid4()
    uuid2 = uuid4()
    return_value = {
        "itusers": [
            {
                "objects": [
                    {
                        "user_key": "foo",
                        "validity": {"from": "2021-01-01", "to": None},
                        "employee_uuid": uuid1,
                        "itsystem_uuid": uuid2,
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    output = await asyncio.gather(
        dataloader.load_mo_it_user(uuid4()),
    )
    assert output[0].user_key == "foo"
    assert output[0].itsystem.uuid == uuid2
    assert output[0].person.uuid == uuid1  # type: ignore
    assert output[0].validity.from_date.strftime("%Y-%m-%d") == "2021-01-01"
    assert len(output) == 1


async def test_load_mo_engagement(dataloader: DataLoader, gql_client: AsyncMock):
    return_value = {
        "engagements": [
            {
                "objects": [
                    {
                        "user_key": "foo",
                        "validity": {"from": "2021-01-01", "to": None},
                        "extension_1": "extra info",
                        "extension_2": "more extra info",
                        "extension_3": None,
                        "extension_4": None,
                        "extension_5": None,
                        "extension_6": None,
                        "extension_7": None,
                        "extension_8": None,
                        "extension_9": None,
                        "extension_10": None,
                        "leave_uuid": uuid4(),
                        "primary_uuid": uuid4(),
                        "job_function_uuid": uuid4(),
                        "org_unit_uuid": uuid4(),
                        "engagement_type_uuid": uuid4(),
                        "employee_uuid": uuid4(),
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    output = await asyncio.gather(
        dataloader.load_mo_engagement(uuid4()),
    )
    assert output[0].user_key == "foo"
    assert output[0].validity.from_date.strftime("%Y-%m-%d") == "2021-01-01"
    assert output[0].extension_1 == "extra info"
    assert output[0].extension_2 == "more extra info"
    assert len(output) == 1


async def test_load_mo_it_user_not_found(dataloader: DataLoader, gql_client: AsyncMock):
    return_value: dict = {"itusers": []}

    gql_client.execute.return_value = return_value

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(
            dataloader.load_mo_it_user(uuid4()),
        )


async def test_load_mo_employee_it_users(dataloader: DataLoader, gql_client: AsyncMock):

    uuid1 = uuid4()
    uuid2 = uuid4()
    employee_uuid = uuid4()
    it_system_uuid = uuid4()

    return_value = {
        "employees": [
            {
                "objects": [
                    {
                        "itusers": [
                            {
                                "uuid": uuid1,
                                "itsystem_uuid": str(it_system_uuid),
                            },
                            {
                                "uuid": uuid2,
                                "itsystem_uuid": str(uuid4()),
                            },
                        ]
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    load_mo_it_user = AsyncMock()
    dataloader.load_mo_it_user = load_mo_it_user  # type: ignore

    await asyncio.gather(
        dataloader.load_mo_employee_it_users(employee_uuid, it_system_uuid),
    )

    load_mo_it_user.assert_called_once_with(uuid1)


async def test_load_mo_employees_in_org_unit(
    dataloader: DataLoader, gql_client: AsyncMock
):

    employee_uuid1 = uuid4()
    employee_uuid2 = uuid4()
    return_value = {
        "org_units": [
            {
                "objects": [
                    {
                        "engagements": [
                            {
                                "employee_uuid": employee_uuid1,
                            },
                            {
                                "employee_uuid": employee_uuid2,
                            },
                        ]
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    load_mo_employee = AsyncMock()
    dataloader.load_mo_employee = load_mo_employee  # type: ignore

    await asyncio.gather(
        dataloader.load_mo_employees_in_org_unit(uuid4()),
    )

    load_mo_employee.assert_any_call(employee_uuid1)
    load_mo_employee.assert_any_call(employee_uuid2)


async def test_load_mo_org_unit_addresses(
    dataloader: DataLoader, gql_client: AsyncMock
):

    address_uuid1 = uuid4()
    address_uuid2 = uuid4()
    return_value = {
        "org_units": [
            {
                "objects": [
                    {
                        "addresses": [
                            {
                                "uuid": address_uuid1,
                            },
                            {
                                "uuid": address_uuid2,
                            },
                        ]
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    load_mo_address = AsyncMock()
    dataloader.load_mo_address = load_mo_address  # type: ignore

    await asyncio.gather(
        dataloader.load_mo_org_unit_addresses(uuid4(), uuid4()),
    )

    load_mo_address.assert_any_call(address_uuid1)
    load_mo_address.assert_any_call(address_uuid2)


async def test_load_mo_employee_engagements(
    dataloader: DataLoader, gql_client: AsyncMock
):

    uuid1 = uuid4()
    employee_uuid = uuid4()

    return_value = {
        "employees": [
            {
                "objects": [
                    {
                        "engagements": [
                            {
                                "uuid": uuid1,
                            },
                        ]
                    }
                ]
            }
        ]
    }

    gql_client.execute.return_value = return_value

    load_mo_engagement = AsyncMock()
    dataloader.load_mo_engagement = load_mo_engagement  # type: ignore

    await asyncio.gather(
        dataloader.load_mo_employee_engagements(employee_uuid),
    )

    load_mo_engagement.assert_called_once_with(uuid1)


async def test_load_mo_employee_it_users_not_found(
    dataloader: DataLoader, gql_client: AsyncMock
):

    return_value: dict = {"employees": []}

    gql_client.execute.return_value = return_value

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(
            dataloader.load_mo_employee_it_users(uuid4(), uuid4()),
        )


async def test_is_primary(dataloader: DataLoader, gql_client: AsyncMock):

    return_value: dict = {"engagements": [{"objects": [{"is_primary": True}]}]}

    gql_client.execute.return_value = return_value

    primary = await asyncio.gather(dataloader.is_primary(uuid4()))
    assert primary == [True]


async def test_query_mo(dataloader: DataLoader, gql_client: AsyncMock):
    expected_output: dict = {"objects": []}
    gql_client.execute.return_value = expected_output

    query = gql(
        """
        query TestQuery {
          employees {
            uuid
          }
        }
        """
    )

    output = await asyncio.gather(dataloader.query_mo(query, raise_if_empty=False))
    assert output == [expected_output]

    with pytest.raises(NoObjectsReturnedException):
        await asyncio.gather(dataloader.query_mo(query, raise_if_empty=True))


async def test_query_mo_all_objects(dataloader: DataLoader, gql_client: AsyncMock):

    query = gql(
        """
        query TestQuery {
          employees (uuid:"uuid") {
            uuid
          }
        }
        """
    )

    expected_output: list = [{"objects": []}, {"objects": ["item1", "item2"]}]
    gql_client.execute.side_effect = expected_output

    output = await asyncio.gather(
        dataloader.query_past_future_mo(query, current_objects_only=False)
    )
    assert output == [expected_output[1]]

    query1 = print_ast(gql_client.execute.call_args_list[0].args[0])
    query2 = print_ast(gql_client.execute.call_args_list[1].args[0])

    # The first query attempts to request current objects only
    assert "from_date" not in query1
    assert "to_date" not in query1

    # If that fails, all objects are requested
    assert "from_date" in query2
    assert "to_date" in query2


def test_query_mo_sync(dataloader: DataLoader, gql_client_sync: MagicMock):
    expected_output: dict = {"objects": "items"}
    gql_client_sync.execute.return_value = expected_output

    query = gql(
        """
        query TestQuery {
          employees {
            uuid
          }
        }
        """
    )

    dataloader._check_if_empty = MagicMock()  # type: ignore
    output = dataloader.query_mo_sync(query, raise_if_empty=False)
    assert output == expected_output
    dataloader._check_if_empty.assert_not_called()

    output = dataloader.query_mo_sync(query)
    assert output == expected_output
    dataloader._check_if_empty.assert_called_once()


async def test_load_all_mo_objects(dataloader: DataLoader, gql_client: AsyncMock):

    return_values: list = [
        {"employees": [{"objects": [{"uuid": uuid4()}]}]},
        {"org_units": [{"objects": [{"uuid": uuid4()}]}]},
        {
            "addresses": [
                {
                    "objects": [
                        {
                            "uuid": uuid4(),
                            "employee_uuid": uuid4(),
                            "org_unit_uuid": None,
                        },
                    ]
                },
                {
                    "objects": [
                        {
                            "uuid": uuid4(),
                            "employee_uuid": None,
                            "org_unit_uuid": uuid4(),
                        },
                    ]
                },
            ]
        },
        {
            "itusers": [
                {
                    "objects": [
                        {
                            "uuid": uuid4(),
                            "employee_uuid": uuid4(),
                            "org_unit_uuid": None,
                        }
                    ]
                }
            ]
        },
        {
            "engagements": [
                {
                    "objects": [
                        {
                            "uuid": uuid4(),
                            "employee_uuid": uuid4(),
                            "org_unit_uuid": uuid4(),
                        }
                    ]
                }
            ],
        },
    ]

    gql_client.execute.side_effect = return_values

    output = await asyncio.gather(dataloader.load_all_mo_objects())

    all_objects = output[0]

    uuid = return_values[0]["employees"][0]["objects"][0]["uuid"]
    parent_uuid = uuid
    assert all_objects[0]["uuid"] == uuid
    assert all_objects[0]["object_type"] == ObjectType.EMPLOYEE
    assert all_objects[0]["service_type"] == ServiceType.EMPLOYEE
    assert all_objects[0]["payload"].uuid == parent_uuid
    assert all_objects[0]["payload"].object_uuid == uuid

    uuid = return_values[1]["org_units"][0]["objects"][0]["uuid"]
    parent_uuid = uuid
    assert all_objects[1]["uuid"] == uuid
    assert all_objects[1]["object_type"] == ObjectType.ORG_UNIT
    assert all_objects[1]["service_type"] == ServiceType.ORG_UNIT
    assert all_objects[1]["payload"].uuid == parent_uuid
    assert all_objects[1]["payload"].object_uuid == uuid

    uuid = return_values[2]["addresses"][0]["objects"][0]["uuid"]
    parent_uuid = return_values[2]["addresses"][0]["objects"][0]["employee_uuid"]
    assert all_objects[2]["uuid"] == uuid
    assert all_objects[2]["object_type"] == ObjectType.ADDRESS
    assert all_objects[2]["service_type"] == ServiceType.EMPLOYEE
    assert all_objects[2]["payload"].uuid == parent_uuid
    assert all_objects[2]["payload"].object_uuid == uuid

    uuid = return_values[2]["addresses"][1]["objects"][0]["uuid"]
    parent_uuid = return_values[2]["addresses"][1]["objects"][0]["org_unit_uuid"]
    assert all_objects[3]["uuid"] == uuid
    assert all_objects[3]["object_type"] == ObjectType.ADDRESS
    assert all_objects[3]["service_type"] == ServiceType.ORG_UNIT
    assert all_objects[3]["payload"].uuid == parent_uuid
    assert all_objects[3]["payload"].object_uuid == uuid

    uuid = return_values[3]["itusers"][0]["objects"][0]["uuid"]
    parent_uuid = return_values[3]["itusers"][0]["objects"][0]["employee_uuid"]
    assert all_objects[4]["uuid"] == uuid
    assert all_objects[4]["object_type"] == ObjectType.IT
    assert all_objects[4]["service_type"] == ServiceType.EMPLOYEE
    assert all_objects[4]["payload"].uuid == parent_uuid
    assert all_objects[4]["payload"].object_uuid == uuid

    uuid = return_values[4]["engagements"][0]["objects"][0]["uuid"]
    parent_uuid = return_values[4]["engagements"][0]["objects"][0]["employee_uuid"]
    assert all_objects[5]["uuid"] == uuid
    assert all_objects[5]["object_type"] == ObjectType.ENGAGEMENT
    assert all_objects[5]["service_type"] == ServiceType.EMPLOYEE
    assert all_objects[5]["payload"].uuid == parent_uuid
    assert all_objects[5]["payload"].object_uuid == uuid

    assert len(all_objects) == 6


async def test_load_all_mo_objects_add_validity(
    dataloader: DataLoader, gql_client: AsyncMock
):

    query_mo = AsyncMock()
    query_mo.return_value = {}
    dataloader.query_mo = query_mo  # type: ignore

    await dataloader.load_all_mo_objects(add_validity=True)
    query = query_mo.call_args[0][0].to_dict()
    assert "validity" in str(query)

    query_mo.reset_mock()

    await dataloader.load_all_mo_objects(add_validity=False)
    query = query_mo.call_args[0][0].to_dict()
    assert "validity" not in str(query)


async def test_load_all_mo_objects_specify_uuid(
    dataloader: DataLoader, gql_client: AsyncMock
):

    employee_uuid = uuid4()
    return_values: list = [
        {"employees": [{"objects": [{"uuid": employee_uuid}]}]},
        {"org_units": []},
        {"addresses": []},
        {"engagements": []},
        {"itusers": []},
    ]

    gql_client.execute.side_effect = return_values

    output = await asyncio.gather(
        dataloader.load_all_mo_objects(uuid=str(employee_uuid))
    )
    assert output[0][0]["uuid"] == employee_uuid
    assert len(output[0]) == 1


async def test_load_all_mo_objects_specify_uuid_multiple_results(
    dataloader: DataLoader, gql_client: AsyncMock
):

    uuid = uuid4()
    return_values: list = [
        {"employees": [{"objects": [{"uuid": uuid}]}]},
        {"org_units": [{"objects": [{"uuid": uuid}]}]},
        {"addresses": []},
        {"engagements": []},
        {"itusers": []},
    ]

    gql_client.execute.side_effect = return_values

    with pytest.raises(MultipleObjectsReturnedException):
        await dataloader.load_all_mo_objects(uuid=str(uuid))


async def test_load_all_mo_objects_invalid_query(
    dataloader: DataLoader, gql_client: AsyncMock
):

    # Return a single it-user, which belongs neither to an employee nor org-unit
    return_value: dict = {
        "employees": [],
        "org_units": [],
        "addresses": [],
        "itusers": [
            {
                "objects": [
                    {"uuid": uuid4(), "employee_uuid": None, "org_unit_uuid": None}
                ]
            }
        ],
        "engagements": [],
    }
    gql_client.execute.return_value = return_value

    with pytest.raises(InvalidQueryResponse):
        await asyncio.gather(dataloader.load_all_mo_objects())


async def test_load_all_mo_objects_TransportQueryError(
    dataloader: DataLoader, gql_client: AsyncMock
):

    employee_uuid = uuid4()
    org_unit_uuid = uuid4()
    return_values = [
        {"employees": [{"objects": [{"uuid": employee_uuid}]}]},
        {"org_units": [{"objects": [{"uuid": org_unit_uuid}]}]},
        TransportQueryError("foo"),
        TransportQueryError("foo"),
        TransportQueryError("foo"),
    ]
    gql_client.execute.side_effect = return_values
    with capture_logs() as cap_logs:

        output = await asyncio.gather(dataloader.load_all_mo_objects())
        warnings = [w for w in cap_logs if w["log_level"] == "warning"]
        assert len(warnings) == 0

        assert output[0][0]["uuid"] == employee_uuid
        assert output[0][1]["uuid"] == org_unit_uuid
        assert len(output[0]) == 2


async def test_load_all_mo_objects_only_TransportQueryErrors(
    dataloader: DataLoader, gql_client: AsyncMock
):

    return_values = [
        TransportQueryError("foo"),
        TransportQueryError("foo"),
        TransportQueryError("foo"),
        TransportQueryError("foo"),
        TransportQueryError("foo"),
    ]
    gql_client.execute.side_effect = return_values
    with capture_logs() as cap_logs:
        await asyncio.gather(dataloader.load_all_mo_objects())
        warnings = [w for w in cap_logs if w["log_level"] == "warning"]
        assert len(warnings) == 5


async def test_load_all_mo_objects_invalid_object_type_to_try(
    dataloader: DataLoader, gql_client: AsyncMock
):
    with pytest.raises(KeyError):
        await asyncio.gather(
            dataloader.load_all_mo_objects(
                object_types_to_try=("non_existing_object_type",)
            )
        )


async def test_shared_attribute(dataloader: DataLoader):

    converter = MagicMock()
    converter.mapping = {
        "mo_to_ldap": {
            "Employee": {"cpr_no": None, "name": None},
            "Address": {"cpr_no": None, "value": None},
        }
    }
    dataloader.user_context["converter"] = converter

    assert dataloader.shared_attribute("cpr_no") is True
    assert dataloader.shared_attribute("name") is False
    assert dataloader.shared_attribute("value") is False

    with pytest.raises(AttributeNotFound):
        dataloader.shared_attribute("non_existing_attribute")


async def test_load_mo_object(dataloader: DataLoader):
    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_all_mo_objects",
        return_value=["obj1"],
    ):
        result = await asyncio.gather(
            dataloader.load_mo_object("uuid", ObjectType.EMPLOYEE)
        )
        assert result[0] == "obj1"

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_all_mo_objects",
        return_value=[],
    ):
        result = await asyncio.gather(
            dataloader.load_mo_object("uuid", ObjectType.EMPLOYEE)
        )
        assert result[0] is None


async def test_modify_ldap(
    dataloader: DataLoader,
    sync_tool: AsyncMock,
    ldap_connection: MagicMock,
):

    ldap_connection.result = {"description": "success"}
    dn = "CN=foo"
    changes: dict = {"parameter_to_modify": [("MODIFY_ADD", "value_to_modify")]}

    # Validate that the entry is not in the ignore dict
    assert len(sync_tool.dns_to_ignore[dn]) == 0

    # Modify the entry. Validate that it is added to the ignore dict
    dataloader.modify_ldap(dn, changes)
    assert len(sync_tool.dns_to_ignore[dn]) == 1

    # Modify the same entry again. Validate that we still only ignore once
    dataloader.modify_ldap(dn, changes)
    assert len(sync_tool.dns_to_ignore[dn]) == 1

    # Validate that any old entries get cleaned, and a new one gets added
    sync_tool.dns_to_ignore.ignore_dict[dn.lower()] = [
        datetime.datetime(1900, 1, 1),
        datetime.datetime(1901, 1, 1),
    ]
    assert len(sync_tool.dns_to_ignore[dn]) == 2
    dataloader.modify_ldap(dn, changes)
    assert len(sync_tool.dns_to_ignore[dn]) == 1
    assert sync_tool.dns_to_ignore[dn][0] > datetime.datetime(1950, 1, 1)

    # Validate that our checks work
    with pytest.raises(
        InvalidChangeDict, match="Exactly one attribute can be changed at a time"
    ):
        changes = {
            "parameter_to_modify": [("MODIFY_ADD", "value_to_modify")],
            "another_parameter_to_modify": [("MODIFY_ADD", "value_to_modify")],
        }
        dataloader.modify_ldap(dn, changes)

    # Validate that our checks work
    with pytest.raises(
        InvalidChangeDict, match="Exactly one change can be submitted at a time"
    ):
        changes = {
            "parameter_to_modify": [
                ("MODIFY_ADD", "value_to_modify"),
                ("MODIFY_ADD", "another_value_to_modify"),
            ],
        }
        dataloader.modify_ldap(dn, changes)

    # Validate that our checks work
    with pytest.raises(
        InvalidChangeDict, match="Exactly one value can be changed at a time"
    ):
        changes = {
            "parameter_to_modify": [
                (
                    "MODIFY_ADD",
                    [
                        "value_to_modify",
                        "another_value_to_modify",
                    ],
                )
            ],
        }
        dataloader.modify_ldap(dn, changes)

    # Validate that empty lists are allowed
    changes = {"parameter_to_modify": [("MODIFY_REPLACE", [])]}
    dataloader.modify_ldap(dn, changes)
    ldap_connection.compare.assert_called_with(dn, "parameter_to_modify", "")

    # Simulate case where a value exists
    ldap_connection.compare.return_value = True
    with capture_logs() as cap_logs:
        dataloader.modify_ldap(dn, changes)
        messages = [w for w in cap_logs if w["log_level"] == "info"]

        assert re.match(".*already exists.*", str(messages[-1]["event"]))

    # DELETE statments should still be executed, even if a value exists
    changes = {"parameter_to_modify": [("MODIFY_DELETE", "foo")]}
    response = dataloader.modify_ldap(dn, changes)
    assert response == {"description": "success"}


async def test_modify_ldap_ou_not_in_ous_to_write_to(
    dataloader: DataLoader,
    sync_tool: AsyncMock,
    ldap_connection: MagicMock,
):
    dataloader.ou_in_ous_to_write_to = MagicMock()  # type: ignore
    dataloader.ou_in_ous_to_write_to.return_value = False

    assert dataloader.modify_ldap("CN=foo", {}) is None  # type: ignore


async def test_get_ldap_it_system_uuid(dataloader: DataLoader, converter: MagicMock):
    uuid = uuid4()
    converter.get_it_system_uuid.return_value = uuid
    assert dataloader.get_ldap_it_system_uuid() == uuid

    converter.get_it_system_uuid.side_effect = UUIDNotFoundException("UUID Not found")
    assert dataloader.get_ldap_it_system_uuid() is None


async def test_find_or_make_mo_employee_dn(
    dataloader: DataLoader, username_generator: MagicMock
):

    uuid_1 = uuid4()
    uuid_2 = uuid4()

    it_system_uuid = uuid4()
    dataloader.get_ldap_it_system_uuid = MagicMock()  # type: ignore
    dataloader.load_mo_employee_it_users = AsyncMock()  # type: ignore
    dataloader.load_mo_employee = AsyncMock()  # type: ignore
    dataloader.load_ldap_cpr_object = MagicMock()  # type: ignore
    dataloader.upload_mo_objects = AsyncMock()  # type: ignore
    dataloader.extract_unique_dns = MagicMock()  # type: ignore
    dataloader.get_ldap_objectGUID = MagicMock()  # type: ignore

    # Case where there is an IT-system that contains the DN
    dataloader.load_mo_employee.return_value = Employee(cpr_no=None)
    dataloader.load_mo_employee_it_users.return_value = []
    dataloader.get_ldap_it_system_uuid.return_value = it_system_uuid
    dataloader.extract_unique_dns.return_value = ["CN=foo,DC=bar"]
    dn = (await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4())))[0]
    assert dn == "CN=foo,DC=bar"

    # Same as above, but the it-system contains an invalid value
    dataloader.extract_unique_dns.return_value = []
    username_generator.generate_dn.return_value = "CN=generated_dn_1,DC=DN"
    dataloader.get_ldap_objectGUID.return_value = uuid_1
    dn = (await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4())))[0]
    uploaded_uuid = dataloader.upload_mo_objects.await_args_list[0].args[0][0].user_key
    assert dn == "CN=generated_dn_1,DC=DN"
    assert uploaded_uuid == str(uuid_1)
    dataloader.upload_mo_objects.reset_mock()

    # Same as above, but there are multiple IT-users
    dataloader.extract_unique_dns.return_value = ["CN=foo,DC=bar", "CN=foo2,DC=bar"]
    with pytest.raises(MultipleObjectsReturnedException):
        await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4()))

    # Case where there is no IT-system that contains the DN, but the cpr lookup succeeds
    dataloader.load_mo_employee.return_value = Employee(cpr_no="0101911234")
    dataloader.extract_unique_dns.return_value = []
    dataloader.load_ldap_cpr_object.return_value = LdapObject(
        dn="CN=dn_already_in_ldap,DC=foo"
    )
    dn = (await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4())))[0]
    assert dn == "CN=dn_already_in_ldap,DC=foo"

    # Same as above, but the cpr-lookup does not succeed
    dataloader.load_ldap_cpr_object.side_effect = NoObjectsReturnedException("foo")
    username_generator.generate_dn.return_value = "CN=generated_dn_2,DC=DN"
    dataloader.get_ldap_objectGUID.return_value = uuid_2
    dn = (await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4())))[0]
    uploaded_uuid = dataloader.upload_mo_objects.await_args_list[0].args[0][0].user_key
    assert dn == "CN=generated_dn_2,DC=DN"
    assert uploaded_uuid == str(uuid_2)
    dataloader.upload_mo_objects.reset_mock()

    # Same as above, but an it-system does not exist
    dataloader.get_ldap_it_system_uuid.return_value = None
    username_generator.generate_dn.return_value = "CN=generated_dn_3,DC=DN"
    dn = (await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4())))[0]
    assert dn == "CN=generated_dn_3,DC=DN"
    dataloader.upload_mo_objects.assert_not_awaited()
    dataloader.upload_mo_objects.reset_mock()

    # Same as above, but the user also has no cpr number
    dataloader.load_mo_employee.return_value = Employee(cpr_no=None)
    with pytest.raises(DNNotFound):
        await asyncio.gather(dataloader.find_or_make_mo_employee_dn(uuid4()))


def test_extract_unique_objectGUIDs(dataloader: DataLoader):

    ad_it_user_1 = ITUser.from_simplified_fields(
        str(uuid4()),
        uuid4(),
        datetime.datetime.today().strftime("%Y-%m-%d"),
        person_uuid=uuid4(),
    )
    ad_it_user_2 = ITUser.from_simplified_fields(
        str(uuid4()),
        uuid4(),
        datetime.datetime.today().strftime("%Y-%m-%d"),
        person_uuid=uuid4(),
    )
    ad_it_user_3 = ITUser.from_simplified_fields(
        "not_an_uuid",
        uuid4(),
        datetime.datetime.today().strftime("%Y-%m-%d"),
        person_uuid=uuid4(),
    )

    objectGUIDs = dataloader.extract_unique_objectGUIDs(
        [ad_it_user_1, ad_it_user_2, ad_it_user_3]
    )

    assert UUID(ad_it_user_1.user_key) in objectGUIDs
    assert UUID(ad_it_user_2.user_key) in objectGUIDs
    assert len(objectGUIDs) == 2


def test_extract_unique_dns(dataloader: DataLoader):

    dataloader.extract_unique_objectGUIDs = MagicMock()  # type: ignore
    dataloader.extract_unique_objectGUIDs.return_value = [uuid4(), uuid4()]

    dataloader.get_ldap_dn = MagicMock()  # type: ignore
    dataloader.get_ldap_dn.return_value = "CN=foo"

    dns = dataloader.extract_unique_dns([])

    assert len(dns) == 2
    assert dns[0] == "CN=foo"
    assert dns[1] == "CN=foo"


def test_get_ldap_dn(dataloader: DataLoader):
    with patch(
        "mo_ldap_import_export.dataloaders.single_object_search",
        return_value={"dn": "CN=foo"},
    ):
        assert dataloader.get_ldap_dn(uuid4()) == "CN=foo"


def test_get_ldap_objectGUID(dataloader: DataLoader):
    uuid = uuid4()
    dataloader.load_ldap_object = MagicMock()  # type: ignore
    dataloader.load_ldap_object.return_value = LdapObject(
        dn="foo", objectGUID=str(uuid)
    )

    assert dataloader.get_ldap_objectGUID("") == uuid


def test_load_ldap_attribute_values(dataloader: DataLoader):
    responses = [
        {"attributes": {"foo": 1}},
        {"attributes": {"foo": "2"}},
        {"attributes": {"foo": []}},
    ]
    with patch(
        "mo_ldap_import_export.dataloaders.paged_search",
        return_value=responses,
    ):
        values = dataloader.load_ldap_attribute_values("foo")
        assert "1" in values
        assert "2" in values
        assert "[]" in values
        assert len(values) == 3


def test_create_mo_class(dataloader: DataLoader):

    uuid = uuid4()

    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {"class_create": {"uuid": str(uuid)}}

    assert dataloader.create_mo_class("", "", uuid4()) == uuid


def test_update_mo_class(dataloader: DataLoader):

    uuid = uuid4()

    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {"class_update": {"uuid": str(uuid)}}

    assert dataloader.update_mo_class("", "", uuid4(), uuid4()) == uuid


def test_create_mo_job_function(dataloader: DataLoader):

    uuid1 = uuid4()
    uuid2 = uuid4()

    dataloader.load_mo_facet_uuid = MagicMock()  # type: ignore
    dataloader.load_mo_facet_uuid.return_value = uuid1

    dataloader.create_mo_class = MagicMock()  # type: ignore
    dataloader.create_mo_class.return_value = uuid2

    assert dataloader.create_mo_job_function("foo") == uuid2
    assert dataloader.create_mo_engagement_type("bar") == uuid2

    args = dataloader.create_mo_class.call_args_list[0].args

    assert args[0] == "foo"
    assert args[1] == "foo"
    assert args[2] == uuid1

    args = dataloader.create_mo_class.call_args_list[1].args

    assert args[0] == "bar"
    assert args[1] == "bar"
    assert args[2] == uuid1


def test_load_mo_facet_uuid(dataloader: DataLoader):

    uuid = uuid4()
    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {"facets": [{"uuid": str(uuid)}]}

    assert dataloader.load_mo_facet_uuid("") == uuid


def test_load_mo_facet_uuid_multiple_facets(dataloader: DataLoader):

    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {
        "facets": [{"uuid": str(uuid4())}, {"uuid": str(uuid4())}]
    }

    with pytest.raises(MultipleObjectsReturnedException):
        dataloader.load_mo_facet_uuid("")


def test_get_root_org(dataloader: DataLoader):
    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {"org": {"uuid": str(uuid4())}}

    assert type(dataloader.get_root_org()) == UUID


def test_create_mo_it_system(dataloader: DataLoader):
    dataloader.query_mo_sync = MagicMock()  # type: ignore
    dataloader.query_mo_sync.return_value = {"itsystem_create": {"uuid": str(uuid4())}}

    assert type(dataloader.create_mo_it_system("foo", "bar")) == UUID


def test_add_ldap_object(dataloader: DataLoader):
    dataloader.add_ldap_object("CN=foo", attributes={"foo": 2})
    dataloader.ldap_connection.add.assert_called_once()


def test_return_mo_employee_uuid_result(dataloader: DataLoader):
    uuid = uuid4()

    result: dict = {"employees": [], "itusers": []}
    assert dataloader._return_mo_employee_uuid_result(result) is None

    result = {"employees": [{"uuid": uuid}], "itusers": []}
    assert dataloader._return_mo_employee_uuid_result(result) == uuid

    result = {"itusers": [{"objects": [{"employee_uuid": uuid}]}]}
    assert dataloader._return_mo_employee_uuid_result(result) == uuid

    result = {
        "itusers": [
            {"objects": [{"employee_uuid": uuid}]},
            {"objects": [{"employee_uuid": uuid}]},
        ]
    }
    assert dataloader._return_mo_employee_uuid_result(result) == uuid

    result = {
        "itusers": [
            {"objects": [{"employee_uuid": uuid, "cpr_no": "010101-1234"}]},
            {"objects": [{"employee_uuid": uuid4(), "cpr_no": "010101-1234"}]},
        ]
    }
    with pytest.raises(MultipleObjectsReturnedException, match="010101-xxxx"):
        dataloader._return_mo_employee_uuid_result(result)

    result = {
        "employees": [
            {"uuid": uuid, "cpr_no": "010101-1234"},
            {"uuid": uuid4(), "cpr_no": "010101-1234"},
        ],
        "itusers": [],
    }
    with pytest.raises(MultipleObjectsReturnedException, match="010101-xxxx"):
        dataloader._return_mo_employee_uuid_result(result)


def test_ou_in_ous_to_write_to(dataloader: DataLoader):

    settings_mock = MagicMock()
    settings_mock.ldap_ous_to_write_to = ["OU=foo", "OU=mucki,OU=bar"]
    dataloader.user_context["settings"] = settings_mock

    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=foo,DC=k") is True
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=bar,DC=k") is False
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=mucki,OU=bar,DC=k") is True
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,DC=k") is False

    settings_mock.ldap_ous_to_write_to = [""]
    dataloader.user_context["settings"] = settings_mock

    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=foo,DC=k") is True
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=bar,DC=k") is True
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,OU=mucki,OU=bar,DC=k") is True
    assert dataloader.ou_in_ous_to_write_to("CN=Tobias,DC=k") is True
