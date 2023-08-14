# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from _datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import RoleCreate
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import RoleRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(RoleRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the role data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                roles {
                    objects {
                        uuid
                        objects {
                            uuid
                            user_key
                            employee_uuid
                            org_unit_uuid
                            role_type_uuid
                            type
                            validity {from to}
                        }
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["roles"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(RoleRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query roles by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    roles(uuids: $uuids) {
                        objects {
                            uuid
                        }
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [role.get("uuid") for role in response.data["roles"]["objects"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_role", new_callable=AsyncMock)
async def test_create_role_mutation_unit_test(
    create_role: AsyncMock, test_data: RoleCreate
) -> None:
    """Tests that the mutator function for creating a role passes through, with the
    defined pydantic model."""

    mutation = """
        mutation CreateRole($input: RoleCreateInput!) {
            role_create(input: $input) {
                uuid
            }
        }
    """

    create_role.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"role_create": {"uuid": str(test_data.uuid)}}

    create_role.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_role_integration_test(
    data, graphapi_post, employee_uuids, org_uuids
) -> None:
    """Test that roles can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    org_uuid = data.draw(st.sampled_from(org_uuids))
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=org_from, max_value=org_to or datetime.max)
    )
    if org_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=org_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    role_type = fetch_class_uuids(graphapi_post, "role_type")

    test_data = data.draw(
        st.builds(
            RoleCreate,
            uuid=st.uuids() | st.none(),
            person=st.sampled_from(employee_uuids),
            role_type=st.sampled_from(role_type),
            org_unit=st.just(org_uuid),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateRole($input: RoleCreateInput!) {
            role_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["role_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            roles(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    objects {
                        user_key
                        employee: employee_uuid
                        org_unit: org_unit_uuid
                        role_type: role_type_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["roles"]["objects"])["objects"])

    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["role_type"]) == test_data.role_type
    assert obj["user_key"] == test_data.user_key or str(uuid)

    assert (
        datetime.fromisoformat(obj["validity"]["from"]).date()
        == test_data.validity.from_date.date()
    )
    if obj["validity"]["to"] is not None:
        assert (
            datetime.fromisoformat(obj["validity"]["to"]).date()
            == test_data.validity.to_date.date()
        )
    else:
        assert test_data.validity.to_date is None
