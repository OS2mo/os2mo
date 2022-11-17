# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
"""Test dataloaders."""
import asyncio
from collections.abc import Iterator
from typing import Collection
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from more_itertools import collapse
from ramodels.mo.employee import Employee

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.dataloaders import configure_dataloaders
from mo_ldap_import_export.dataloaders import Dataloaders
from mo_ldap_import_export.dataloaders import get_ldap_attributes
from mo_ldap_import_export.dataloaders import LdapEmployee
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException


@pytest.fixture()
def ldap_attributes() -> dict:
    return {"department": None, "name": "John", "employeeID": "0101011234"}


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
    monkeypatch.setenv("LDAP_ORGANIZATIONAL_UNIT", "OU=Magenta")
    return Settings()


@pytest.fixture
def dataloaders(
    ldap_connection: MagicMock,
    gql_client: AsyncMock,
    model_client: AsyncMock,
    settings: Settings,
    cpr_field: str,
) -> Iterator[Dataloaders]:
    """Fixture to construct a dataloaders object using fixture mocks.

    Yields:
        Dataloaders with mocked clients.
    """
    dataloaders = configure_dataloaders(
        {
            "user_context": {
                "settings": settings,
                "ldap_connection": ldap_connection,
                "gql_client": gql_client,
                "model_client": model_client,
                "cpr_field": cpr_field,
            },
        }
    )
    yield dataloaders


def mock_ldap_response(ldap_attributes: dict, dn: str) -> dict[str, Collection[str]]:

    expected_attributes = ldap_attributes.keys()
    inner_dict = ldap_attributes

    for attribute in expected_attributes:
        if attribute not in inner_dict.keys():
            inner_dict[attribute] = None

    response = {"dn": dn, "type": "searchResEntry", "attributes": inner_dict}

    return response


async def test_load_ldap_employee(
    ldap_connection: MagicMock, dataloaders: Dataloaders, ldap_attributes: dict
) -> None:
    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"
    cpr = "0101011234"

    expected_result = [LdapEmployee(dn=dn, cpr=cpr, **ldap_attributes)]

    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    output = await asyncio.gather(
        dataloaders.ldap_employee_loader.load(dn),
    )

    assert output == expected_result


async def test_load_ldap_employee_empty_list(
    ldap_connection: MagicMock, dataloaders: Dataloaders, ldap_attributes: dict
) -> None:
    """
    Simulate case where the department is an empty list
    """
    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"
    cpr = "0101011234"

    ldap_attributes["department"] = None
    expected_result = [LdapEmployee(dn=dn, cpr=cpr, **ldap_attributes)]

    ldap_attributes["department"] = []
    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    output = await asyncio.gather(
        dataloaders.ldap_employee_loader.load(dn),
    )

    assert output == expected_result


async def test_load_ldap_employee_multiple_results(
    ldap_connection: MagicMock, dataloaders: Dataloaders, ldap_attributes: dict
) -> None:
    # Mock data
    dn = "DC=ad,DC=addev"

    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)] * 20

    try:
        await asyncio.gather(
            dataloaders.ldap_employee_loader.load(dn),
        )
    except Exception as e:
        assert type(e) == MultipleObjectsReturnedException


async def test_load_ldap_employee_no_results(
    ldap_connection: MagicMock, dataloaders: Dataloaders
) -> None:

    ldap_connection.response = []
    dn = "foo"

    try:
        await asyncio.gather(
            dataloaders.ldap_employee_loader.load(dn),
        )
    except Exception as e:
        assert type(e) == NoObjectsReturnedException


async def test_load_ldap_employees(
    ldap_connection: MagicMock, dataloaders: Dataloaders, ldap_attributes: dict
) -> None:
    """Test that load_organizationalPersons works as expected."""

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"
    cpr = "0101011234"

    expected_results = [LdapEmployee(dn=dn, cpr=cpr, **ldap_attributes)]

    # Mock LDAP connection
    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    # Simulate three pages
    cookies = [bytes("first page", "utf-8"), bytes("second page", "utf-8"), None]
    results = iter(
        [
            {"controls": {"1.2.840.113556.1.4.319": {"value": {"cookie": cookie}}}}
            for cookie in cookies
        ]
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    # Every time a search is performed, point to the next page.
    ldap_connection.search.side_effect = set_new_result

    # Get result from dataloader
    output = await asyncio.gather(
        dataloaders.ldap_employees_loader.load(0),
    )

    assert output == [expected_results * len(cookies)]


async def test_modify_ldap_employee(
    ldap_connection: MagicMock,
    dataloaders: Dataloaders,
    ldap_attributes: dict,
) -> None:

    employee = LdapEmployee(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        cpr="0101011234",
        **ldap_attributes
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
        "mo_ldap_import_export.dataloaders.load_ldap_employee", return_value=[employee]
    ):
        output = await asyncio.gather(
            dataloaders.ldap_employees_uploader.load(employee),
        )

    assert output == [
        [good_response] * len(allowed_parameters_to_upload)
        + [bad_response] * len(disallowed_parameters_to_upload)
    ]


async def test_create_ldap_employee(
    ldap_connection: MagicMock,
    dataloaders: Dataloaders,
    ldap_attributes: dict,
    cpr_field: str,
) -> None:

    # Test to see if the cpr field is added. Even if not supplied in the attributes
    ldap_attributes_without_cpr_field = {
        key: value for key, value in ldap_attributes.items() if key != cpr_field
    }

    employee = LdapEmployee(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        cpr="0101011234",
        **ldap_attributes_without_cpr_field
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

    parameters_to_upload = [k for k in employee.dict().keys() if k not in ["dn", "cpr"]]
    parameters_to_upload += [cpr_field]

    results = iter(
        [non_existing_object_response] + [good_response] * len(parameters_to_upload)
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    ldap_connection.modify.side_effect = set_new_result

    # Get result from dataloader
    output = await asyncio.gather(
        dataloaders.ldap_employees_uploader.load(employee),
    )

    assert output == [[good_response] * len(parameters_to_upload)]


async def test_load_mo_employees(
    dataloaders: Dataloaders, gql_client: AsyncMock
) -> None:

    cpr_nos = ["1407711900", "0910443755", "1904433310"]
    uuids = [uuid4() for i in range(3)]

    gql_client.execute.return_value = {
        "employees": [
            {"objects": [{"cpr_no": cpr_nos[0], "uuid": uuids[0]}]},
            {
                "objects": [
                    {"cpr_no": cpr_nos[1], "uuid": uuids[1]},
                    {"cpr_no": cpr_nos[2], "uuid": uuids[2]},
                ]
            },
        ]
    }

    expected_results = []
    for cpr_no, uuid in zip(cpr_nos, uuids):
        expected_results.append(Employee(**{"cpr_no": cpr_no, "uuid": uuid}))

    output = await asyncio.gather(
        dataloaders.mo_employees_loader.load(0),
    )

    assert output == [expected_results]


async def test_load_mo_employee(
    dataloaders: Dataloaders, gql_client: AsyncMock
) -> None:

    cpr_no = "1407711900"
    uuid = uuid4()

    gql_client.execute.return_value = {
        "employees": [
            {"objects": [{"cpr_no": cpr_no, "uuid": uuid}]},
        ]
    }

    expected_result = [Employee(**{"cpr_no": cpr_no, "uuid": uuid})]

    output = await asyncio.gather(
        dataloaders.mo_employee_loader.load(uuid),
    )

    assert output == expected_result


async def test_upload_mo_employee(
    model_client: AsyncMock, dataloaders: Dataloaders
) -> None:
    """Test that test_upload_mo_employee works as expected."""
    model_client.upload.return_value = ["1", None, "3"]

    results = await asyncio.gather(
        dataloaders.mo_employee_uploader.load(1),
        dataloaders.mo_employee_uploader.load(2),
        dataloaders.mo_employee_uploader.load(3),
    )
    assert results == ["1", None, "3"]
    model_client.upload.assert_called_with([1, 2, 3])


async def test_get_ldap_attributes():
    ldap_connection = MagicMock()

    # Simulate 3 levels
    levels = ["bottom", "middle", "top", None]
    expected_attributes = [["mama", "papa"], ["brother", "sister"], ["wife"], None]

    # We expect only the first two levels as output. 'top' is not taken into account
    expected_output = list(collapse(expected_attributes[:2]))

    # Format object_classes dict
    object_classes = {}
    for i in range(len(levels) - 1):
        schema = MagicMock()

        schema.may_contain = expected_attributes[i]
        schema.superior = levels[i + 1]
        object_classes[levels[i]] = schema

    # Add to mock
    ldap_connection.server.schema.object_classes = object_classes

    # test the function
    output = get_ldap_attributes(ldap_connection, levels[0])
    assert output == expected_output
