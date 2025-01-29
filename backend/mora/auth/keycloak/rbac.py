# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from structlog import get_logger

import mora.auth.keycloak.uuid_extractor as uuid_extractor
import mora.config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.owner import get_owners
from mora.graphapi.shim import execute_graphql
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import EntityType

logger = get_logger()


async def _get_employee_uuid_via_it_system(
    it_system: UUID, it_user_key: UUID | str
) -> UUID:
    """Return the employee UUID of the related it user.

    This is used to implement the
    `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configuration option.
    """

    query = """
    query GetEmployeeUUIDFromItUser($user_keys: [String!]!, $itsystem_uuids: [UUID!]!) {
      itusers(filter: {itsystem_uuids: $itsystem_uuids, user_keys: $user_keys}) {
        objects {
          current {
            employee_uuid
          }
        }
      }
    }
    """
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder(
            {"user_keys": it_user_key, "itsystem_uuids": it_system}
        ),
    )
    if r.errors or r.data is None:
        raise AuthorizationError("Error when looking up IT users")
    try:
        return UUID(one(r.data["itusers"]["objects"])["current"]["employee_uuid"])
    except ValueError:
        raise AuthorizationError("Expected exactly one matching IT user")


def _get_employee_uuid_via_token(token: Token) -> UUID:
    return token.uuid


async def _get_employee_uuid(token: Token) -> UUID:
    """Select employee UUID based on MOs configuration."""

    it_system = (
        mora.config.get_settings().keycloak_rbac_authoritative_it_system_for_owners
    )
    lookup_via_it_system = it_system is not None

    if lookup_via_it_system:
        return await _get_employee_uuid_via_it_system(it_system, token.uuid)
    return _get_employee_uuid_via_token(token)


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
    if admin_only:
        logger.debug("User is not admin, but endpoint is admin_only")
        raise AuthorizationError("Endpoint requires admin access. You're not admin!")

    if OWNER in roles:
        if token.uuid is None:
            raise AuthorizationError("User has owner role, but UUID unset.")
        logger.debug("User has owner role - checking ownership...")
        # E.g. the entity_uuids variable will be {<uuid1>} if we are editing details
        # of an org unit or an employee and {<uuid1>, <uuid2>} if we are
        # moving an org unit
        entity_type = await uuid_extractor.get_entity_type(request)
        entity_uuids = await uuid_extractor.get_entity_uuids(request)
        entities = {(entity_type, uuid) for uuid in entity_uuids}
        await check_owner(token, entities)
        logger.debug(f"User {token.preferred_username} authorized")
        return

    logger.debug(
        f"User {token.preferred_username} with UUID {token.uuid} not authorized"
    )
    raise AuthorizationError("Not authorized to perform this operation")


async def check_owner(token: Token, entities: set[tuple[EntityType, UUID]]) -> None:
    """Check if the token is owner of the given entities.

    This function is called from both the Service-API and GraphQL.
    """
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
    logger.debug("Check owner", entities=entities)
    user_uuid = await _get_employee_uuid(token)
    owners = await asyncio.gather(
        *(get_owners(entity_uuid, entity_type) for entity_type, entity_uuid in entities)
    )
    current_user_ownership_verified = [(user_uuid in owner) for owner in owners]
    if current_user_ownership_verified and all(current_user_ownership_verified):
        return None
    # This function intentionally returns None or raises (instead of returning a
    # boolean) because _get_employee_uuid() might also raise an AuthorizationError,
    # which we would like to propagate to the error message in the Service-API.
    raise AuthorizationError("Not owner")
