# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from uuid import uuid4

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the KLE data model."""
    query = """
        query {
            kles {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        kle_number_uuid
                        kle_aspect_uuids
                        org_unit_uuid
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
async def test_create_kle_integration_test(
    graphapi_post: GraphAPIPost, org_uuids
) -> None:
    """Test that KLE annotations can be created in LoRa via GraphQL."""

    org_uuid = org_uuids[0]
    parent_from, parent_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    start_date = parent_from

    kle_aspect_uuids = fetch_class_uuids(graphapi_post, "kle_aspect")
    kle_number_uuids = fetch_class_uuids(graphapi_post, "kle_number")

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "asd123",
        "org_unit": str(org_uuid),
        "kle_aspects": [str(u) for u in kle_aspect_uuids],
        "kle_number": str(kle_number_uuids[0]),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutation = """
        mutation CreateKLE($input: KLECreateInput!) {
            kle_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert response.errors is None
    uuid = UUID(response.data["kle_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            kles(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        type
                        org_unit: org_unit_uuid
                        kle_number: kle_number_uuid
                        kle_aspects: kle_aspect_uuids
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["kles"]["objects"])["objects"])

    assert obj["kle_aspects"] == test_data["kle_aspects"]
    assert obj["kle_number"] == test_data["kle_number"]
    assert obj["org_unit"] == test_data["org_unit"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "user_key": "random_user_key",
            "kle_number": "d7c12965-6207-4c82-88b8-68dbf6667492",
            "kle_aspects": ["9016d80a-c6d2-4fb4-83f1-87ecc23ab062"],
            "org_unit": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "user_key": None,
            "kle_number": "d7c12965-6207-4c82-88b8-68dbf6667492",
            "kle_aspects": [
                "f9748c65-3354-4682-a035-042c534c6b4e",
                "fdbdb18f-5a28-4414-bc43-d5c2b70c0510",
            ],
            "org_unit": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "user_key": "New_cool_user_key",
            "kle_number": None,
            "kle_aspects": None,
            "org_unit": None,
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "user_key": None,
            "kle_number": None,
            "kle_aspects": [
                "f9748c65-3354-4682-a035-042c534c6b4e",
                "fdbdb18f-5a28-4414-bc43-d5c2b70c0510",
                "9016d80a-c6d2-4fb4-83f1-87ecc23ab062",
            ],
            "org_unit": None,
            "validity": {"from": "2023-07-10T00:00:00+02:00", "to": None},
        },
    ],
)
async def test_update_kle_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    """Test that KLEs can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query KleQuery($uuid: UUID!) {
            kles(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        user_key
                        kle_aspects: kle_aspect_uuids
                        kle_number: kle_number_uuid
                        org_unit: org_unit_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(uuid)})

    assert response.errors is None

    pre_update_kle = one(one(response.data["kles"]["objects"])["objects"])

    mutation = """
        mutation UpdateKLE($input: KLEUpdateInput!) {
            kle_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    # Writing verify query to retrieve objects containing data on the desired uuids.
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            kles(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        user_key
                        kle_aspects: kle_aspect_uuids
                        kle_number: kle_number_uuid
                        org_unit: org_unit_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    kle_objects_post_update = one(
        one(verify_response.data["kles"]["objects"])["objects"]
    )

    expected_updated_kle = {k: v or pre_update_kle[k] for k, v in test_data.items()}

    assert kle_objects_post_update["user_key"] == expected_updated_kle["user_key"]
    assert kle_objects_post_update["kle_number"] == expected_updated_kle["kle_number"]
    assert set(kle_objects_post_update["kle_aspects"]) == set(
        expected_updated_kle["kle_aspects"]
    )
    assert kle_objects_post_update["org_unit"] == expected_updated_kle["org_unit"]
    assert kle_objects_post_update["validity"] == expected_updated_kle["validity"]


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "to": "2023-07-25T00:00:00+02:00",
        },
        {
            "uuid": "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5",
            "to": "2040-01-01T00:00:00+01:00",
        },
    ],
)
async def test_kle_terminate_integration(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateKLE($input: KLETerminateInput!) {
            kle_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            kles(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        validity {
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None
    kle_objects_post_terminate = one(
        one(verify_response.data["kles"]["objects"])["objects"]
    )
    assert test_data["uuid"] == kle_objects_post_terminate["uuid"]
    assert test_data["to"] == kle_objects_post_terminate["validity"]["to"]
