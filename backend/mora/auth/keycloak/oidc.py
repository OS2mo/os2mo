# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from structlog import get_logger
from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR
)
import jwt.exceptions
from mora.auth.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from mora.auth.keycloak.models import Token
from mora import config

SCHEMA = config.get_settings().keycloak_schema
HOST = config.get_settings().keycloak_host
PORT = config.get_settings().keycloak_port
REALM = config.get_settings().keycloak_realm
ALG = config.get_settings().keycloak_signing_alg

# URI for obtaining JSON Web Key Set (JWKS), i.e. the public Keycloak key
JWKS_URI = f'{SCHEMA}://{HOST}:{PORT}' \
           f'/auth/realms/{REALM}/protocol/openid-connect/certs'


logger = get_logger()

# For getting and parsing the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='service/token')

# JWKS client for fetching and caching JWKS
jwks_client = jwt.PyJWKClient(JWKS_URI)


async def noauth() -> Token:
    """Noop auth provider."""
    return Token()


async def keycloak_auth(token: str = Depends(oauth2_scheme)) -> Token:
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

        decoded_token: dict = jwt.decode(token, signing.key, algorithms=[ALG])
        return Token.parse_obj(decoded_token)

    except Exception as err:
        raise AuthenticationError(err)


auth = keycloak_auth
# TODO: Remove this, once a proper auth solution is in place,
#  that works for local DIPEX development.
#  https://redmine.magenta-aps.dk/issues/44020
if not config.get_settings().os2mo_auth:
    auth = noauth


# Exception handler to be used by the FastAPI app object
def authentication_exception_handler(
    request: Request,
    err: AuthenticationError
) -> JSONResponse:
    if err.is_client_side_error():
        logger.exception('Client side authentication error', exception=err.exc)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={
                'status': 'Unauthorized',
                'msg': str(err.exc)
            }
        )

    logger.exception(
        'Problem communicating with the Keycloak server', exception=err.exc
    )

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={'msg': 'A server side authentication error occurred'}
    )


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


async def rbac_owner(request: Request, token: Token = Depends(auth)):
    """
    Role based access control (RBAC) dependency function for the FastAPI
    endpoints that require authorization in addition to authentication. The
    function just returns, if the user is authorized and throws an
    AuthorizationError if the user is not authorized. If the RBAC feature is
    not enabled the function will just return immediately.

    :param request: the incoming FastAPI request.
    :param token: selected JSON values from the Keycloak token
    """

    if not config.get_settings().keycloak_rbac_enabled:
        return

    # This special import structure is currently required to avoid circular
    # import problems in the Python code
    from mora.auth.keycloak.rbac import _rbac
    return await _rbac(token, request, False)
