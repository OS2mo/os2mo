# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Related units as of GraphQL version 30.

Version 31 replaced the symmetric related units of `related_units_update` with
directed `related_unit_create`, `related_unit_update` and
`related_unit_terminate`.
"""

from collections.abc import Callable
from functools import partial
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.fixture
def graphapi_post_v30(graphapi_post: GraphAPIPost) -> GraphAPIPost:
    return partial(graphapi_post, url="/graphql/v30")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post_v30: GraphAPIPost):
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
    response = graphapi_post_v30(query)
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
async def test_update_related_units_integration_test(
    test_data, graphapi_post_v30
) -> None:
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
    response: GQLResponse = graphapi_post_v30(query, {"uuid": str(uuid)})
    assert response.errors is None

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post_v30(
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
    response: GQLResponse = graphapi_post_v30(
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
@pytest.mark.usefixtures("empty_db")
def test_update_related_units_unknown_destination(
    graphapi_post_v30: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """Updating related units with a non-existent destination is rejected."""

    origin = create_org_unit("origin")

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """

    response = graphapi_post_v30(
        mutation,
        {
            "input": {
                "origin": str(origin),
                "destination": [str(uuid4())],
                "validity": {"from": "2017-06-01"},
            }
        },
    )
    assert response.errors is not None
    assert (
        one(response.errors)["extensions"]["error_context"]["error_key"]
        == "E_ORG_UNIT_NOT_FOUND"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_update_related_units_outside_validity(
    graphapi_post_v30: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """A destination that is not active at the given date is rejected."""

    origin = create_org_unit("origin")
    destination = create_org_unit("destination")

    terminate = """
        mutation TerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
            org_unit_terminate(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post_v30(
        terminate,
        {
            "input": {
                "uuid": str(destination),
                "to": "2017-01-01",
            }
        },
    )
    assert response.errors is None

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """

    response = graphapi_post_v30(
        mutation,
        {
            "input": {
                "origin": str(origin),
                "destination": [str(destination)],
                "validity": {"from": "2018-01-01"},
            }
        },
    )
    assert response.errors is not None
    assert (
        one(response.errors)["extensions"]["error_context"]["error_key"]
        == "V_DATE_OUTSIDE_ORG_UNIT_RANGE"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_units_update_relates_origin_as_org_unit(
    graphapi_post: GraphAPIPost,
    graphapi_post_v30: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """Version 31 reads the `origin` of `related_units_update` as `org_unit`."""
    # The origin sorts last, so LoRa returns it last
    origin = create_org_unit(
        "origin", uuid=UUID("00000000-0000-0000-0000-00000000000b")
    )
    destination = create_org_unit(
        "destination", uuid=UUID("00000000-0000-0000-0000-00000000000a")
    )

    mutation = """
        mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
            related_units_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post_v30(
        mutation,
        {
            "input": {
                "origin": str(origin),
                "destination": [str(destination)],
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None

    query = """
        query ReadRelatedUnits($uuid: UUID!) {
            related_units(filter: {org_units: [$uuid]}) {
                objects {
                    current {
                        org_unit_response { uuid }
                        related_org_unit_response { uuid }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(origin)})
    assert response.errors is None
    assert one(response.data["related_units"]["objects"])["current"] == {
        "org_unit_response": {"uuid": str(origin)},
        "related_org_unit_response": {"uuid": str(destination)},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_create_is_read_by_version_30(
    graphapi_post: GraphAPIPost,
    graphapi_post_v30: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """Related units created in version 31 read as before in version 30."""
    org_unit = create_org_unit("org_unit")
    related_org_unit = create_org_unit("related_org_unit")
    response = graphapi_post(
        """
        mutation CreateRelatedUnit($input: RelatedUnitCreateInput!) {
            related_unit_create(input: $input) { uuid }
        }
        """,
        {
            "input": {
                "org_unit": str(org_unit),
                "related_org_unit": str(related_org_unit),
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None

    query = """
        query ReadRelatedUnits($uuid: UUID!) {
            related_units(filter: {org_units: [$uuid]}) {
                objects {
                    current {
                        org_unit_uuids
                        org_units_response { objects { uuid } }
                    }
                }
            }
        }
    """
    response = graphapi_post_v30(query, {"uuid": str(org_unit)})
    assert response.errors is None
    current = one(response.data["related_units"]["objects"])["current"]
    expected = {str(org_unit), str(related_org_unit)}
    assert set(current["org_unit_uuids"]) == expected
    assert {o["uuid"] for o in current["org_units_response"]["objects"]} == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_units_update_keeps_relations_from_version_31(
    graphapi_post: GraphAPIPost,
    graphapi_post_v30: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """`related_units_update` sees relations created in version 31.

    As a unit can only be related to another unit once, relating them again is a
    no-op, and leaving them out terminates the relation.
    """
    origin = create_org_unit("origin")
    destination = create_org_unit("destination")
    response = graphapi_post(
        """
        mutation CreateRelatedUnit($input: RelatedUnitCreateInput!) {
            related_unit_create(input: $input) { uuid }
        }
        """,
        {
            "input": {
                "org_unit": str(destination),
                "related_org_unit": str(origin),
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None
    uuid = response.data["related_unit_create"]["uuid"]

    def relate(destinations: list[UUID]) -> None:
        response = graphapi_post_v30(
            """
            mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
                related_units_update(input: $input) { uuid }
            }
            """,
            {
                "input": {
                    "origin": str(origin),
                    "destination": [str(d) for d in destinations],
                    "validity": {"from": "2022-01-01"},
                }
            },
        )
        assert response.errors is None

    def read() -> list[dict[str, Any]]:
        response = graphapi_post(
            """
            query ReadRelatedUnits($uuid: UUID!) {
                related_units(filter: {org_units: [$uuid]}) {
                    objects { uuid current { validity { from to } } }
                }
            }
            """,
            {"uuid": str(origin)},
        )
        assert response.errors is None
        return response.data["related_units"]["objects"]

    relate([destination])
    assert read() == [
        {
            "uuid": uuid,
            "current": {"validity": {"from": "2020-01-01T00:00:00+01:00", "to": None}},
        }
    ]

    # The relation is terminated, so it is no longer current
    relate([])
    assert read() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "mutator", ["related_unit_create", "related_unit_update", "related_unit_terminate"]
)
def test_directed_related_unit_mutators_do_not_exist(
    graphapi_post_v30: GraphAPIPost, mutator: str
) -> None:
    """The directed related unit mutators are introduced in version 31."""
    response = graphapi_post_v30(f"mutation {{ {mutator} {{ uuid }} }}")
    assert response.errors is not None
    assert f"Cannot query field '{mutator}'" in one(response.errors)["message"]
