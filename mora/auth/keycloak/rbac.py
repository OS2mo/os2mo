# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import select
from structlog import get_logger

import mora.config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import ITSystemFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

logger = get_logger()


def _actor_filter(token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor.

    With `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configured, the
    actor is the employee holding the token's uuid as an external id in that
    IT system; otherwise the employee with the token's uuid itself.
    """
    # A token with no uuid never gets this far, see `owner_policy`
    assert token.uuid is not None
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


def _is_owner_org_unit(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID
) -> ColumnElement:
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
    return exists().where(predicate)


def _is_owner_employee(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID
) -> ColumnElement:
    """Check employee ownership via the GraphQL employee owner filter."""
    predicate = employee_predicate(
        info=info,
        filter=EmployeeFilter(
            uuids=[entity_uuid],
            owner=OwnerFilter(owner=actor),
        ),
    )
    return exists().where(predicate)


async def check_owner(info: "MOInfo", checks: list[ColumnElement]) -> None:
    """Check if the token is owner of the given entities."""
    logger.debug("Check owner", checks=checks)
    if checks and await info.context.session.scalar(select(and_(*checks))):
        return None
    raise AuthorizationError("Not owner")
