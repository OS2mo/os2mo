# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import re
from uuid import UUID
from uuid import uuid4
from typing import Any
from typing import Dict
from typing import Optional

import pytest

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


def mock_employee(aioresponses, *args, **kwargs) -> UUID:
    employee = gen_employee()

    pattern = re.compile(r"^http://mox/organisation/bruger.*$")
    aioresponses.get(pattern, payload={"results": [[employee]]})

    return employee["id"]


@pytest.mark.asyncio
async def test_query_employees(aioresponses):
    """Test that we are able to query our employee."""
    uuid = mock_employee(aioresponses)

    query = "query { employees { uuid, cpr_no, user_key, name }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employees"] == [
        {
            "uuid": str(uuid),
            "cpr_no": "0101700000",
            "user_key": "user_key",
            "name": "first_name last_name",
        }
    ]


@pytest.mark.asyncio
async def test_query_employees_by_uuids(aioresponses):
    """Test that we are able to query our employee by UUID (bulk)."""
    uuid = mock_employee(aioresponses)

    query = """
        query TestQuery($uuid: UUID!) {
            employees_by_uuids(uuids: [$uuid]) {
                uuid, cpr_no, user_key, name
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid)})

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employees_by_uuids"] == [
        {
            "uuid": str(uuid),
            "cpr_no": "0101700000",
            "user_key": "user_key",
            "name": "first_name last_name",
        }
    ]


@pytest.mark.asyncio
async def test_query_employee_by_uuid(aioresponses):
    """Test that we are able to query our employee by UUID (single)."""
    uuid = mock_employee(aioresponses)

    query = """
        query TestQuery($uuid: UUID!) {
            employee_by_uuid(uuid: $uuid) {
                uuid, cpr_no, user_key, name
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid)})

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employee_by_uuid"] == {
        "uuid": str(uuid),
        "cpr_no": "0101700000",
        "user_key": "user_key",
        "name": "first_name last_name",
    }


@pytest.mark.asyncio
async def test_query_no_employees(aioresponses):
    """Test that we are able to query our employees, and get an empty result."""
    pattern = re.compile(r"^http://mox/organisation/bruger.*$")
    aioresponses.get(pattern, payload={"results": []})

    query = "query { employees { uuid }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employees"] == []


@pytest.mark.asyncio
async def test_query_multiple_employees(aioresponses):
    """Test that we are able to query multiple employees at once."""
    employees = [gen_employee(), gen_employee(), gen_employee()]
    pattern = re.compile(r"^http://mox/organisation/bruger.*$")
    aioresponses.get(pattern, payload={"results": [employees]})

    query = "query { employees { uuid }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert len(aioresponses.requests) == 1

    assert result.errors is None
    assert result.data["employees"] == [
        {"uuid": employee["id"]} for employee in employees
    ]
