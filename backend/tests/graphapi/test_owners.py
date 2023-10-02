# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 1),
        # Employee filters
        ({"employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}, 1),
        ({"employees": "6ee24785-ee9a-4502-81c2-7697009c9053"}, 0),
        (
            {
                "employees": [
                    "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "6ee24785-ee9a-4502-81c2-7697009c9053",
                ]
            },
            1,
        ),
        # Organisation Unit filter
        ({"org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}, 1),
        ({"org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3"}, 0),
        (
            {
                "org_units": [
                    "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                ]
            },
            1,
        ),
        # Mixed filters
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            },
            0,
        ),
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
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
