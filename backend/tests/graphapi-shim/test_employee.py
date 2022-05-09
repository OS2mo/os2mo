# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import re
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
import respx
from httpx import Response

from tests.graphapi.test_organisation import mock_organisation
from tests.util import patch_is_graphql
from tests.util import patch_query_args

from mora import exceptions
from mora.common import get_connector
from mora.service.employee import EmployeeDetails
from mora.service.employee import get_one_employee
from mora.service.shimmed.employee import get_employee


def gen_employee(
    uuid: Optional[UUID] = None,
    user_key: str = "user_key",
    first_name: str = "first_name",
    last_name: str = "last_name",
    from_time: str = "1970-01-01 00:00:00+01",
    seniority: Optional[str] = None,
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
                            "seniority": seniority,
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


def mock_employee(respx, **kwargs) -> UUID:
    employee = gen_employee(**kwargs)
    respx.get(
        "http://mox/organisation/bruger",
    ).mock(return_value=Response(200, json={"results": [[employee]]}))
    return employee["id"]


async def old_get_employee(id: UUID, only_primary_uuid: Optional[bool] = None) -> dict:
    """Old non-shim implementation of get_employee, for equivalence testing."""
    c = get_connector()
    r = await get_one_employee(
        c,
        id,
        user=None,
        details=EmployeeDetails.FULL,
        only_primary_uuid=only_primary_uuid,
    )
    if not r:
        exceptions.ErrorCodes.E_USER_NOT_FOUND()
    return r


@pytest.mark.parametrize("only_primary_uuid", [True, False])
@pytest.mark.parametrize("employee_exists", [True, False])
@pytest.mark.asyncio
@respx.mock
async def test_shim_equivalence(only_primary_uuid, employee_exists):
    """Ensure that the shim implementation behaves exactly like the old one did."""
    if employee_exists:
        uuid = mock_employee(respx)
    else:
        pattern = re.compile(r"^http://mox/organisation/bruger.*$")
        respx.get(pattern).mock(return_value=Response(200, json={"results": [[]]}))
        uuid = uuid4()

    mock_organisation(respx)
    new_exception = None
    old_exception = None

    with patch_query_args():
        with patch_is_graphql(True):
            try:
                new_result = await get_employee(uuid, only_primary_uuid, at=None)
            except Exception as exception:
                new_exception = exception
            try:
                old_result = await old_get_employee(uuid, only_primary_uuid)
            except Exception as exception:
                old_exception = exception

    # Neither of these should ever occur
    if new_exception and not old_exception:
        raise new_exception
    if not new_exception and old_exception:
        raise old_exception

    if new_exception and old_exception:
        assert new_exception.status_code == old_exception.status_code
        assert new_exception.detail == old_exception.detail
    else:
        assert new_result == old_result
