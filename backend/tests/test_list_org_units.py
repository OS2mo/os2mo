# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import uuid4

import hypothesis.strategies as st
from hypothesis import given
from mora.service.orgunit import list_orgunits


@patch("mora.service.orgunit.get_details_from_query_args")
@given(st.lists(st.uuids()))
async def test_org_unit_hierarchy(details_mock, hierarchies):
    common_mock = AsyncMock()
    orgid = uuid4()
    expected = [str(u) for u in hierarchies]

    with patch("mora.common.get_connector", return_value=common_mock):
        assert await list_orgunits(orgid=orgid, hierarchy_uuids=hierarchies)

    if hierarchies:
        assert "opmærkning" in common_mock.organisationenhed.paged_get.call_args[1]
        assert (
            common_mock.organisationenhed.paged_get.call_args[1]["opmærkning"]
            == expected
        )
    else:
        assert "opmærkning" not in common_mock.organisationenhed.paged_get.call_args[1]
