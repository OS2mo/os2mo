# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest.mock
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from fastapi.exceptions import HTTPException
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidAudienceError
from jwt.exceptions import InvalidSignatureError
from jwt.exceptions import InvalidTokenError
from jwt.exceptions import PyJWTError
from mora.auth.exceptions import AuthenticationError
from mora.auth.exceptions import get_auth_exception_handler
from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import get_auth_dependency
from pydantic import ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from structlog import get_logger


@pytest.fixture
def signing() -> jwt.PyJWT:
    """Used for mocking the Keycloak public key."""
    jwtRS256_pub = b"""
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAxvD/gKyDYrUjyrWRZEE4
ySZ+bdO5vN/yhlCkpley8wcBZxiPrkYZBMJe5BCwyjCyYkL6ujcw61VdrrUwSwC+
FXyLYCfr3Jn6gm+xwE9bjyEcWYMi001Ndu2eH7qFZC44R6131X1qTFMPZgIoFLyj
l7WiStyJTRnqXZkGIf9AM2qh+fA9nVbjd+dNJfJJyohJ1e/U4dBAorwKXi9KT1/r
SGs7hugvURcpMJYpwGJTCZJLXTn/aam8uBns6GT3SEUP89eQnRo8osXOPZensKtQ
WoX8qN0FbSt3uGYDXrZQZeEg9mpBKvGqvhI7DWOHhDkfmguC54oFf8BJqmhj7HGa
xDS9CO/vwPOxm5G6rb/bNtoP2S6IkPbq2JZwvSfYL+F8adwSqvwzqyZ2Y3OMhjh5
1Bqx4ywd9g5lTek8QJLitg0Ln+I/cy1QYpCQCIJWsBiqav0ntEiyIsYcR9oKCAtB
mtCs74v8fgA22tzk+NrPGtbm2jmtAzEXAo8Ero+k32Hwg/cvt8XyUxpLqqH3eujC
guln+klKjYAAm4GjAgCZLJfLOeYtLQhpcdDHXNIDj0+kODbvwrvkDzY1JdLVLNNU
Hh057MxnDaCj6j+UQXCaeddpfVdsfoScJjGgcSdGmfw7he+xC610WSAmrfaEQzkp
HMROYWbxPhu/DyTgQozGzWUCAwEAAQ==
-----END PUBLIC KEY-----
    """
    public_key = serialization.load_pem_public_key(jwtRS256_pub)
    signing = jwt.PyJWT({"kty": "RSA"})
    setattr(signing, "key", public_key)
    return signing


@pytest.fixture(scope="session")
def private_key() -> bytes:
    """Used for mocking the Keycloak private key."""
    jwtRS256 = b"""
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
    """
    return jwtRS256


@pytest.fixture(scope="session")
def hackers_key() -> bytes:
    """Used for mocking the Keycloak hacker's key."""
    jwtRS256 = b"""
-----BEGIN RSA PRIVATE KEY-----
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
oVFpAoIBAQCHhpGe/TGxxJGJD/ZLRUlGJno+JHV7Ls/CLeaFBjj+WE9XR0WlFIj3
IwLMeOIjIBwWn2ATHBCQWdSx4za7ts0gSt5tLjRbCB8+DcscmOM0PshpNwh+X1YN
yURfgMAF8eAnZa5/iTpcwtuTiXdGvzSxArYeUIP5Tmvvuie1UEnvRn0mOvXrBosQ
RR9ZjXP8PZjwee7Yv5iuTfkTJbGrBkt6NJa5VGpS2fz43vAgyOEj/KqKPeYQABVt
0ckOy3nIkJRZ9XQRV1h0nQs3F5MwzHDj3t/97bGmj/Vr8J+YjyOUOIj8Zyx6VWC6
HyioSQz235SEbMbWTbepmnpIpSZVm315AoIBAQChha2ukCOueFzcWkx9CqRk/n7R
vngvmEvzK/VW4/7UKgrcwOumy5VmsYG+cIu7D2LXD69ojpe8wj60Om+tfhEIQdeP
pRtMjKozFzSV3vw2QbJF3zCTL7G+Ao+17Nn44pBnBV8DT0hK2IS9A4V/oqC8pbYu
oKTQG2bE+aSJo8HEK4Lbnd6/3bNBszymO9Kj+XixAXsqTVI3b8o6XxNo84kkKKHj
x3AlW98cY2DfWF3leMR8juTXafIcSgpFeompEUuG1KKWe+Wz38hdmKffcTWl0h6V
nHNHk/srBIhWYfTLko15x0JW4JII6B+Smw6u4GyJvHaxaf8oDYHSzWeSPPWx
-----END RSA PRIVATE KEY-----
    """
    return jwtRS256


@pytest.fixture
def parsed_token() -> dict[str, Any]:
    """Used for mocking the OIDC token."""
    return {
        "acr": "1",
        "allowed-origins": ["http://localhost:5001"],
        "azp": "mo",
        "email": "bruce@kung.fu",
        "email_verified": False,
        "exp": int(datetime.now().timestamp()) + 300,
        "family_name": "Lee",
        "given_name": "Bruce",
        "iat": int(datetime.now().timestamp()),
        "iss": "http://localhost:8081/auth/realms/mo",
        "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
        "name": "Bruce Lee",
        "preferred_username": "bruce",
        "scope": "email profile",
        "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
        "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
        "typ": "Bearer",
        "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
    }


auth = get_auth_dependency(
    host="keycloak",
    port=8080,
    realm="mo",
    token_url_path="service/token",
    token_model=Token,
)


def generate_token(parsed_token: dict, key: bytes) -> str:
    """
    Generate a request containing an auth header with a OIDC Bearer token
    :param parsed_token: parsed token (see example above)
    :param key: The JWK to sign the token with
    """
    token = jwt.encode(parsed_token, key, algorithm="RS256")
    return token


def test_auth_exception_handler_return_401_for_client_side_error() -> None:
    exc = AuthenticationError(InvalidSignatureError())
    authentication_exception_handler = get_auth_exception_handler(get_logger())

    assert (
        authentication_exception_handler(None, exc).status_code == HTTP_401_UNAUTHORIZED
    )


def test_auth_exception_handler_return_500_for_server_side_error() -> None:
    exc = AuthenticationError(PyJWTError())
    authentication_exception_handler = get_auth_exception_handler(get_logger())
    assert (
        authentication_exception_handler(None, exc).status_code
        == HTTP_500_INTERNAL_SERVER_ERROR
    )


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_auth_decodes_token(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Create auth request with token signed by correct key
    token = generate_token(parsed_token, private_key)

    actual_token = await auth(token)
    expected_token = Token(
        azp="mo",
        email="bruce@kung.fu",
        preferred_username="bruce",
        uuid=UUID("99e7b256-7dfa-4ee8-95c6-e3abe82e236a"),
    )

    assert actual_token == expected_token


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_leeway(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Set "exp" to a slightly expired timestamp
    parsed_token["exp"] = int(datetime.now().timestamp()) - 3

    # Create auth request with token signed by correct key
    token = generate_token(parsed_token, private_key)

    actual_token = await auth(token)
    expected_token = Token(
        azp="mo",
        email="bruce@kung.fu",
        preferred_username="bruce",
        uuid=UUID("99e7b256-7dfa-4ee8-95c6-e3abe82e236a"),
    )

    assert actual_token == expected_token


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_raise_exception_for_invalid_signature(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    hackers_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Create auth request with token signed with hackers key
    token = generate_token(parsed_token, hackers_key)

    with pytest.raises(AuthenticationError) as exc_info:
        await auth(token)
        assert isinstance(exc_info.value.exc, InvalidSignatureError)


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_raise_exception_for_expired_token(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Set "exp" to an expired timestamp
    parsed_token["exp"] = int(datetime.now().timestamp()) - 6

    # Create auth request with token signed by correct key
    token = generate_token(parsed_token, private_key)

    with pytest.raises(AuthenticationError) as exc_info:
        await auth(token)
        assert isinstance(exc_info.value.exc, ExpiredSignatureError)


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_ensure_get_signing_from_jwt_called(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]
    token = generate_token(parsed_token, private_key)

    await auth(token)

    token = jwt.encode(parsed_token, private_key, algorithm="RS256")

    mock_get_signing_key_from_jwt.assert_called_once_with(token)


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_exception_when_aud_in_token_and_audience_is_not_set(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Set aud in token
    parsed_token["aud"] = "mo"
    token = generate_token(parsed_token, private_key)

    with pytest.raises(AuthenticationError) as exc_info:
        await auth(token)
        assert isinstance(exc_info.value.exc, InvalidAudienceError)


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_token_accepted_when_aud_in_token_and_audience_is_set(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Set aud in token
    parsed_token["aud"] = "mo"
    token = generate_token(parsed_token, private_key)

    auth = get_auth_dependency(
        host="keycloak",
        port=8080,
        realm="mo",
        token_url_path="service/token",
        token_model=Token,
        audience="mo",
    )

    assert await auth(token)


@unittest.mock.patch("mora.auth.keycloak.oidc.jwt.PyJWKClient.get_signing_key_from_jwt")
async def test_token_accepted_when_aud_in_token_and_verify_aud_is_false(
    mock_get_signing_key_from_jwt,
    signing: jwt.PyJWT,
    parsed_token: dict[str, Any],
    private_key: bytes,
):
    # Mock the public signing.key used in the auth function
    mock_get_signing_key_from_jwt.side_effect = [signing]

    # Set aud in token
    parsed_token["aud"] = "mo"
    token = generate_token(parsed_token, private_key)

    auth = get_auth_dependency(
        host="keycloak",
        port=8080,
        realm="mo",
        token_url_path="service/token",
        token_model=Token,
        verify_audience=False,
    )

    assert await auth(token)


def test_exception_set_correctly() -> None:
    exc = AuthenticationError(InvalidSignatureError())
    assert isinstance(exc.exc, InvalidSignatureError)


def test_is_client_side_error_true_for_invalid_token_error() -> None:
    exc = AuthenticationError(InvalidTokenError())
    assert exc.is_client_side_error()


def test_is_client_side_error_true_for_http_exception_401() -> None:
    exc = AuthenticationError(HTTPException(status_code=HTTP_401_UNAUTHORIZED))
    assert exc.is_client_side_error()


def test_is_client_side_error_false_for_http_exception_500() -> None:
    exc = AuthenticationError(HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR))
    assert not exc.is_client_side_error()


def test_is_client_side_error_false_for_server_error() -> None:
    exc = AuthenticationError(PyJWTError())
    assert not exc.is_client_side_error()


def test_azp_mandatory() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Token()
    errors = exc_info.value.errors()[0]

    assert errors["loc"] == ("azp",)
    assert errors["type"] == "value_error.missing"


def test_should_ignore_extra_fields() -> None:
    token = Token(azp="some-client", extra=0)
    with pytest.raises(AttributeError):
        token.extra


def test_should_set_realm_access_to_default_value() -> None:
    token = Token(azp="some-client")
    assert token.realm_access.roles == set()


def test_should_set_roles_correctly() -> None:
    roles = {"admin", "owner"}
    token = Token(azp="some-client", realm_access=RealmAccess(roles=roles))
    assert token.realm_access.roles == roles


def test_invalid_email_address_not_allowed() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Token(azp="mo", uuid=uuid4(), email="Invalid email")
    errors = exc_info.value.errors()[0]

    assert errors["loc"] == ("email",)
    assert errors["type"] == "value_error.email"


def test_token_with_all_fields_set() -> None:
    uuid = uuid4()
    roles = {"admin", "owner"}
    token = Token(
        azp="mo",
        email="bruce@kung.fu",
        preferred_username="bruce",
        realm_access=RealmAccess(roles=roles),
        uuid=uuid,
    )

    assert token.azp == "mo"
    assert token.email == "bruce@kung.fu"
    assert token.preferred_username == "bruce"
    assert token.realm_access.roles == roles
    assert token.uuid == uuid
