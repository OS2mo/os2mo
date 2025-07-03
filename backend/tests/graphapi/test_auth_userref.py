# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from fastapi import FastAPI
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import LORA_USER_UUID
from mora.db import AsyncSession
from mora.db import FacetRegistrering
from mora.graphapi.shim import execute_graphql
from mora.mapping import ADMIN
from sqlalchemy import select

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import admin_auth

FACET_CREATE_MUTATION = """
    mutation CreateFacet($input: FacetCreateInput!) {
        facet_create(input: $input) {
            uuid
        }
    }
"""
FACET_CREATE_PAYLOAD = {
    "user_key": "TestFacet",
    "validity": {"from": "2012-03-04", "to": None},
}


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

    result: GQLResponse = graphapi_post(
        query=FACET_CREATE_MUTATION, variables={"input": FACET_CREATE_PAYLOAD}
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
    # This intentionally uses execute_graphql to bypass the middleware
    response = await execute_graphql(
        query=FACET_CREATE_MUTATION, variable_values={"input": FACET_CREATE_PAYLOAD}
    )
    assert response.errors is None
    facet_uuid = UUID(response.data["facet_create"]["uuid"])

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    assert brugerref == LORA_USER_UUID


@pytest.mark.integration_test
async def test_unparsable_token(
    empty_db: AsyncSession,
    root_org: UUID,
    graphapi_post: GraphAPIPost,
    fastapi_admin_test_app: FastAPI,
) -> None:
    """Integrationtest for testing user references in LoRa."""
    token = await admin_auth()

    def _auth():
        return token

    def _token_getter():
        context = {"calls": 0}

        async def _get():
            if context["calls"] == 0:
                raise ValueError("BOOM")
            context["calls"] += 1
            return token

        return _get

    fastapi_admin_test_app.dependency_overrides[auth] = _auth
    fastapi_admin_test_app.dependency_overrides[token_getter] = _token_getter

    result: GQLResponse = graphapi_post(
        query=FACET_CREATE_MUTATION, variables={"input": FACET_CREATE_PAYLOAD}
    )
    assert result.errors is None
    assert result.data
    facet_uuid = UUID(result.data["facet_create"]["uuid"])

    brugerref = await empty_db.scalar(
        select(FacetRegistrering.actor).where(
            FacetRegistrering.facet_id == str(facet_uuid)
        )
    )

    assert brugerref == LORA_USER_UUID
