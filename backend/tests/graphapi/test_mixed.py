# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from yarl import URL

from .test_employees import gen_employee
from .test_employees import mock_employee
from .test_organisation import mock_organisation
from .util import execute


@pytest.mark.asyncio
async def test_query_employees_lazy_organisation(aioresponses):
    """Test that we are able to query lazy fields."""
    org_uuid = mock_organisation(aioresponses)
    employee_uuid = mock_employee(aioresponses)

    # org is a lazy field here
    query = "query { employees { uuid, cpr_no, user_key }, org { uuid, name } }"
    result = await execute(query)

    # We expect only two outgoing request to be done (one for employee, one for org)
    assert sum(len(v) for v in aioresponses.requests.values()) == 2

    assert result.errors is None
    assert result.data["employees"] == [
        {
            "uuid": str(employee_uuid),
            "cpr_no": "0101700000",
            "user_key": "user_key",
        }
    ]
    assert result.data["org"] == {
        "uuid": str(org_uuid),
        "name": "name",
    }


@pytest.mark.asyncio
async def test_query_multiple_employees_lazy_organisation(aioresponses):
    """Test that we are able to query multiple employees at once with lazy fields."""
    org_uuid = mock_organisation(aioresponses)

    employees = [gen_employee(), gen_employee(), gen_employee()]
    aioresponses.get(
        URL("http://mox/organisation/bruger"),
        payload={"results": [employees]},
        repeat=True,
    )

    # org is a lazy field here
    query = "query { employees { uuid }, org { uuid } }"
    result = await execute(query)

    # We expect only two outgoing request to be done (one for employees, one for org)
    assert sum(len(v) for v in aioresponses.requests.values()) == 2

    assert result.errors is None
    assert result.data["employees"] == [
        {"uuid": employee["id"]} for employee in employees
    ]
    assert result.data["org"] == {
        "uuid": str(org_uuid),
    }
