# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

import jwt.exceptions
from fastapi import Depends
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from starlette_context import context
from structlog import get_logger

from mora import config
from mora.auth.exceptions import AuthenticationError
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.legacy import validate_session
from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.graphapi.versions.latest.permissions import ALL_PERMISSIONS

logger = get_logger()


NO_AUTH_UUID = UUID("00000000-0000-0000-0000-000000000000")
LEGACY_AUTH_UUID = UUID("00000000-0000-0000-0000-000000000001")


async def noauth() -> Token:
    """Noop auth provider."""
    return Token(
        azp="mo-frontend",
        uuid=str(NO_AUTH_UUID),
        realm_access=RealmAccess(roles={"admin", "owner"}.union(ALL_PERMISSIONS)),
    )


async def legacyauth() -> Token:  # pragma: no cover
    """Legacy auth provider."""
    return Token(
        azp="mo-frontend",
        uuid=str(LEGACY_AUTH_UUID),
        realm_access=RealmAccess(
            roles={"admin", "owner", "service_api"}.union(ALL_PERMISSIONS)
        ),
    )


TokenModel = TypeVar("TokenModel", bound=Token)


def get_auth_dependency(
    host: str,
    port: int,
    realm: str,
    token_url_path: str,
    token_model: type[TokenModel],
    http_schema: str = "http",
    alg: str = "RS256",
    verify_audience: bool = True,
    audience: str | list[str] | None = None,
):
    # URI for obtaining JSON Web Key Set (JWKS), i.e. the public Keycloak key
    JWKS_URI = (
        f"{http_schema}://{host}:{port}"
        f"/auth/realms/{realm}/protocol/openid-connect/certs"
    )

    # JWKS client for fetching and caching JWKS
    jwks_client = jwt.PyJWKClient(JWKS_URI)

    # For getting and parsing the Authorization header
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url_path)

    async def keycloak_auth(token: str = Depends(oauth2_scheme)) -> TokenModel:
        """
        Ensure the caller has a valid OIDC token, i.e. that the Authorization
        header is set with a valid bearer token.

        :param token: encoded Keycloak token
        :return: selected JSON values from the Keycloak token

        **Example return value**

        .. sourcecode:: json

            {
                "acr": "1",
                "allowed-origins": ["http://localhost:5001"],
                "azp": "mo",
                "email": "bruce@kung.fu",
                "email_verified": false,
                "exp": 1621779689,
                "family_name": "Lee",
                "given_name": "Bruce",
                "iat": 1621779389,
                "iss": "http://localhost:8081/auth/realms/mo",
                "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
                "name": "Bruce Lee",
                "preferred_username": "bruce",
                "realm_access": {
                    "roles": [
                      "admin"
                  ]
                },
                "scope": "email profile",
                "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
                "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
                "typ": "Bearer",
                "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a"
            }

        """

        try:
            # Get the public signing key from Keycloak. The JWKS client uses an
            # lru_cache, so it will not make an HTTP request to Keycloak each time
            # get_signing_key_from_jwt() is called.

            signing = jwks_client.get_signing_key_from_jwt(token)

            # The jwt.decode() method raises an exception (e.g.
            # InvalidSignatureError, ExpiredSignatureError,...) in case the OIDC
            # token is invalid. These exceptions will be caught by the
            # auth_exception_handler below which is used by the FastAPI app.

            # The audience verification can be disabled (aud
            # claim in the token) when all services in the stack trust
            # each other
            # (see https://www.keycloak.org/docs/latest/server_admin/index.html#_audience)
            decoded_token: dict = jwt.decode(
                token,
                signing.key,
                algorithms=[alg],
                audience=audience,
                options={"verify_aud": verify_audience},
                leeway=5,
            )

            return token_model.parse_obj(decoded_token)

        except Exception as err:
            raise AuthenticationError(err)

    return keycloak_auth


token_url_path = "service/token"
keycloak_auth = get_auth_dependency(
    host=config.get_settings().keycloak_host,
    port=config.get_settings().keycloak_port,
    realm=config.get_settings().keycloak_realm,
    token_url_path=token_url_path,
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


async def fetch_keycloak_token(request: Request) -> Token:
    oauth2_scheme = await OAuth2PasswordBearer(tokenUrl=token_url_path)(request)
    return await validate_token(oauth2_scheme)


async def legacy_auth_adapter(request: Request) -> Token:  # pragma: no cover
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
            return await legacyauth()
    return await fetch_keycloak_token(request)


# TODO: Remove this, once a proper auth solution is in place,
#  that works for local DIPEX development.
#  https://redmine.magenta-aps.dk/issues/44020
if not config.get_settings().os2mo_auth:  # pragma: no cover
    auth = noauth
elif config.get_settings().os2mo_legacy_sessions:  # pragma: no cover
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


def token_getter(request: Request) -> Callable[[], Awaitable[Token]]:
    """Programatically get a Token using whatever backend has been configured.

    Args:
        request: The FastAPI request object to extract the token from.

    Returns:
        The extracted or dummy token object or None, if validation fails.
    """

    async def get_token():
        if token := context.get("token", False):
            return token

        if auth == noauth:  # pragma: no cover
            result = await noauth()
        elif auth == legacy_auth_adapter:  # pragma: no cover
            result = await legacy_auth_adapter(request)
        else:
            result = await fetch_keycloak_token(request)

        context["token"] = result
        return result

    return get_token


def service_api_auth(token: Token = Depends(auth)) -> None:
    """Check if the Service API role is set."""
    roles = token.realm_access.roles

    if "service_api" not in roles:
        raise AuthorizationError("The Service API is gone")

    logger.debug("Service API access granted", actor=token.uuid)
