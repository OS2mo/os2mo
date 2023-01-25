# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
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
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import OrganisationUnitCreate
from mora.graphapi.versions.latest.models import OrganisationUnitUpdate
from mora.graphapi.versions.latest.types import UUIDReturn
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
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
    """
    created_uuid = uuid4()
    create_org_unit.return_value = UUIDReturn(uuid=created_uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"org_unit_create": {"uuid": str(created_uuid)}}

    create_org_unit.assert_called_with(test_data)


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
            uuid=st.uuids(),
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
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
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
                    uuid
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
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        ("", 9),
        # Filter roots
        ("(parents: null)", 2),
        # Filter under node
        ('(parents: "2874e1dc-85e6-4269-823a-e1125484dfd3")', 4),
        ('(parents: "b1f69701-86d8-496e-a3f1-ccef18ac1958")', 1),
        (
            """
            (parents: [
                "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "b1f69701-86d8-496e-a3f1-ccef18ac1958"
            ])
        """,
            5,
        ),
    ],
)
async def test_org_unit_parent_filter(graphapi_post, filter_snippet, expected) -> None:
    """Test parent filter on organisation units."""
    org_unit_query = f"""
        query OrgUnit {{
            org_units{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(org_unit_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        # Filter none
        ("", 9),
        ("(hierarchies: null)", 9),
        # Filter 'linjeorg'
        ('(hierarchies: "f805eb80-fdfe-8f24-9367-68ea955b9b9b")', 2),
        # Filter 'hidden'
        ('(hierarchies: "8c30ab5a-8c3a-566c-bf12-790bdd7a9fef")', 1),
        # Filter 'selvejet'
        ('(hierarchies: "69de6410-bfe7-bea5-e6cc-376b3302189c")', 1),
        # Filter 'linjeorg' + 'hidden'
        (
            """
            (hierarchies: [
                "f805eb80-fdfe-8f24-9367-68ea955b9b9b"
                "8c30ab5a-8c3a-566c-bf12-790bdd7a9fef",
            ])
            """,
            3,
        ),
    ],
)
async def test_org_unit_hierarchy_filter(
    graphapi_post, filter_snippet, expected
) -> None:
    """Test hierarchies filter on organisation units."""
    org_unit_query = f"""
        query OrgUnit {{
            org_units{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(org_unit_query)
    assert response.errors is None
    assert len(response.data["org_units"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": None,
            "name": None,
            "parent": None,
            "org_unit_type": None,
            "time_planning": None,
            "org_unit_level": None,
            "org_unit_hierarchy": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "-",
            "name": None,
            "parent": None,
            "org_unit_type": None,
            "time_planning": None,
            "org_unit_level": None,
            "org_unit_hierarchy": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "Testing user key for tests",
            "name": "Testing name for tests",
            "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
            "time_planning": "27935dbb-c173-4116-a4b5-75022315749d",
            "org_unit_level": "0f015b67-f250-43bb-9160-043ec19fad48",
            "org_unit_hierarchy": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "skole-børn",
            "name": "Skole og Børn",
            "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "org_unit_type": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            "time_planning": None,
            "org_unit_level": None,
            "org_unit_hierarchy": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_org_unit_mutation_integration_test(
    graphapi_post, test_data
) -> None:
    """Test that organisation units can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
                objects {
                    user_key
                    name
                    parent: parent_uuid
                    org_unit_type: unit_type_uuid
                    time_planning: time_planning_uuid
                    org_unit_level: org_unit_level_uuid
                    org_unit_hierarchy: org_unit_hierarchy
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    response: GQLResponse = graphapi_post(query, {"uuid": str(uuid)})
    assert response.errors is None

    pre_update_org_unit = one(one(response.data["org_units"])["objects"])

    mutate_query = """
        mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
            org_unit_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: [UUID!]!) {
            org_units(uuids: $uuid){
                objects {
                    uuid
                    user_key
                    name
                    parent: parent_uuid
                    org_unit_type: unit_type_uuid
                    time_planning: time_planning_uuid
                    org_unit_level: org_unit_level_uuid
                    org_unit_hierarchy: org_unit_hierarchy
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    verify_response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    post_update_org_unit = one(one(verify_response.data["org_units"])["objects"])

    expected_updated_org_unit = {
        k: v or pre_update_org_unit[k] for k, v in test_data.items()
    }

    assert post_update_org_unit == expected_updated_org_unit


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.update_org_unit", new_callable=AsyncMock)
async def test_update_org_unit_mutation_unit_test(
    update_org_unit: AsyncMock, test_data: OrganisationUnitUpdate
) -> None:
    """Tests that the mutator function for updating an organisation unit passes through,
    with the defined pydantic model."""

    mutation = """
        mutation UpdateOrganisationUnit($input: OrganisationUnitUpdateInput!) {
            org_unit_update(input: $input) {
                uuid
            }
        }
    """

    update_org_unit.return_value = UUIDReturn(uuid=test_data.uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"org_unit_update": {"uuid": str(test_data.uuid)}}

    update_org_unit.assert_called_with(test_data)
