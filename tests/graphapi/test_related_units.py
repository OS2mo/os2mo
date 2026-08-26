# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest
from fastapi.encoders import jsonable_encoder

from tests.conftest import GQLResponse

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the related_unit data model."""
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_related_units_org_unit_not_found(graphapi_post) -> None:
    """Updating related units with a non-existent unit yields E_ORG_UNIT_NOT_FOUND."""
    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation,
        {
            "input": {
                "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "destination": ["00000000-0000-0000-0000-000000000000"],
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            }
        },
    )
    assert response.errors is not None
    assert any(
        e.get("extensions", {}).get("error_context", {}).get("error_key")
        == "E_ORG_UNIT_NOT_FOUND"
        for e in response.errors
    ), f"unexpected errors: {response.errors}"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_related_units_date_outside_org_unit_range(graphapi_post) -> None:
    """Updating related units from a date where a unit is inactive yields
    V_DATE_OUTSIDE_ORG_UNIT_RANGE."""
    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """
    # HIST_UNIT ("da77153e-30f3-4dc2-a611-ee912a28d8aa") is only valid
    # from 2016-01-01 to 2018-12-31, so a 2019 effective date puts it
    # outside its validity range.
    response: GQLResponse = graphapi_post(
        mutation,
        {
            "input": {
                "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "destination": ["da77153e-30f3-4dc2-a611-ee912a28d8aa"],
                "validity": {"from": "2019-06-01T00:00:00+01:00", "to": None},
            }
        },
    )
    assert response.errors is not None
    assert any(
        e.get("extensions", {}).get("error_context", {}).get("error_key")
        == "V_DATE_OUTSIDE_ORG_UNIT_RANGE"
        for e in response.errors
    ), f"unexpected errors: {response.errors}"
