# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from mora.db import AsyncSession
from mora.db import FacetRegistrering
from sqlalchemy import select

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import fake_auth


@pytest.mark.integration_test
async def test_create_facet(
    empty_db: AsyncSession, root_org: UUID, graphapi_post: GraphAPIPost
) -> None:
    """Integrationtest for testing user references in LoRa."""
    payload = {
        "user_key": "TestFacet",
        "validity": {"from": "2012-03-04", "to": None},
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

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    user_ref = await fake_auth()
    assert brugerref == user_ref.uuid
