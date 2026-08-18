# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.mapping import ADMIN

logger = get_logger()


async def _rbac(token: Token) -> None:
    """
    Role based access control (RBAC) dependency function for the FastAPI
    endpoints that require authorization in addition to authentication. The
    function just returns, if the user is authorized and throws an
    AuthorizationError if the user is not authorized. Only a user with the
    admin role set in the Keycloak token is authorized. Ownership based
    authorization is exclusively available through GraphQL.

    :param token: selected JSON values from the Keycloak token
    """
    logger.debug("_rbac called")
    roles = token.realm_access.roles
    if ADMIN in roles:
        logger.debug("User has admin role - write permission granted")
        return

    logger.debug(
        f"User {token.preferred_username} with UUID {token.uuid} not authorized"
    )
    raise AuthorizationError("Not authorized to perform this operation")
