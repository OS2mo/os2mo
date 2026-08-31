# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists
from structlog import get_logger

from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

logger = get_logger()


def _is_owner_org_unit(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID | None
) -> ColumnElement | None:
    """Check org-unit ownership via the GraphQL org-unit owner filter.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors. No org unit named is nothing
    to own, and thus nothing to check.
    """
    if entity_uuid is None:
        return None
    predicate = organisation_unit_predicate(
        info=info,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[entity_uuid]),
            owner=OwnerFilter(owner=actor),
        ),
    )
    return exists().where(predicate)


def _is_owner_employee(
    info: "MOInfo", actor: EmployeeFilter, entity_uuid: UUID | None
) -> ColumnElement | None:
    """Check employee ownership via the GraphQL employee owner filter.

    No employee named is nothing to own, and thus nothing to check.
    """
    if entity_uuid is None:
        return None
    predicate = employee_predicate(
        info=info,
        filter=EmployeeFilter(
            uuids=[entity_uuid],
            owner=OwnerFilter(owner=actor),
        ),
    )
    return exists().where(predicate)
