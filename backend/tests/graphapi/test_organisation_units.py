# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from operator import itemgetter
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import OrganisationUnitCreate
from mora.graphapi.versions.latest.types import OrganizationUnit
from ramodels.mo import OrganisationUnitRead
from ramodels.mo import Validity as RAValidity
from tests.conftest import GQLResponse


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


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_org_unit", new_callable=AsyncMock)
async def test_create_org_unit(
    create_org_unit: AsyncMock, test_data: OrganisationUnitCreate
) -> None:
    """Test that pydantic jsons are passed through to create_org_unit."""

    mutate_query = """
        mutation CreateOrgUnit($input: OrganizationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
    """

    created_uuid = uuid4()
    create_org_unit.return_value = OrganizationUnit(uuid=created_uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"org_unit_create": {"uuid": str(created_uuid)}}

    create_org_unit.assert_called_with(test_data)


@pytest.fixture(scope="class", name="org_uuids")
def fetch_org_uuids(sample_structures_no_reset, graphapi_post: Callable) -> list[UUID]:
    parent_uuids_query = """
        query FetchOrgUUIDs {
            org_units {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_uuids_query)
    assert response.errors is None
    org_uuids = list(map(UUID, map(itemgetter("uuid"), response.data["org_units"])))
    return org_uuids


def fetch_org_unit_validity(
    graphapi_post: Callable, org_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
                objects {
                    uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(validity_query, {"uuid": str(org_uuid)})
    assert response.errors is None
    validity = one(one(response.data["org_units"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_class_uuids(graphapi_post: Callable, facet_name: str) -> list[UUID]:
    class_query = """
        query FetchClassUUIDs($user_key: String!) {
            facets(user_keys: [$user_key]) {
                classes {
                    uuid
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(class_query, {"user_key": facet_name})
    assert response.errors is None
    facet = one(response.data["facets"])
    class_uuids = list(map(UUID, map(itemgetter("uuid"), facet["classes"])))
    return class_uuids


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_create_org_unit_integration_test(data, graphapi_post, org_uuids) -> None:
    """Test that organisation units can be created in LoRa via GraphQL."""
    # org_uuids = fetch_org_uuids(graphapi_post)

    parent_uuid = data.draw(st.sampled_from(org_uuids))
    parent_from, parent_to = fetch_org_unit_validity(graphapi_post, parent_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=parent_from, max_value=parent_to or datetime.max)
    )
    if parent_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=parent_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    org_unit_type_uuids = fetch_class_uuids(graphapi_post, "org_unit_type")
    time_planning_uuids = fetch_class_uuids(graphapi_post, "time_planning")
    org_unit_level_uuids = fetch_class_uuids(graphapi_post, "org_unit_level")

    test_data = data.draw(
        st.builds(
            OrganisationUnitCreate,
            # TODO: Allow all text
            name=st.text(
                alphabet=st.characters(whitelist_categories=("L",)), min_size=1
            ),
            parent=st.just(parent_uuid),
            org_unit_type=st.sampled_from(org_unit_type_uuids),
            time_planning=st.sampled_from(time_planning_uuids),
            org_unit_level=st.sampled_from(org_unit_level_uuids),
            # TODO: Handle org_unit_hierarchy as we do with the above
            # NOTE: org_unit_hierarchy does not exist in the sample data
            org_unit_hierarchy=st.none(),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )
    payload = jsonable_encoder(test_data)

    mutate_query = """
        mutation CreateOrgUnit($input: OrganizationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(mutate_query, {"input": payload})
    assert response.errors is None
    uuid = UUID(response.data["org_unit_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            org_units(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    user_key
                    name
                    parent_uuid
                    unit_type_uuid
                    time_planning_uuid
                    org_unit_level_uuid
                    org_unit_hierarchy_uuid: org_unit_hierarchy
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["org_units"])["objects"])
    assert obj["name"] == test_data.name
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert UUID(obj["parent_uuid"]) == test_data.parent
    assert UUID(obj["unit_type_uuid"]) == test_data.org_unit_type
    assert UUID(obj["time_planning_uuid"]) == test_data.time_planning
    assert UUID(obj["org_unit_level_uuid"]) == test_data.org_unit_level
    # assert UUID(obj["org_unit_hierarchy_uuid"]) == test_data.org_unit_hierarchy
    assert obj["org_unit_hierarchy_uuid"] is None
    assert test_data.org_unit_hierarchy is None

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


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_no_reset")
async def test_org_unit_parent_filter(graphapi_post) -> None:
    """Test parent filter on organisation units."""

    org_unit_query = """
        query OrgUnit {
            org_units {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(org_unit_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == 9

    parent_query = """
        query ParentOrgUnit {
            org_units(parents: null) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == 2

    parent_query = """
        query ParentOrgUnit {
            org_units(parents: "2874e1dc-85e6-4269-823a-e1125484dfd3") {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == 4

    parent_query = """
        query ParentOrgUnit {
            org_units(parents: [
                "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "b1f69701-86d8-496e-a3f1-ccef18ac1958"
            ]) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == 5
