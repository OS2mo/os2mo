# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Union

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.types import Info
from strawberry.permission import BasePermission

from mora import config
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import rbac
from mora.auth.exceptions import AuthorizationError


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Checks if a valid OIDC token was sent in the Authorization header."""
        # Auth disabled -> Full access
        if not config.get_settings().graphql_auth:
            return True

        request: Union[Request, WebSocket] = info.context["request"]

        # TODO: Currently we cannot use auth directly as it uses FastAPI's Depends
        #       Maybe we should offer a non-'Depends' version?
        token_url_path = "service/token"
        try:
            oauth2_scheme = await OAuth2PasswordBearer(tokenUrl=token_url_path)(request)
        except HTTPException as exc:
            raise PermissionError(exc.detail)

        token = await auth(token=oauth2_scheme)
        try:
            await rbac(request, admin_only=False, token=token)
        except AuthorizationError:
            return False
        return True
