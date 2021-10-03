# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import re
from uuid import uuid4
from uuid import UUID
from typing import Optional

import pytest

from mora import exceptions
from mora.service.employee import get_one_employee
from mora.service.employee import EmployeeDetails
from mora.service.shimmed import get_employee
from mora.common import get_connector

from tests.graphapi.test_organisation import mock_organisation
from tests.graphapi.test_employees import mock_employee
from tests.util import patch_is_graphql
from tests.util import patch_query_args


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
async def test_shim_equivalence(aioresponses, only_primary_uuid, employee_exists):
    """Ensure that the shim implementation behaves exactly like the old one did."""
    if employee_exists:
        uuid = mock_employee(aioresponses, repeat=True)
    else:
        pattern = re.compile(r"^http://mox/organisation/bruger.*$")
        aioresponses.get(pattern, repeat=True, payload={"results": [[]]})
        uuid = uuid4()

    mock_organisation(aioresponses, repeat=True)
    new_exception = None
    old_exception = None

    with patch_query_args():
        with patch_is_graphql(True):
            try:
                new_result = await get_employee(uuid, only_primary_uuid)
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
