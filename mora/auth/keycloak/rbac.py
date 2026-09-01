# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import TYPE_CHECKING
from typing import get_type_hints
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_
from structlog import get_logger

from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import Collections
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


def _is_owner_detail(
    info: "MOInfo", actor: EmployeeFilter, collection: Collections, entity_uuid: UUID
) -> ColumnElement:
    """Check detail ownership via the GraphQL filter of its own collection."""
    # The detail collections, each the predicate selecting its objects
    predicate = {
        "address": resolvers.address_predicate,
        "association": resolvers.association_predicate,
        "engagement": resolvers.engagement_predicate,
        "ituser": resolvers.it_user_predicate,
        "kle": resolvers.kle_predicate,
        "leave": resolvers.leave_predicate,
        "manager": resolvers.manager_predicate,
        "owner": resolvers.owner_predicate,
        "rolebinding": resolvers.rolebinding_predicate,
    }[collection]
    filter = get_type_hints(predicate)["filter"]
    owner = OwnerFilter(owner=actor)
    # A detail is owned by whoever owns the org unit or the person it links.
    # Every collection can name an org unit, only some can name a person
    via_org_unit = exists().where(
        predicate(
            info=info,
            filter=filter(
                uuids=[entity_uuid],
                org_unit=OrganisationUnitFilter(
                    ancestor=OrganisationUnitFilter(owner=owner)
                ),
            ),
        )
    )
    if "employee" not in get_type_hints(filter):
        return via_org_unit
    via_person = exists().where(
        predicate(
            info=info,
            filter=filter(uuids=[entity_uuid], employee=EmployeeFilter(owner=owner)),
        )
    )
    return or_(via_org_unit, via_person)
