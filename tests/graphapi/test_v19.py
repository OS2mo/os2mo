# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_facet_validity(graphapi_post: GraphAPIPost) -> None:
    """Test facet behaviour."""
    mutation = """
        mutation FacetCreate {
          facet_create(input: {user_key: "test", validity: {to: "2010-11-12"}}) {
            uuid
          }
        }
    """

    response_create: GQLResponse = graphapi_post(mutation, url="/graphql/v19")
    facet_uuid = response_create.data["facet_create"]["uuid"]

    query = """
        query GetFacet($uuid: UUID!) {
          facets(filter: {uuids: [$uuid]}) {
            objects {
              current {
                user_key
              }
            }
          }
        }
    """
    query_variables = {"uuid": facet_uuid}

    # GraphQL versions prior to v20 ignored facet start and end dates, returning an
    # empty 'current' object.
    response_v19: GQLResponse = graphapi_post(
        query, query_variables, url="/graphql/v19"
    )
    assert response_v19.errors is None
    assert response_v19.data == {
        "facets": {
            "objects": [
                {
                    "current": None,
                }
            ]
        }
    }

    # After v20, facets are correctly filtered on their start and end dates, thus the
    # entire object is filtered from the 'current' query.
    response_v20: GQLResponse = graphapi_post(
        query, query_variables, url="/graphql/v20"
    )
    assert response_v20.errors is None
    assert response_v20.data == {"facets": {"objects": []}}
