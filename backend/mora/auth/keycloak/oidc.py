# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR
)
import jwt.exceptions
from mora.auth.exceptions import AuthError
from mora.settings import config

SCHEMA = config['auth']['keycloak_schema']
HOST = config['auth']['keycloak_host']
PORT = config['auth']['keycloak_port']
REALM = config['auth']['keycloak_realm']
ALG = config['auth']['keycloak_signing_alg']

# URI for obtaining JSON Web Key Set (JWKS), i.e. the public Keycloak key
JWKS_URI = f'{SCHEMA}://{HOST}:{PORT}' \
           f'/auth/realms/{REALM}/protocol/openid-connect/certs'

logger = logging.getLogger(__name__)

# For getting and parsing the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='unused')

# JWKS client for fetching and caching JWKS
jwks_client = jwt.PyJWKClient(JWKS_URI)


async def auth(request: Request) -> dict:
    """
    Ensure the caller has a valid OIDC token, i.e. that the Authorization
    header is set with a valid bearer token.

    :param request: Incoming request
    :return: parsed (JWT) token

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
            "scope": "email profile",
            "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
            "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
            "typ": "Bearer"
        }

    """

    # TODO: Remove this, once a proper auth solution is in place,
    #  that works for local DIPEX development.
    #  https://redmine.magenta-aps.dk/issues/44020
    if config["ENV"] in ["development", "testing"]:
        return {}

    try:
        token = await oauth2_scheme(request)

        # Get the public signing key from Keycloak. The JWKS client uses an
        # lru_cache, so it will not make an HTTP request to Keycloak each time
        # get_signing_key_from_jwt() is called.

        signing = jwks_client.get_signing_key_from_jwt(token)

        # The jwt.decode() method raises an exception (e.g.
        # InvalidSignatureError, ExpiredSignatureError,...) in case the OIDC
        # token is invalid. These exceptions will be caught by the
        # auth_exception_handler below which is used by the FastAPI app.

        return jwt.decode(token, signing.key, algorithms=[ALG])

    except Exception as err:
        raise AuthError(err)


# Exception handler to be used by the FastAPI app object
def auth_exception_handler(request: Request, err: AuthError) -> JSONResponse:
    if err.is_client_side_error():
        logger.debug('Client side authentication error: ' + str(err.exc))
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={'msg': 'Unauthorized'}
        )

    logger.error(
        'Problem communicating with the Keycloak server: ' + str(err.exc)
    )

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={'msg': 'A server side authentication error occurred'}
    )
