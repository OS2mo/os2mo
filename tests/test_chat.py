# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response


@pytest.mark.integration_test
async def test_chat_page(admin_client: TestClient, empty_db) -> None:
    response = admin_client.get("/chat")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "OS2mo Chat" in response.text
    # The agent's tool executor goes straight to the GraphQL API as the user
    assert "execute_graphql" in response.text
    assert "/graphql" in response.text
    # Model calls are proxied, not made direct from the browser
    assert "/chat/llm" in response.text
    # Auth is the standard Keycloak Authorization Code + PKCE flow, not a
    # hand-entered token
    assert "mo-frontend" in response.text
    assert "code_challenge_method" in response.text


@pytest.mark.integration_test
async def test_llm_proxy_unconfigured(
    admin_client: TestClient, empty_db, set_settings: Callable[..., None]
) -> None:
    """Without a Gemini key the proxy reports 503 rather than calling out."""
    set_settings(CHAT_GEMINI_API_KEY="")
    response = admin_client.post("/chat/llm", json={"request": {"contents": []}})
    assert response.status_code == 503
    assert "chat_gemini_api_key" in response.json()["error"]


@pytest.mark.integration_test
async def test_llm_proxy_requires_request(admin_client: TestClient, empty_db) -> None:
    """A payload without a request body is rejected before any outbound call."""
    response = admin_client.post("/chat/llm", json={"model": "anything"})
    assert response.status_code == 400
    assert response.json()["error"] == "Missing request."


@pytest.mark.integration_test
async def test_llm_proxy_forwards_to_gemini(
    admin_client: TestClient,
    empty_db,
    set_settings: Callable[..., None],
    respx_mock: respx.MockRouter,
) -> None:
    """The proxy injects the key and the configured model, ignoring the client."""
    set_settings(
        CHAT_GEMINI_API_KEY="test-key", CHAT_GEMINI_MODEL="gemini-3-flash-preview"
    )
    route = respx_mock.post(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-3-flash-preview:generateContent"
    ).mock(
        return_value=Response(
            200, json={"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}
        )
    )

    response = admin_client.post(
        "/chat/llm",
        # A client-supplied model must be ignored in favour of the configured one
        json={"model": "evil-model", "request": {"contents": []}},
    )

    assert response.status_code == 200
    assert response.json()["candidates"][0]["content"]["parts"][0]["text"] == "hi"
    assert route.called
    assert route.calls.last.request.headers["x-goog-api-key"] == "test-key"
