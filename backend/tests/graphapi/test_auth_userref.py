# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from fastapi import FastAPI
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import LORA_USER_UUID
from mora.common import get_connector
from mora.db import AsyncSession
from mora.db import FacetRegistrering
from mora.mapping import ADMIN
from sqlalchemy import select

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import admin_auth


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
    create_facet: Callable[[], UUID],
    set_auth: SetAuth,
    token_uuid: UUID | None,
    actor_uuid: UUID,
) -> None:
    """Integrationtest for testing user references in LoRa."""
    # Change our token user to the specified UUID
    set_auth(ADMIN, token_uuid)

    facet_uuid = create_facet()

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


@pytest.mark.integration_test
async def test_unparsable_token(
    empty_db: AsyncSession,
    create_facet: Callable[[], UUID],
    fastapi_admin_test_app: FastAPI,
) -> None:
    """Integrationtest for testing user references in LoRa."""
    token = await admin_auth()

    def _auth():
        return token

    def _token_getter():
        context = {"calls": 0}

        async def _get():
            context["calls"] += 1
            if context["calls"] == 1:
                raise ValueError("BOOM")
            return token

        return _get

    fastapi_admin_test_app.dependency_overrides[auth] = _auth
    fastapi_admin_test_app.dependency_overrides[token_getter] = _token_getter

    facet_uuid = create_facet()

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    assert brugerref == LORA_USER_UUID
