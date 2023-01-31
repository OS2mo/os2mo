# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
import asyncio
import re
from collections.abc import Iterator
from typing import Collection
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ldap3.core.exceptions import LDAPInvalidValueError
from ramodels.mo.details.address import Address
from ramodels.mo.employee import Employee
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import CprNoNotFound
from mo_ldap_import_export.exceptions import NoObjectsReturnedException


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
        yield MagicMock()


@pytest.fixture
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def gql_client_sync() -> Iterator[MagicMock]:
    yield MagicMock()


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

    return Settings()


@pytest.fixture
def converter() -> MagicMock:
    converter_mock = MagicMock()
    converter_mock.find_ldap_object_class.return_value = "user"
    return converter_mock


@pytest.fixture
def context(
    ldap_connection: MagicMock,
    gql_client: AsyncMock,
    model_client: AsyncMock,
    settings: Settings,
    cpr_field: str,
    converter: MagicMock,
    gql_client_sync: MagicMock,
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
    cpr_no = "0101012002"

    expected_result = LdapObject(dn=dn, **ldap_attributes)
    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    output = dataloader.load_ldap_cpr_object(cpr_no, "Employee")

    assert output == expected_result


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
            dataloader.upload_ldap_object(employee, "user"),
        )

    assert output == [
        [good_response] * len(allowed_parameters_to_upload)
        + [bad_response] * len(disallowed_parameters_to_upload)
    ]


async def test_create_invalid_ldap_employee(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    ldap_attributes: dict,
    cpr_field: str,
) -> None:

    ldap_attributes_without_cpr_field = {
        key: value for key, value in ldap_attributes.items() if key != cpr_field
    }

    employee = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        **ldap_attributes_without_cpr_field,
    )

    # Get result from dataloader
    try:
        await asyncio.gather(
            dataloader.upload_ldap_object(employee, "user"),
        )
    except CprNoNotFound as e:
        assert e.status_code == 404
        assert type(e) == CprNoNotFound


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
        dataloader.upload_ldap_object(address, "user"),
    )

    changes = {"postalAddress": [("MODIFY_ADD", "foo")]}
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
            dataloader.upload_ldap_object(ldap_object, "user"),
        )

        warnings = [w for w in cap_logs if w["log_level"] == "warning"]
        assert re.match(
            "Invalid value",
            str(warnings[-1]["event"]),
        )


async def test_create_ldap_employee(
    ldap_connection: MagicMock,
    dataloader: DataLoader,
    ldap_attributes: dict,
    cpr_field: str,
) -> None:

    employee = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev", **ldap_attributes
    )

    non_existing_object_response = {
        "result": 0,
        "description": "noSuchObject",
        "dn": "",
        "message": "",
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

    parameters_to_upload = [k for k in employee.dict().keys() if k not in ["dn"]]

    results = iter(
        [non_existing_object_response] + [good_response] * len(parameters_to_upload)
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    ldap_connection.modify.side_effect = set_new_result

    # Get result from dataloader
    output = await asyncio.gather(
        dataloader.upload_ldap_object(employee, "user"),
    )

    assert output == [[good_response] * len(parameters_to_upload)]


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
        }
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

    output = dataloader.load_mo_address_types()
    assert output[uuid]["name"] == name


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
        "visibility": {"uuid": uuid},
    }

    # Note that 'Address' requires 'person' to be a dict
    expected_result = Address(**address_dict.copy())

    # While graphQL returns it as a list with length 1
    address_dict["person"] = [{"cpr_no": "0101012002", "uuid": uuid}]
    address_dict["address_type"]["user_key"] = "address"
    address_dict["value2"] = None
    address_dict["visibility_uuid"] = uuid

    gql_client.execute.return_value = {
        "addresses": [
            {"objects": [address_dict]},
        ]
    }

    output = await asyncio.gather(
        dataloader.load_mo_address(uuid),
    )

    address_metadata = {
        "address_type_user_key": address_dict["address_type"]["user_key"],
        "employee_cpr_no": address_dict["person"][0]["cpr_no"],
    }

    assert output[0][0] == expected_result
    assert output[0][1] == address_metadata


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

    ldap_objects = [
        # LdapObject(dn="foo", value="New address"),
        LdapObject(dn="foo", value="Old address"),
    ]

    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(dn="foo", value=["New address", "Old address"]),
    ):
        dataloader.cleanup_attributes_in_ldap(ldap_objects)

        changes = {"value": [("MODIFY_DELETE", "Old address")]}
        assert dataloader.ldap_connection.modify.called_once_with("foo", changes)

    # Simulate impossible case - where the value field of the ldap object on the server
    # is not a list
    with patch(
        "mo_ldap_import_export.dataloaders.DataLoader.load_ldap_object",
        return_value=LdapObject(dn="foo", value="New address"),
    ):
        with pytest.raises(Exception):
            dataloader.cleanup_attributes_in_ldap(ldap_objects)

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
    return_value = {
        "employees": [
            {"uuid": uuid},
        ]
    }

    gql_client.execute.return_value = return_value
    gql_client_sync.execute.return_value = return_value

    output = await asyncio.gather(
        dataloader.find_mo_employee_uuid("0101011221"),
    )
    assert output[0] == uuid

    output_sync = dataloader.find_mo_employee_uuid_sync("0101011221")
    assert output_sync == uuid


async def test_find_mo_employee_uuid_not_found(
    dataloader: DataLoader, gql_client: AsyncMock
):
    gql_client.execute.return_value = {"employees": []}

    output = await asyncio.gather(
        dataloader.find_mo_employee_uuid("0101011221"),
    )

    assert output[0] is None


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

    output = dataloader.load_mo_address_types()
    assert output == {}


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
    assert output[0].person.uuid == uuid1
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
