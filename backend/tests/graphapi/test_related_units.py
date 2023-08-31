# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from pytest import MonkeyPatch

from ..conftest import GraphAPIPost
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import RelatedUnitsUpdate
from ramodels.mo.details import RelatedUnitRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(RelatedUnitRead))
def test_query_all(test_data, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query all attributes of the related_unit data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                related_units {
                    objects {
                        uuid
                        objects {
                            uuid
                            user_key
                            org_unit_uuids
                            type
                            validity {from to}
                        }
                    }
                }
            }
        """
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["related_units"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(RelatedUnitRead))
def test_query_by_uuid(test_input, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query related_units by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
            query TestQuery($uuids: [UUID!]) {
                related_units(filter: {uuids: $uuids}) {
                    objects {
                        uuid
                    }
                }
            }
            """
        response = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [
        related.get("uuid") for related in response.data["related_units"]["objects"]
    ]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.update_related_units",
    new_callable=AsyncMock,
)
async def test_update_related_units_mutation_unit_test(
    update_related_units: AsyncMock, test_data: RelatedUnitsUpdate
) -> None:
    """Tests that the mutator function for creating a RelatedUnits annotation passes through,
    with the defined pydantic model."""

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """

    update_related_units.return_value = test_data.origin

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"related_units_update": {"uuid": str(test_data.origin)}}

    update_related_units.assert_called_with(test_data)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "destination": [
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "68c5d78e-ae26-441f-a143-0103eca8b62a",
                "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            ],
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "destination": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "destination": [
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "68c5d78e-ae26-441f-a143-0103eca8b62a",
                "dad7d0ad-c7a9-4a94-969d-464337e31fec",
                "b688513d-11f7-4efc-b679-ab082a2055d0",
                "fa2e23c9-860a-4c90-bcc6-2c0721869a25",
            ],
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "origin": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "destination": [
                "68c5d78e-ae26-441f-a143-0103eca8b62a",
            ],
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_related_units_integration_test(test_data, graphapi_post) -> None:
    """Test that relations between units can be updated in LoRa via GraphQL."""
    uuid = test_data["origin"]

    query = """
        query RelatedUnits($uuid: UUID!) {
            related_units(filter: {org_units: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        user_key
                        org_unit_uuids
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(query, {"uuid": str(uuid)})
    assert response.errors is None

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None

    verify_query = """
        query VerifyQuery($org_units: UUID!) {
            related_units(filter: {org_units: [$org_units]}) {
                objects {
                    objects {
                        org_unit_uuids
                    }
            }
        }
    }
    """
    response: GQLResponse = graphapi_post(
        verify_query, {"org_units": str(test_data["origin"])}
    )
    assert response.errors is None

    objects = response.data["related_units"]["objects"]

    if test_data["destination"] is None:
        assert objects == []
    else:
        relations = [
            {"objects": [{"org_unit_uuids": [str(dest), str(test_data["origin"])]}]}
            for dest in test_data["destination"]
        ]
        assert len(relations) == len(objects)
