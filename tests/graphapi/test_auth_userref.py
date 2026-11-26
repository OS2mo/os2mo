# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from sqlalchemy import select

from mora.db import AsyncSession
from mora.db import FacetRegistrering
from mora.mapping import ADMIN
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.fixture
def create_facet(graphapi_post: GraphAPIPost, root_org: UUID) -> Callable[[], UUID]:
    def inner() -> UUID:
        facet_create_mutation = """
            mutation CreateFacet($input: FacetCreateInput!) {
                facet_create(input: $input) {
                    uuid
                }
            }
        """
        payload = {
            "user_key": "TestFacet",
            "validity": {"from": "2012-03-04", "to": None},
        }

        result: GQLResponse = graphapi_post(
            query=facet_create_mutation, variables={"input": payload}
        )
        assert result.errors is None
        assert result.data
        facet_uuid = UUID(result.data["facet_create"]["uuid"])
        return facet_uuid

    return inner


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "token_uuid",
    [UUID("a2f13305-e49b-416a-b31c-8d80b24b269b"), None],
)
async def test_create_facet(
    empty_db: AsyncSession,
    create_facet: Callable[[], UUID],
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    token_uuid: UUID | None,
) -> None:
    """LoRa records the UUID of the actor, regardless of the token's UUID."""
    set_auth(ADMIN, token_uuid, "facet-creator")

    facet_uuid = create_facet()

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    response = graphapi_post("query { me { actor { uuid } } }")
    assert response.errors is None
    assert response.data
    assert brugerref == UUID(response.data["me"]["actor"]["uuid"])
    assert brugerref != token_uuid
