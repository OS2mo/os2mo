# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from sqlalchemy import exists
from sqlalchemy import select
from structlog import get_logger

import mora.auth.keycloak.uuid_extractor as uuid_extractor
import mora.config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.db import BrugerRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.graphapi.shim import execute_graphql
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import EntityType

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

logger = get_logger()


async def _get_employee_uuid_via_it_system(
    it_system: UUID, it_external_id: UUID | str
) -> UUID:
    """Return the employee UUID of the related it user.

    This is used to implement the
    `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configuration option.
    """

    query = """
    query GetEmployeeUUIDFromItUser($filter: ITUserFilter!) {
      itusers(filter: $filter) {
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
            {
                "filter": {
                    "itsystem": {"uuids": [it_system]},
                    "external_ids": [it_external_id],
                }
            },
        ),
    )
    if r.errors or r.data is None:  # pragma: no cover
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
        await check_owner_serviceapi(token, entities)
        logger.debug(f"User {token.preferred_username} authorized")
        return

    logger.debug(
        f"User {token.preferred_username} with UUID {token.uuid} not authorized"
    )
    raise AuthorizationError("Not authorized to perform this operation")


async def _is_owner_org_unit(
    info: "MOInfo", user_uuid: UUID, entity_uuid: UUID
) -> bool:
    """Check org-unit ownership via the GraphQL org-unit owner filter.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    predicate = organisation_unit_predicate(
        info=info,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[entity_uuid]),
            owner=OwnerFilter(owner=EmployeeFilter(uuids=[user_uuid])),
        ),
    )
    session = info.context.session
    id_column = OrganisationEnhedRegistrering.organisationenhed_id
    return bool(
        await session.scalar(select(exists(select(id_column).where(predicate))))
    )


async def _is_owner_employee(
    info: "MOInfo", user_uuid: UUID, entity_uuid: UUID
) -> bool:
    """Check employee ownership via the GraphQL employee owner filter."""
    predicate = employee_predicate(
        info=info,
        filter=EmployeeFilter(
            uuids=[entity_uuid],
            owner=OwnerFilter(owner=EmployeeFilter(uuids=[user_uuid])),
        ),
    )
    session = info.context.session
    id_column = BrugerRegistrering.bruger_id
    return bool(
        await session.scalar(select(exists(select(id_column).where(predicate))))
    )


async def _is_owner_via_predicate(
    info: "MOInfo",
    user_uuid: UUID,
    entity_type: EntityType,
    entity_uuid: UUID,
) -> bool:
    """Check ownership in-process using the GraphQL filter predicates.

    Used from GraphQL mutators, where a real `info` is available to drive the
    predicate builders, running a lightweight EXISTS query against the
    request-scoped session instead of a nested `execute_graphql` call.
    """
    if entity_type == EntityType.ORG_UNIT:
        return await _is_owner_org_unit(info, user_uuid, entity_uuid)
    return await _is_owner_employee(info, user_uuid, entity_uuid)


async def _is_owner_org_unit_via_graphql(user_uuid: UUID, entity_uuid: UUID) -> bool:
    """Check whether `user_uuid` owns the org unit or one of its ancestors.

    The `descendant` filter grants ownership via the unit itself or any of its
    ancestors, reproducing the ancestor-inheritance semantics that ownership
    checks have always had for org units.
    """
    query = """
    query CheckOrgUnitOwner($filter: OrganisationUnitFilter!) {
      org_units(filter: $filter) {
        objects {
          uuid
        }
      }
    }
    """
    filter_value = {
        "descendant": {"uuids": [entity_uuid]},
        "owner": {"owner": {"uuids": [user_uuid]}},
    }
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder({"filter": filter_value}),
    )
    if r.errors or r.data is None:  # pragma: no cover
        raise AuthorizationError("Error when checking ownership")
    return bool(r.data["org_units"]["objects"])


async def _is_owner_employee_via_graphql(user_uuid: UUID, entity_uuid: UUID) -> bool:
    """Check whether `user_uuid` owns the employee."""
    query = """
    query CheckEmployeeOwner($filter: EmployeeFilter!) {
      employees(filter: $filter) {
        objects {
          uuid
        }
      }
    }
    """
    filter_value = {
        "uuids": [entity_uuid],
        "owner": {"owner": {"uuids": [user_uuid]}},
    }
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder({"filter": filter_value}),
    )
    if r.errors or r.data is None:  # pragma: no cover
        raise AuthorizationError("Error when checking ownership")
    return bool(r.data["employees"]["objects"])


async def _is_owner_via_graphql(
    user_uuid: UUID, entity_type: EntityType, entity_uuid: UUID
) -> bool:
    """Check ownership through `execute_graphql`.

    Works from both the Service-API and GraphQL, as it needs no GraphQL `info`.
    """
    if entity_type == EntityType.ORG_UNIT:
        return await _is_owner_org_unit_via_graphql(user_uuid, entity_uuid)
    return await _is_owner_employee_via_graphql(user_uuid, entity_uuid)


async def _check_owner(
    token: Token,
    entities: set[tuple[EntityType, UUID]],
    is_owner: Callable[[UUID, EntityType, UUID], Awaitable[bool]],
) -> None:
    """Resolve the token's user and require ownership of all entities.

    In some cases several entities have to be checked, e.g. if
    we are moving a unit. In such cases we have to check for
    ownership in both the source (the unit to be moved) and target
    (the receiving unit). In some cases only the
    source is relevant, e.g. if an org unit detail is created/edited.

    `is_owner` performs the per-entity lookup; the Service-API and GraphQL
    supply different implementations.
    """
    logger.debug("Check owner", entities=entities)
    user_uuid = await _get_employee_uuid(token)
    ownership = await asyncio.gather(
        *(
            is_owner(user_uuid, entity_type, entity_uuid)
            for entity_type, entity_uuid in entities
        )
    )
    if ownership and all(ownership):
        return None
    # This function intentionally returns None or raises (instead of returning a
    # boolean) because _get_employee_uuid() might also raise an AuthorizationError,
    # which we would like to propagate to the error message in the Service-API.
    raise AuthorizationError("Not owner")


async def check_owner(
    info: "MOInfo", token: Token, entities: set[tuple[EntityType, UUID]]
) -> None:
    """Check ownership from GraphQL mutators, using the request's `info`.

    Uses the in-process predicate lookup rather than a nested `execute_graphql`
    call, as a real `info` (and its request-scoped session) is available here.
    """
    await _check_owner(token, entities, partial(_is_owner_via_predicate, info))


async def check_owner_serviceapi(
    token: Token, entities: set[tuple[EntityType, UUID]]
) -> None:
    """Check ownership from the Service-API (no GraphQL `info` available)."""
    await _check_owner(token, entities, _is_owner_via_graphql)
