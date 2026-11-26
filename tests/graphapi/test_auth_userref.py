# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from sqlalchemy import select

from mora.auth.middleware import NO_AUTH_MIDDLEWARE_UUID
from mora.common import get_connector
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


@pytest.mark.integration_test
async def test_no_auth_middleware(
    empty_db: AsyncSession,
    root_org: UUID,
) -> None:
    """Integrationtest for testing user references in LoRa without middleware."""
    payload = {
        "attributter": {
            "facetegenskaber": [
                {
                    "brugervendtnoegle": "TestFacet",
                    "virkning": {"from": "1900-01-01", "to": "infinity"},
                }
            ]
        },
        "relationer": {
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": str(root_org),
                    "virkning": {"from": "1900-01-01", "to": "infinity"},
                }
            ],
            "facettilhoerer": [
                {
                    "objekttype": "klassifikation",
                    "uuid": "cdeecc2f-5f96-4a2c-b5df-a59d3a04de59",
                    "virkning": {"from": "1900-01-01", "to": "infinity"},
                }
            ],
        },
        "tilstande": {
            "facetpubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": {"from": "1900-01-01", "to": "infinity"},
                }
            ]
        },
    }

    # Programmatically creating a facet outside of a request flow
    connector = get_connector()
    facet_uuid = UUID(await connector.facet.create(payload))

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    assert brugerref == NO_AUTH_MIDDLEWARE_UUID
