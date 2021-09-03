# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from fastapi import Request, Depends
from starlette.responses import JSONResponse

from starlette.status import HTTP_403_FORBIDDEN
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora import config
from os2mo_fastapi_utils.auth.oidc import get_auth_dependency


async def noauth() -> Token:
    """Noop auth provider."""
    return Token(azp='mo')


auth = get_auth_dependency(
    host=config.get_settings().keycloak_host,
    port=config.get_settings().keycloak_port,
    realm=config.get_settings().keycloak_realm,
    token_url_path='service/token',
    token_model=Token,
    http_schema=config.get_settings().keycloak_schema,
    alg=config.get_settings().keycloak_signing_alg,
    verify_audience=config.get_settings().keycloak_verify_audience
)
# TODO: Remove this, once a proper auth solution is in place,
#  that works for local DIPEX development.
#  https://redmine.magenta-aps.dk/issues/44020
if not config.get_settings().os2mo_auth:
    auth = noauth


def authorization_exception_handler(
    request: Request,
    err: AuthorizationError
) -> JSONResponse:

    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content={
            'status': 'Forbidden',
            'msg': str(err)
        }
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
