# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio

from fastapi import Request
from structlog import get_logger

import mora.auth.keycloak.uuid_extractor as uuid_extractor
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.owner import get_owners
from mora.mapping import ADMIN
from mora.mapping import OWNER

logger = get_logger()


async def _rbac(token: Token, request: Request, admin_only: bool) -> None:
    """
    Role based access control (RBAC) dependency function for the FastAPI
    endpoints that require authorization in addition to authentication. The
    function just returns, if the user is authorized and throws an
    AuthorizationError if the user is not authorized. A user with the admin
    role set in the Keycloak token is always authorized. A users with the owner
    role set in the Keycloak token is only authorized if the user is the owner
    of the org unit(s) subject to modification or one of the units ancestors.
    A user with no roles set is not authorized.

    :param token: selected JSON values from the Keycloak token
    :param request: the incoming FastAPI request.
    :param admin_only: true if endpoint only accessible to admins
    """

    logger.debug("_rbac called")

    roles = token.realm_access.roles

    if ADMIN in roles:
        logger.debug("User has admin role - write permission granted")
        return
    if OWNER in roles and not admin_only:
        logger.debug("User has owner role - checking ownership...")

        # E.g. the uuids variable will be {<uuid1>} if we are editing details
        # of an org unit or an employee and {<uuid1>, <uuid2>} if we are
        # moving an org unit
        uuids = await uuid_extractor.get_entity_uuids(request)
        logger.debug("UUIDs", uuids=uuids)

        entity_type = await uuid_extractor.get_entity_type(request)

        # In some cases several ancestor owner sets are needed, e.g. if
        # we are moving a unit. In such cases we have to check for
        # ownerships in both the source (the unit to be moved) and target
        # (the receiving unit) ancestor trees. In some cases only the
        # source is relevant, e.g. if an org unit detail is created/edited.
        # The owners list below will have exactly two elements (sets) if we
        # are moving a unit and exactly one element otherwise, e.g.
        # {{<owner_uuid>, <owner_parent_uuid>, <owner_grand_parent_uuid>}}
        # when editing details of a unit and
        # {
        #   {<src_owner_uuid>, <src_owner_parent_uuid>, <src_owner_grand_parent_uuid>},
        #   {<tar_owner_uuid>, <tar_owner_parent_uuid>, <tar_owner_grand_parent_uuid>}
        # }
        # when moving an org unit.

        owners = await asyncio.gather(
            *(get_owners(uuid, entity_type) for uuid in uuids)
        )

        current_user_ownership_verified = [(token.uuid in owner) for owner in owners]

        if current_user_ownership_verified and all(current_user_ownership_verified):
            logger.debug(f"User {token.preferred_username} authorized")
            return

    logger.debug(
        f"User {token.preferred_username} with UUID " f"{token.uuid} not authorized"
    )

    raise AuthorizationError("Not authorized to perform this operation")
