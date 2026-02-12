# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_parent_uuid(
    root_org: UUID,
    create_org_unit: Callable[[str, UUID | None], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    org_unit_uuid = create_org_unit("test", None)
    query = """
    query OrgUnitByUUID($filter: OrganisationUnitFilter) {
      org_units(filter: $filter) {
        objects {
          current {
            parent_uuid
            parent {
              uuid
            }
            parent_response {
              uuid
            }
          }
        }
      }
    }
    """

    # GraphQL v27 confusingly returned the root org's UUID for org-units
    # without a parent.
    response_v27 = graphapi_post(
        query,
        variables={"filter": {"uuids": [str(org_unit_uuid)]}},
        url="/graphql/v27",
    )
    assert response_v27.errors is None
    assert response_v27.data == {
        "org_units": {
            "objects": [
                {
                    "current": {
                        "parent_uuid": root_org,
                        "parent": None,
                        "parent_response": {"uuid": root_org},
                    }
                }
            ]
        }
    }

    # GraphQL v28 correctly returns none.
    response_v28 = graphapi_post(
        query,
        variables={"filter": {"uuids": [str(org_unit_uuid)]}},
        url="/graphql/v28",
    )
    assert response_v28.errors is None
    assert response_v28.data == {
        "org_units": {
            "objects": [
                {
                    "current": {
                        "parent_uuid": None,
                        "parent": None,
                        "parent_response": None,
                    }
                }
            ]
        }
    }
