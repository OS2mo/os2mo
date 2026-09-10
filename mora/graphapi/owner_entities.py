# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import get_type_hints
from uuid import UUID

from more_itertools import first
from more_itertools import flatten
from more_itertools import one
from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_
from strawberry import UNSET

from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

# A check builds the clause the actor must satisfy to own an entity
Check = Callable[["MOInfo", EmployeeFilter], ColumnElement]
OwnerRule = Callable[[Any], list[Check]]


def org_unit(uuid: UUID | None) -> list[Check]:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    if uuid is None or uuid is UNSET:
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
    if uuid is None or uuid is UNSET:
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


def first_of(*checks: list[Check]) -> list[Check]:
    """Require only the first of the checks that requires anything."""
    return first(filter(None, checks), [])


def all_of(*checks: list[Check]) -> list[Check]:
    """Require all of the checks."""
    return list(flatten(checks))


def each(rule: OwnerRule) -> OwnerRule:
    """Turn a rule for one input into the rule for a list of them.

    The plural mutators, `addresses_create` and the like, take a list of
    inputs, and the actor must own whatever every one of them requires.
    """
    return lambda inputs: all_of(*map(rule, inputs))


def org_unit_or_person(
    org_unit_uuid: UUID | None, person_uuid: UUID | None
) -> list[Check]:
    """Require ownership of the unit if one is named, else of the person."""
    return first_of(org_unit(org_unit_uuid), person(person_uuid))


def check_parent(uuid: UUID, parent: UUID | None) -> list[Check]:
    """Require ownership of the parent a unit is moved under, if it is moved.

    GraphQL edits always contain the full object, so the parent named is just
    as often the one the unit already has, which is no move at all.
    """
    if parent is None or parent is UNSET:
        return []

    def check(info: "MOInfo", actor: EmployeeFilter) -> ColumnElement:
        # Whether the parent named is the one the unit already has
        keeps_parent = exists().where(
            organisation_unit_predicate(
                info=info,
                filter=OrganisationUnitFilter(
                    uuids=[parent], child=OrganisationUnitFilter(uuids=[uuid])
                ),
            )
        )
        # ... or the actor owns the parent it is moved under
        moved_under = one(org_unit(parent))(info, actor)
        return or_(keeps_parent, moved_under)

    return [check]


# The rule for each collection's detail
address = partial(detail, collection="address")
association = partial(detail, collection="association")
engagement = partial(detail, collection="engagement")
ituser = partial(detail, collection="ituser")
kle = partial(detail, collection="kle")
leave = partial(detail, collection="leave")
manager = partial(detail, collection="manager")
owner = partial(detail, collection="owner")
rolebinding = partial(detail, collection="rolebinding")


# What a mutator requires owned, read off its `input`.
# A mutator not listed here is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "address_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "address_terminate": lambda input: address(input.uuid),
    "address_update": lambda input: all_of(
        address(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    "addresses_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    # The unit of the association
    "association_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "association_terminate": lambda input: association(input.uuid),
    "association_update": lambda input: all_of(
        association(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    # The employee itself
    "employee_create": lambda input: person(input.uuid),
    "employee_terminate": lambda input: person(input.uuid),
    "employee_update": lambda input: person(input.uuid),
    # The unit of the engagement
    "engagement_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "engagement_terminate": lambda input: engagement(input.uuid),
    "engagement_update": lambda input: all_of(
        engagement(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    "engagements_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    "engagements_update": each(
        lambda input: all_of(
            engagement(input.uuid),
            org_unit_or_person(input.org_unit, input.person or input.employee),
        )
    ),
    # The unit of the IT-association, whose update cannot name a person
    "itassociation_create": lambda input: org_unit_or_person(
        input.org_unit, input.person
    ),
    "itassociation_terminate": lambda input: association(input.uuid),
    "itassociation_update": lambda input: all_of(
        association(input.uuid), org_unit(input.org_unit)
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "ituser_terminate": lambda input: ituser(input.uuid),
    "ituser_update": lambda input: all_of(
        ituser(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
    "itusers_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person)
    ),
    # The annotated unit
    "kle_create": lambda input: org_unit(input.org_unit),
    "kle_terminate": lambda input: kle(input.uuid),
    "kle_update": lambda input: all_of(kle(input.uuid), org_unit(input.org_unit)),
    # The person on leave
    "leave_create": lambda input: person(input.person),
    "leave_terminate": lambda input: leave(input.uuid),
    "leave_update": lambda input: all_of(leave(input.uuid), person(input.person)),
    # The unit of the manager
    "manager_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "manager_terminate": lambda input: manager(input.uuid),
    "manager_update": lambda input: all_of(
        manager(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
    "managers_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person)
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": lambda input: org_unit(input.parent),
    "org_unit_terminate": lambda input: org_unit(input.uuid),
    "org_unit_update": lambda input: all_of(
        org_unit(input.uuid), check_parent(input.uuid, input.parent)
    ),
    # The unit or the person owned (exactly one is set)
    "owner_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "owner_terminate": lambda input: owner(input.uuid),
    "owner_update": lambda input: all_of(
        owner(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
    # The origin of the relation
    "related_units_update": lambda input: org_unit(input.origin),
    # The unit of the role-binding, if one is named
    "rolebinding_create": lambda input: org_unit(input.org_unit),
    "rolebinding_terminate": lambda input: rolebinding(input.uuid),
    "rolebinding_update": lambda input: all_of(
        rolebinding(input.uuid), org_unit(input.org_unit)
    ),
    "rolebindings_create": each(lambda input: org_unit(input.org_unit)),
}
