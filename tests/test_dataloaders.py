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
from fastramqpi.context import Context
from more_itertools import collapse
from ramodels.mo.employee import Employee

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.dataloaders import configure_dataloaders
from mo_ldap_import_export.dataloaders import Dataloaders
from mo_ldap_import_export.dataloaders import get_ldap_attributes
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.dataloaders import make_overview_entry
from mo_ldap_import_export.exceptions import CprNoNotFound
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldap import paged_search


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
    monkeypatch.setenv("LDAP_USER_CLASS", "user")

    return Settings()


@pytest.fixture
def context(
    ldap_connection: MagicMock,
    gql_client: AsyncMock,
    model_client: AsyncMock,
    settings: Settings,
    cpr_field: str,
) -> Context:

    return {
        "user_context": {
            "settings": settings,
            "ldap_connection": ldap_connection,
            "gql_client": gql_client,
            "model_client": model_client,
            "cpr_field": cpr_field,
        },
    }


@pytest.fixture
def dataloaders(
    context: Context,
) -> Iterator[Dataloaders]:
    """Fixture to construct a dataloaders object using fixture mocks.

    Yields:
        Dataloaders with mocked clients.
    """
    dataloaders = configure_dataloaders(context)
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

    expected_result = [LdapObject(dn=dn, **ldap_attributes)]

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
        assert e.status_code == 404


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
        assert e.status_code == 404


async def test_load_ldap_employees(
    dataloaders: Dataloaders, ldap_attributes: dict
) -> None:
    """Test that test_load_ldap_employees works as expected."""

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_results = [LdapObject(dn=dn, **ldap_attributes)]

    # Get result from dataloader
    with patch(
        "mo_ldap_import_export.dataloaders.paged_search",
        return_value=[mock_ldap_response(ldap_attributes, dn)],
    ):
        output = await asyncio.gather(
            dataloaders.ldap_employees_loader.load(0),
        )

    assert output == [expected_results]


async def test_modify_ldap_employee(
    ldap_connection: MagicMock,
    dataloaders: Dataloaders,
    ldap_attributes: dict,
) -> None:

    employee = LdapObject(
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


async def test_create_invalid_ldap_employee(
    ldap_connection: MagicMock,
    dataloaders: Dataloaders,
    ldap_attributes: dict,
    cpr_field: str,
) -> None:

    ldap_attributes_without_cpr_field = {
        key: value for key, value in ldap_attributes.items() if key != cpr_field
    }

    employee = LdapObject(
        dn="CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev",
        **ldap_attributes_without_cpr_field
    )

    # Get result from dataloader
    try:
        await asyncio.gather(
            dataloaders.ldap_employees_uploader.load(employee),
        )
    except CprNoNotFound as e:
        assert e.status_code == 404
        assert type(e) == CprNoNotFound


async def test_create_ldap_employee(
    ldap_connection: MagicMock,
    dataloaders: Dataloaders,
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
    output = get_ldap_attributes(ldap_connection, str(levels[0]))
    assert output == expected_output


async def test_paged_search(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_results = [mock_ldap_response(ldap_attributes, dn)]

    # Mock LDAP connection
    ldap_connection.response = expected_results

    # Simulate three pages
    cookies = [bytes("first page", "utf-8"), bytes("second page", "utf-8"), None]
    results = iter(
        [
            {
                "controls": {"1.2.840.113556.1.4.319": {"value": {"cookie": cookie}}},
                "description": "OK",
            }
            for cookie in cookies
        ]
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    # Every time a search is performed, point to the next page.
    ldap_connection.search.side_effect = set_new_result

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    output = paged_search(context, searchParameters)

    assert output == expected_results * len(cookies)


async def test_invalid_paged_search(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    ldap_connection.result = {
        "description": "operationsError",
    }

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    output = paged_search(context, searchParameters)

    assert output == []


async def test_make_overview_entry():

    attributes = ["foo", "bar"]
    superiors = ["state", "country", "world"]
    entry = make_overview_entry(attributes, superiors)

    assert entry == {"attributes": attributes, "superiors": superiors}


async def test_get_overview(dataloaders: Dataloaders):

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
        output = (
            await asyncio.gather(
                dataloaders.ldap_overview_loader.load([1]),
            )
        )[0]

    assert output == {
        "object1": {"attributes": ["attr1", "attr2"], "superiors": ["sup1", "sup2"]}
    }


async def test_get_populated_overview(dataloaders: Dataloaders):

    overview = {
        "object1": {"attributes": ["attr1", "attr2"], "superiors": ["sup1", "sup2"]}
    }

    responses = [
        {
            "attributes": {
                "attr1": "foo",  # We expect this attribute in the output
                "attr2": None,  # But not this one
            }
        }
    ]

    with patch(
        "mo_ldap_import_export.dataloaders.load_ldap_overview",
        return_value=[overview],
    ), patch(
        "mo_ldap_import_export.dataloaders.paged_search",
        return_value=responses,
    ):
        output = (
            await asyncio.gather(
                dataloaders.ldap_populated_overview_loader.load([1]),
            )
        )[0]

    assert output == {
        "object1": {"attributes": ["attr1"], "superiors": ["sup1", "sup2"]}
    }
