# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID

import pytest
from more_itertools import one
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from tests.conftest import GraphAPIPost

from .utils import gen_read_parent
from .utils import gen_set_parent
from .utils import sjsonable_encoder

fixture_parent_uuid = UUID("2874e1dc-85e6-4269-823a-e1125484dfd3")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "initial,new,expected",
    [
        # Starting with UUID set
        # Using same UUID does nothing
        (fixture_parent_uuid, fixture_parent_uuid, fixture_parent_uuid),
        # Using unset does nothing
        (fixture_parent_uuid, UNSET, fixture_parent_uuid),
        # Using None does nothing
        (fixture_parent_uuid, None, fixture_parent_uuid),
        # Starting with None
        # Using UUID sets UUID
        (None, fixture_parent_uuid, fixture_parent_uuid),
        # Using unset does nothing
        (None, UNSET, None),
        # Using None does nothing
        (None, None, None),
    ],
)
async def test_parent_changes(
    graphapi_post: GraphAPIPost,
    initial: UUID | None,
    new: UUID | UnsetType | None,
    expected: UUID | None,
) -> None:
    """Test that we can change, noop and clear parent."""
    url = "/graphql/v21"

    uuid = UUID("dad7d0ad-c7a9-4a94-969d-464337e31fec")

    read_parent = partial(gen_read_parent, graphapi_post, url, uuid)
    set_parent = partial(gen_set_parent, graphapi_post, url, uuid)

    # Setup and assert initial state
    # NOTE: Uses v22 as only v21 cannot actually clear the field
    gen_set_parent(graphapi_post, "/graphql/v22", uuid, initial)
    parent_uuid = read_parent()
    assert parent_uuid == initial

    # Fire our change and assert result
    set_parent(new)
    parent_uuid = read_parent()
    assert parent_uuid == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
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
    graphapi_post: GraphAPIPost, test_data
) -> None:
    """Test that organisation units can be updated in LoRa via GraphQL."""
    url = "/graphql/v21"

    uuid = test_data["uuid"]

    query = """
        query OrgUnitQuery($uuid: UUID!) {
            org_units(filter: {uuids: [$uuid]}) {
                objects {
                    current {
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
        }
    """

    response = graphapi_post(query, {"uuid": str(uuid)}, url=url)
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["org_units"]["objects"])
    assert obj["current"] is not None
    pre_update_org_unit = obj["current"]

    mutate_query = """
        mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
            org_unit_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(
        mutate_query, {"input": sjsonable_encoder(test_data)}, url=url
    )
    assert mutation_response.errors is None

    response = graphapi_post(query, {"uuid": str(uuid)}, url=url)
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["org_units"]["objects"])
    assert obj["current"] is not None
    post_update_org_unit = obj["current"]

    expected_updated_org_unit = {
        k: test_data.get(k) or v for k, v in pre_update_org_unit.items()
    }

    assert post_update_org_unit == expected_updated_org_unit
