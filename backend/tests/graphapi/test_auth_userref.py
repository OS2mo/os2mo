# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from mora.auth.middleware import LORA_USER_UUID
from mora.db import AsyncSession
from mora.db import FacetRegistrering
from mora.mapping import ADMIN
from sqlalchemy import select

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "token_uuid, actor_uuid",
    [
        # Random token UUIDs -> those UUIDs
        (
            UUID("a2f13305-e49b-416a-b31c-8d80b24b269b"),
            UUID("a2f13305-e49b-416a-b31c-8d80b24b269b"),
        ),
        (
            UUID("6998caa6-aee7-4b03-889f-216c2b2cbc62"),
            UUID("6998caa6-aee7-4b03-889f-216c2b2cbc62"),
        ),
        # No UUID -> Faceless
        (
            None,
            LORA_USER_UUID,
        ),
    ],
)
async def test_create_facet(
    empty_db: AsyncSession,
    root_org: UUID,
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    token_uuid: UUID | None,
    actor_uuid: UUID,
) -> None:
    """Integrationtest for testing user references in LoRa."""
    # Change our token user to the specified UUID
    set_auth(ADMIN, token_uuid)

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

    assert brugerref == actor_uuid
