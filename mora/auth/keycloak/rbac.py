# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
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

# A check builds the clause the actor must satisfy to own an entity
Check = Callable[["MOInfo", EmployeeFilter], ColumnElement]


def org_unit(uuid: UUID | None) -> list[Check]:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    if uuid is None:
        return []

    def check(info: "MOInfo", actor: EmployeeFilter) -> ColumnElement:
        predicate = organisation_unit_predicate(
            info=info,
            filter=OrganisationUnitFilter(
                descendant=OrganisationUnitFilter(uuids=[uuid]),
                owner=OwnerFilter(owner=actor),
            ),
        )
        return exists().where(predicate)

    return [check]


def person(uuid: UUID | None) -> list[Check]:
    """Require ownership of the person named, if one is named."""
    if uuid is None:
        return []

    def check(info: "MOInfo", actor: EmployeeFilter) -> ColumnElement:
        predicate = employee_predicate(
            info=info,
            filter=EmployeeFilter(
                uuids=[uuid],
                owner=OwnerFilter(owner=actor),
            ),
        )
        return exists().where(predicate)

    return [check]


def detail(uuid: UUID, collection: Collections) -> list[Check]:
    """Require ownership of the detail itself, whatever it links to now.

    A detail is owned by whoever owns the org unit or the person it links.
    """

    def check(info: "MOInfo", actor: EmployeeFilter) -> ColumnElement:
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
        # Whoever owns what the detail links: its org unit (through any ancestor)
        via_org_unit = exists().where(
            predicate(
                info=info,
                filter=filter(
                    uuids=[uuid],
                    org_unit=OrganisationUnitFilter(
                        ancestor=OrganisationUnitFilter(owner=owner)
                    ),
                ),
            )
        )
        if "employee" not in get_type_hints(filter):
            return via_org_unit
        # ... or its person
        via_person = exists().where(
            predicate(
                info=info,
                filter=filter(uuids=[uuid], employee=EmployeeFilter(owner=owner)),
            )
        )
        return or_(via_org_unit, via_person)

    return [check]
