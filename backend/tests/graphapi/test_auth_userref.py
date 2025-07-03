# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from mora.auth.middleware import LORA_USER_UUID
from mora.common import get_connector
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

    assert brugerref == LORA_USER_UUID
