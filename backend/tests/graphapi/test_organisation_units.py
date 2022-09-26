# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
import string

from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import infer
from hypothesis import strategies as st
from pytest import MonkeyPatch

from mora.graphapi.versions.latest.types import OrganisationUnitType
from mora.graphapi.versions.latest.types import OrganizationUnit
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import mapping
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from ramodels.mo import OrganisationUnitRead
from tests.conftest import GQLResponse

from mora.graphapi.versions.latest.models import OrganisationUnitUpdate
from fastapi.encoders import jsonable_encoder
from mora.graphapi.shim import execute_graphql
from operator import itemgetter
from uuid import UUID
from more_itertools import one
from ramodels.mo import Validity as RAValidity


@given(test_data=graph_data_strat(OrganisationUnitRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all our organisation units."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                org_units {
                    uuid
                    objects {
                        uuid
                        user_key
                        name
                        type
                        validity {from to}
                        parent_uuid
                        unit_type_uuid
                        org_unit_hierarchy
                        org_unit_level_uuid
                        time_planning_uuid
                    }

                }
            }
        """
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["org_units"]) == test_data


@given(test_input=graph_data_uuids_strat(OrganisationUnitRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query organisation units by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    org_units(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [ou.get("uuid") for ou in response.data["org_units"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(data=st.data())
@patch("mora.graphapi.versions.latest.mutators.update_org_unit", new_callable=AsyncMock)
async def test_mutator_for_updating_org_unit(update_org_unit: AsyncMock, data) -> None:
    """Tests that the mutator function for updating an organisation unit passes through,
    with the defined pydantic model."""

    mutation = """
    mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
    org_unit_update(input: $input) {
    uuid
    }
    }
    """
    validity = data.draw(
        st.tuples(
            st.datetimes(min_value=datetime.datetime(1930, 1, 1)),
            st.datetimes() | st.none(),
        ).filter(lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True)
    )

    test_data_validity_from, test_data_validity_to = validity

    test_data = data.draw(
        st.builds(
            OrganisationUnitUpdate,
            from_date=st.just(test_data_validity_from),
            to_date=st.just(test_data_validity_to),
            name=st.text(alphabet=string.printable),
            org_unit_type_uuid=infer,
            org_unit_level_uuid=infer,
            org_unit_hierarchy_uuid=infer,
            parent_uuid=infer,
            time_planning=infer,
            location=infer,
        )
    )
    update_org_unit.return_value = OrganisationUnitType(uuid=test_data.uuid)

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(query=mutation, variable_values={"input": payload})

    update_org_unit.assert_called_with(test_data)

    assert response.errors is None
    assert response.data == {"org_unit_update": {"uuid": str(test_data.uuid)}}


@given(data=st.data())
@pytest.mark.usefixtures("sample_structures")
async def test_updating_org_unit_integration_test(
    data, graphapi_post
) -> None:
    """Test that pydantic jsons are passed through to update_org_unit."""
    valid_org_uuids = [
        UUID("08eaf849-e9f9-53e0-b6b9-3cd45763ecbb"),  # Viuf skole
        UUID("08eaf849-e9f9-53e0-b6b9-3cd45763ecbb"),  # Lunderskov skole
        UUID("0a946185-4712-5c4b-9bbf-b0894603b9a3"),  # Borgmesterens Afdeling
        UUID("0c655440-867d-561e-8c28-2aa0ac8d1e20"),  # Teknisk Support
    ]
    org_unit_uuid = data.draw(st.sampled_from(valid_org_uuids))
    org_unit_uuid_as_str = str(org_unit_uuid)

    validity = data.draw(
        st.tuples(
            st.datetimes(min_value=datetime.datetime(1930, 1, 1)),
            st.datetimes() | st.none(),
        ).filter(lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True)
    )

    test_data_validity_from, test_data_validity_to = validity

    test_data = data.draw(
        st.builds(
            OrganisationUnitUpdate,
            from_date=st.just(test_data_validity_from),
            to_date=st.just(test_data_validity_to),
            name=st.text(alphabet=string.printable),
            org_unit_type_uuid=infer,
            org_unit_level_uuid=infer,
            org_unit_hierarchy_uuid=infer,
            parent_uuid=infer,
            time_planning=infer,
            location=infer,
        )
    )

    mutation = """
    mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
    org_unit_update(input: $input) {
    uuid
    }
    }
    """
    payload = jsonable_encoder(test_data)
    response = await LatestGraphQLSchema.get().execute(
        mutation, variable_values={"input": payload}
    )
    print(test_data)
    assert response.errors is None
    assert response.data == {"org_unit_update": {"uuid": org_unit_uuid_as_str}}
