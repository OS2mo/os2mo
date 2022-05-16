# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from fastapi import Depends
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from os2mo_fastapi_utils.auth.oidc import get_auth_dependency
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from structlog import get_logger

from mora import config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.legacy import validate_session
from mora.auth.keycloak.models import Token

logger = get_logger()


async def noauth() -> Token:
    """Noop auth provider."""
    return Token(azp="mo-frontend", uuid="00000000-0000-0000-0000-000000000000")


keycloak_auth = get_auth_dependency(
    host=config.get_settings().keycloak_host,
    port=config.get_settings().keycloak_port,
    realm=config.get_settings().keycloak_realm,
    token_url_path="service/token",
    token_model=Token,
    http_schema=config.get_settings().keycloak_schema,
    alg=config.get_settings().keycloak_signing_alg,
    verify_audience=config.get_settings().keycloak_verify_audience,
)


async def validate_token(token: str) -> Token:
    """Validate a keycloak token.

    Args:
        The token to be validated.

    Returns:
        Whether the token was validated.
    """
    return await keycloak_auth(token)


async def legacy_auth_adapter(request: Request) -> Token:
    """
    Legacy support for the old session database to allow for grace-period before
    switching to Keycloak auth

    We check for a session header and allow people to access the application if
    they have a session that exists in the old session database

    If no header exists, or session token is invalid, we fall back to Keycloak auth
    """
    session_id = request.headers.get("session")
    if session_id:
        logger.warning("Legacy session token used")
        if validate_session(session_id):
            return await noauth()
    oauth2_scheme = await OAuth2PasswordBearer(tokenUrl="service/token")(request)
    return await validate_token(oauth2_scheme)


# TODO: Remove this, once a proper auth solution is in place,
#  that works for local DIPEX development.
#  https://redmine.magenta-aps.dk/issues/44020
if not config.get_settings().os2mo_auth:
    auth = noauth
elif config.get_settings().os2mo_legacy_session_support:
    auth = legacy_auth_adapter
else:
    auth = keycloak_auth


def authorization_exception_handler(
    request: Request, err: AuthorizationError
) -> JSONResponse:

    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN, content={"status": "Forbidden", "msg": str(err)}
    )


async def rbac(request: Request, admin_only: bool, token: Token = Depends(auth)):
    """
    Role based access control (RBAC) dependency function for the FastAPI
    endpoints that require authorization in addition to authentication. The
    function just returns, if the user is authorized and throws an
    AuthorizationError if the user is not authorized. If the RBAC feature is
    not enabled the function will just return immediately.

    :param request: the incoming FastAPI request.
    :param admin_only:  if true, the endpoint can only be called by the admin role
    :param token: selected JSON values from the Keycloak token
    """

    if not config.get_settings().keycloak_rbac_enabled:
        return

    # This special import structure is currently required to avoid circular
    # import problems in the Python code
    from mora.auth.keycloak.rbac import _rbac

    return await _rbac(token, request, admin_only)


async def rbac_admin(request: Request, token: Token = Depends(auth)):
    return await rbac(request, True, token)


async def rbac_owner(request: Request, token: Token = Depends(auth)):
    return await rbac(request, False, token)
