# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Chatbox frontend prototype.

Serves a single-file chat UI which runs an LLM agent loop in the browser.
The model is given one tool, execute_graphql, which the page executes by
calling our own GraphQL API with the user's bearer token, so the chatbot
can never do more than the logged-in user is allowed to.

Gemini cannot be called directly from the browser (no CORS, and the API key
would leak), so the page proxies each model call through the auth-gated
/chat/llm endpoint, which injects the Gemini API key server-side.
"""

import re
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from mora import config
from mora.auth.keycloak.oidc import auth

router = APIRouter()

# Gemini model names are embedded in the request URL path, so restrict them to
# avoid path traversal or hitting unintended endpoints.
_MODEL_RE = re.compile(r"^[a-zA-Z0-9.\-]+$")


@router.get("", response_class=HTMLResponse)
async def chat_page() -> str:
    """Serve the chatbox single-page app."""
    return (Path(__file__).parent / "index.html").read_text()


@router.post("/llm", dependencies=[Depends(auth)])
async def llm_proxy(payload: dict[str, Any] = Body(...)) -> JSONResponse:
    """Proxy a single Gemini generateContent call, injecting the API key.

    The browser sends ``{"request": {<generateContent body>}}``. The model is
    fixed by configuration, not chosen by the client. Authentication is
    required, so only logged-in users can spend the org's Gemini quota, and
    the API key never leaves the server.
    """
    request_body = payload.get("request")
    if not isinstance(request_body, dict):
        return JSONResponse(status_code=400, content={"error": "Missing request."})

    settings = config.get_settings()
    model = settings.chat_gemini_model
    if not settings.chat_gemini_api_key or not _MODEL_RE.match(model):
        return JSONResponse(
            status_code=503,
            content={"error": "Chatbox is not configured (chat_gemini_api_key)."},
        )

    url = f"{settings.chat_gemini_base_url}/models/{model}:generateContent"
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            url,
            headers={"x-goog-api-key": settings.chat_gemini_api_key},
            json=request_body,
        )
    # Forward Gemini's response verbatim so the browser can handle errors too.
    return JSONResponse(status_code=response.status_code, content=response.json())
