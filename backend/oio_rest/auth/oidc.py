# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from os2mo_fastapi_utils.auth.models import Token
from os2mo_fastapi_utils.auth.oidc import get_auth_dependency

from oio_rest import config

SCHEMA = config.get_settings().keycloak_schema
HOST = config.get_settings().keycloak_host
PORT = config.get_settings().keycloak_port
REALM = config.get_settings().keycloak_realm
ALG = config.get_settings().keycloak_signing_alg
VERIFY_AUDIENCE = config.get_settings().keycloak_verify_audience


async def noauth() -> Token:
    """Noop auth provider."""
    return Token(azp="lora")


auth = get_auth_dependency(
    host=HOST,
    port=PORT,
    realm=REALM,
    token_url_path="service/token",
    token_model=Token,
    http_schema=SCHEMA,
    alg=ALG,
    verify_audience=VERIFY_AUDIENCE,
)
if not config.get_settings().lora_auth:
    auth = noauth
