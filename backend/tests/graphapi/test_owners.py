# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost) -> None:
    """Test that we can query all attributes of the owner data model."""
    query = """
        query {
            owners {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        org_unit_uuid
                        owner_uuid
                        owner_inference_priority
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
    "filter,expected",
    [
        ({}, 2),
        # Owner filters
        ({"owner": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}}, 1),
        ({"owner": {"uuids": "236e0a78-11a0-4ed9-8545-6286bb8611c7"}}, 0),
        (
            {
                "owner": {
                    "uuids": [
                        "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "6ee24785-ee9a-4502-81c2-7697009c9053",
                    ]
                }
            },
            2,
        ),
        # Employee filters
        ({"employee": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}}, 1),
        ({"employee": {"uuids": "6ee24785-ee9a-4502-81c2-7697009c9053"}}, 0),
        (
            {
                "employee": {
                    "uuids": [
                        "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "6ee24785-ee9a-4502-81c2-7697009c9053",
                    ]
                }
            },
            1,
        ),
        # Organisation Unit filter
        ({"org_unit": {"uuids": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}}, 1),
        ({"org_unit": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"}}, 0),
        (
            {
                "org_unit": {
                    "uuids": [
                        "2874e1dc-85e6-4269-823a-e1125484dfd3",
                        "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    ]
                }
            },
            1,
        ),
        # Mixed filters
        (
            {
                "owner": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"},
                "org_unit": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
            },
            0,
        ),
        (
            {
                "owner": {"uuids": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "employee": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"},
            },
            1,
        ),
        (
            {
                "owner": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"},
                "org_unit": {"uuids": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
            },
            1,
        ),
    ],
)
async def test_owner_employees_filters(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test filters on owners."""
    owner_query = """
        query ReadOwners($filter: OwnerFilter!) {
            owners(filter: $filter) {
                objects {
                    uuid
                    objects {
                        owner {
                            uuid
                        }
                        employee_uuid
                        org_unit_uuid
                    }
                }
            }
        }
    """
    response = graphapi_post(owner_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["owners"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter, inherit, expected",
    [
        # We only have 1 owner that can be inherited
        ({"uuids": "85715fc7-925d-401b-822d-467eb4b163b6"}, True, 1),
        ({"uuids": "85715fc7-925d-401b-822d-467eb4b163b6"}, False, 0),
    ],
)
def test_query_inherited_owners(
    graphapi_post: GraphAPIPost, filter, inherit, expected
) -> None:
    """Test that we can get inherited owners."""
    query = """
        query ReadInheritedOwners($filter: OrganisationUnitFilter!, $inherit: Boolean!) {
            org_units(filter: $filter) {
                objects {
                    validities {
                        owners(inherit: $inherit) {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, variables=dict(filter=filter, inherit=inherit))
    assert response.errors is None
    assert (
        len(response.data["org_units"]["objects"][0]["validities"][0]["owners"])
        == expected
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data, expected_fail",
    [
        (
            {
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": None,
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                "person": None,
                "org_unit": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            1,
        ),
        (
            {
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": None,
                "owner": None,
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": None,
                "owner": None,
                "inference_priority": "ENGAGEMENT",
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": None,
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": "ENGAGEMENT",
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            1,
        ),
    ],
)
async def test_create_owner_integration_test(
    graphapi_post: GraphAPIPost, test_data, expected_fail
) -> None:
    mutation = """
        mutation CreateOwner($input: OwnerCreateInput!) {
            owner_create(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    if expected_fail:
        assert mutation_response.errors is not None
        return

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            owners(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        person: employee_uuid
                        org_unit: org_unit_uuid
                        owner: owner_uuid
                        inference_priority: owner_inference_priority
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(
        verify_query, {"uuid": str(mutation_response.data["owner_create"]["uuid"])}
    )
    assert verify_response.errors is None

    created_owner = one(one(verify_response.data["owners"]["objects"])["objects"])

    assert test_data == created_owner


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data, expected_fail",
    # person or org_unit has to be set, otherwise we get:
    # `Must supply at most one of org_unit UUID, person UUID`
    [
        (
            {
                # owned org_unit
                "uuid": "c16ff527-3501-42f7-a942-e606c6c1a0a7",
                "person": None,
                "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "owner": None,
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                # owned org_unit
                "uuid": "c16ff527-3501-42f7-a942-e606c6c1a0a7",
                "person": None,
                "org_unit": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                # owned org_unit
                "uuid": "c16ff527-3501-42f7-a942-e606c6c1a0a7",
                "person": "7626ad64-327d-481f-8b32-36c78eb12f8c",
                "org_unit": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            1,
        ),
        (
            {
                # owned org_unit
                "uuid": "c16ff527-3501-42f7-a942-e606c6c1a0a7",
                "person": None,
                "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": "ASSOCIATION",
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            1,
        ),
        (
            {
                # owned person
                "uuid": "c21574ad-ab5e-456d-bc39-83886c0eff50",
                "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_unit": None,
                "owner": None,
                "inference_priority": None,
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                # owned person
                "uuid": "c21574ad-ab5e-456d-bc39-83886c0eff50",
                "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_unit": None,
                "owner": None,
                "inference_priority": "ENGAGEMENT",
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            0,
        ),
        (
            {
                # owned person
                "uuid": "c21574ad-ab5e-456d-bc39-83886c0eff50",
                "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_unit": None,
                "owner": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "inference_priority": "ENGAGEMENT",
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            1,
        ),
    ],
)
async def test_update_owner_integration_test(
    graphapi_post: GraphAPIPost, test_data, expected_fail
) -> None:
    uuid = test_data["uuid"]

    query = """
        query OwnerQuery($uuid: UUID!) {
            owners(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        person: employee_uuid
                        org_unit: org_unit_uuid
                        owner: owner_uuid
                        inference_priority: owner_inference_priority
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

    pre_update_owner = one(one(response.data["owners"]["objects"])["objects"])

    mutation = """
        mutation UpdateOwner($input: OwnerUpdateInput!) {
            owner_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    if expected_fail:
        assert mutation_response.errors is not None
        return

    assert mutation_response.errors is None

    verify_response = graphapi_post(query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    owner_objects_post_update = one(
        one(verify_response.data["owners"]["objects"])["objects"]
    )

    expected_updated_owner = {
        k: v if v is not None or k == "owner" else pre_update_owner[k]
        for k, v in test_data.items()
    }

    assert expected_updated_owner == owner_objects_post_update


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "c21574ad-ab5e-456d-bc39-83886c0eff50",
            "to": "2023-07-25T00:00:00+02:00",
        },
        {
            "uuid": "c21574ad-ab5e-456d-bc39-83886c0eff50",
            "to": "2040-01-01T00:00:00+01:00",
        },
    ],
)
async def test_owner_terminate_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateOwner($input: OwnerTerminateInput!) {
            owner_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            owners(filter: {uuids: [$uuid]}){
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
    owner_objects_post_terminate = one(
        one(verify_response.data["owners"]["objects"])["objects"]
    )
    assert test_data["uuid"] == owner_objects_post_terminate["uuid"]
    assert test_data["to"] == owner_objects_post_terminate["validity"]["to"]
