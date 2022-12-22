# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest

from mora import mapping
from mora.graphapi.versions.latest.graphql_utils import get_uuids
from oio_rest.db import get_connection
from tests.conftest import fake_auth
from tests.conftest import GQLResponse


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_facet(graphapi_post):
    """Integrationtest for testing user references in LoRa."""
    payload = {
        "user_key": "TestFacet",
        "org_uuid": str(await get_uuids(mapping.ORG, graphapi_post)),
    }
    mutate_query = """
        mutation CreateFacet($input: FacetCreateInput!) {
            facet_create(input: $input) {
                uuid
            }
        }
    """
    result: GQLResponse = graphapi_post(
        query=mutate_query, variables={"input": payload}
    )
    assert result.errors is None
    assert result.data
    facet_uuid = UUID(result.data["facet_create"]["uuid"])

    with get_connection().cursor() as cursor:
        cursor.execute(
            """
            SELECT (registrering).brugerref
            FROM facet_registrering
            WHERE facet_id = %(facet_uuid)s
            """,
            {"facet_uuid": str(facet_uuid)},
        )
        brugerref = cursor.fetchone()[0]

    user_ref = await fake_auth()
    assert str(brugerref) == str(user_ref["uuid"])
