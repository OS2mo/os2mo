# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from aiohttp import ClientSession
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from mora import config


def keycloak_router():
    router = APIRouter()

    settings = config.get_settings()

    SCHEMA = settings.keycloak_schema
    HOST = settings.keycloak_host
    PORT = settings.keycloak_port
    REALM = settings.keycloak_realm

    @router.head("/keycloak.json")
    @router.get("/keycloak.json")
    async def get_keycloak_config() -> dict[str, Any]:  # pragma: no cover
        """Frontend keycloak configuration endpoint."""
        return {
            "realm": REALM,
            "auth-server-url": settings.keycloak_auth_server_url,
            "ssl-required": settings.keycloak_ssl_required,
            "resource": settings.keycloak_mo_client,
            "public-client": True,
            "confidential-port": 0,
        }

    @router.post("/token")
    async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
    ) -> dict[str, Any]:  # pragma: no cover
        """Login endpoint to exchange username + password for access token."""
        token_url = (
            f"{SCHEMA}://{HOST}:{PORT}"
            f"/auth/realms/{REALM}/protocol/openid-connect/token"
        )

        if form_data.grant_type and form_data.grant_type != "password":
            raise HTTPException(status_code=406, detail="grant_type must be 'password'")
        if form_data.client_id:
            raise HTTPException(status_code=406, detail="client_id must be left empty")
        if form_data.client_secret:
            raise HTTPException(
                status_code=406, detail="client_secret must be left empty"
            )
        if form_data.scopes:
            raise HTTPException(
                status_code=406, detail="client_scope must be left empty"
            )

        payload = {
            "client_id": settings.keycloak_mo_client,
            "username": form_data.username,
            "password": form_data.password,
            "grant_type": "password",
        }
        async with ClientSession() as session:
            response = await session.post(token_url, data=payload)
            payload = await response.json()
            if response.status >= 400:
                raise HTTPException(status_code=response.status, detail=payload)
            token = payload["access_token"]
            return {"access_token": token, "token_type": "Bearer"}

    return router
