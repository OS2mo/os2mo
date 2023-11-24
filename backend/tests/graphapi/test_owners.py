# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
