# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
from yarl import URL

from .util import execute


def gen_employee(
    uuid: Optional[UUID] = None,
    user_key: str = "user_key",
    first_name: str = "first_name",
    last_name: str = "last_name",
    from_time: str = "1970-01-01 00:00:00+01",
) -> Dict[str, Any]:
    uuid = uuid or uuid4()
    virkning = {"from": from_time, "to": "infinity"}
    employee = {
        "id": str(uuid),
        "registreringer": [
            {
                "attributter": {
                    "brugeregenskaber": [
                        {"brugervendtnoegle": user_key, "virkning": virkning}
                    ],
                    "brugerudvidelser": [
                        {
                            "fornavn": first_name,
                            "efternavn": last_name,
                            "virkning": virkning,
                        }
                    ],
                },
                "tilstande": {
                    "brugergyldighed": [{"gyldighed": "Aktiv", "virkning": virkning}]
                },
                "relationer": {
                    "tilknyttedepersoner": [
                        {"urn": "urn:dk:cpr:person:0101700000", "virkning": virkning}
                    ],
                },
            }
        ],
    }
    return employee


def mock_employee(aioresponses, *args, repeat=False, **kwargs) -> UUID:
    employee = gen_employee()
    aioresponses.get(
        URL("http://mox/organisation/bruger"),
        payload={"results": [[employee]]},
        repeat=repeat,
    )
    return employee["id"]


@pytest.mark.asyncio
async def test_query_employees(aioresponses):
    """Test that we are able to query our employee."""
    uuid = mock_employee(aioresponses)

    query = "query { employees { uuid, cpr_no, user_key, givenname, surname }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert sum(len(v) for v in aioresponses.requests.values()) == 1

    assert result.errors is None
    assert result.data["employees"] == [
        {
            "uuid": str(uuid),
            "cpr_no": "0101700000",
            "user_key": "user_key",
            "givenname": "first_name",
            "surname": "last_name",
        }
    ]


@pytest.mark.asyncio
async def test_query_employees_by_uuids(aioresponses):
    """Test that we are able to query our employee by UUID (bulk)."""
    uuid = mock_employee(aioresponses)

    query = """
        query TestQuery($uuid: UUID!) {
            employees(uuids: [$uuid]) {
                uuid, cpr_no, user_key, givenname, surname
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid)})

    # We expect only one outgoing request to be done
    assert sum(len(v) for v in aioresponses.requests.values()) == 1

    assert result.errors is None
    assert result.data["employees"] == [
        {
            "uuid": str(uuid),
            "cpr_no": "0101700000",
            "user_key": "user_key",
            "givenname": "first_name",
            "surname": "last_name",
        }
    ]


@pytest.mark.asyncio
async def test_query_employees_by_unknown_uuid(aioresponses):
    """Test that we get an empty response when querying with an unknown uuid."""
    mock_employee(aioresponses)

    query = """
        query TestQuery($uuid: UUID!) {
            employees(uuids: [$uuid]) {
                uuid
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid4())})

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employees"] == []


@pytest.mark.asyncio
async def test_query_no_employees(aioresponses):
    """Test that we are able to query our employees, and get an empty result."""
    aioresponses.get(
        URL("http://mox/organisation/bruger"),
        payload={"results": []},
        repeat=True,
    )

    query = "query { employees { uuid }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert sum(len(v) for v in aioresponses.requests.values()) == 1

    assert result.errors is None
    assert result.data["employees"] == []


@pytest.mark.asyncio
async def test_query_multiple_employees(aioresponses):
    """Test that we are able to query multiple employees at once."""
    employees = [gen_employee(), gen_employee(), gen_employee()]
    aioresponses.get(
        URL("http://mox/organisation/bruger"),
        payload={"results": [employees]},
        repeat=True,
    )

    query = "query { employees { uuid }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert sum(len(v) for v in aioresponses.requests.values()) == 1

    assert result.errors is None
    assert result.data["employees"] == [
        {"uuid": employee["id"]} for employee in employees
    ]
