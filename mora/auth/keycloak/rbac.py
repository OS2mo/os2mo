# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import exists
from sqlalchemy import select
from structlog import get_logger

import mora.config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.db import BrugerRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import ITSystemFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.mapping import ADMIN
from mora.mapping import EntityType

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

logger = get_logger()


def _actor_filter(token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor.

    With `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configured, the
    actor is the employee holding the token's uuid as an external id in that
    IT system; otherwise the employee with the token's uuid itself.
    """
    it_system = (
        mora.config.get_settings().keycloak_rbac_authoritative_it_system_for_owners
    )
    if it_system is not None:
        return EmployeeFilter(
            ituser=ITUserFilter(
                itsystem=ITSystemFilter(uuids=[it_system]),
                external_ids=[str(token.uuid)],
            )
        )
    return EmployeeFilter(uuids=[token.uuid])


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


async def _is_owner_org_unit(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID
) -> bool:
    """Check org-unit ownership via the GraphQL org-unit owner filter.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    predicate = organisation_unit_predicate(
        info=info,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[entity_uuid]),
            owner=OwnerFilter(owner=actor),
        ),
    )
    session = info.context.session
    id_column = OrganisationEnhedRegistrering.organisationenhed_id
    return bool(
        await session.scalar(select(exists(select(id_column).where(predicate))))
    )


async def _is_owner_employee(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID
) -> bool:
    """Check employee ownership via the GraphQL employee owner filter."""
    predicate = employee_predicate(
        info=info,
        filter=EmployeeFilter(
            uuids=[entity_uuid],
            owner=OwnerFilter(owner=actor),
        ),
    )
    session = info.context.session
    id_column = BrugerRegistrering.bruger_id
    return bool(
        await session.scalar(select(exists(select(id_column).where(predicate))))
    )


async def _is_owner(
    info: "MOInfo",
    token: Token,
    entity_type: EntityType,
    entity_uuid: UUID,
) -> bool:
    """Check ownership in-process using the GraphQL filter predicates."""
    actor = _actor_filter(token)
    if entity_type == EntityType.ORG_UNIT:
        return await _is_owner_org_unit(info, actor, entity_uuid)
    return await _is_owner_employee(info, actor, entity_uuid)


async def check_owner(
    info: "MOInfo", token: Token, entities: set[tuple[EntityType, UUID]]
) -> None:
    """Check if the token is owner of the given entities."""
    logger.debug("Check owner", entities=entities)
    ownership = await asyncio.gather(
        *(
            _is_owner(info, token, entity_type, entity_uuid)
            for entity_type, entity_uuid in entities
        )
    )
    if ownership and all(ownership):
        return None
    raise AuthorizationError("Not owner")
