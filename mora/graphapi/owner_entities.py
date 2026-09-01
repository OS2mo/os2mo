# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from collections.abc import Callable
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
from typing import get_type_hints

from more_itertools import first
from more_itertools import flatten
from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_

from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

# A rule yields the ownership a mutator's `input` requires, one check per
# entity it touches. A check of None names no entity, and thus nothing to own
Checks = Iterable[ColumnElement | None]
OwnerRule = Callable[["MOInfo", EmployeeFilter, Any], Checks]


def org_unit(field: str = "org_unit") -> OwnerRule:
    """The org unit the field names, if it names one.

    Owning any ancestor also grants ownership: the `descendant` filter
    matches the unit together with all of its ancestors.
    """

    def check(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
        entity_uuid = getattr(input, field, None)
        if entity_uuid is None:
            return []
        predicate = organisation_unit_predicate(
            info=info,
            filter=OrganisationUnitFilter(
                descendant=OrganisationUnitFilter(uuids=[entity_uuid]),
                owner=OwnerFilter(owner=actor),
            ),
        )
        return [exists().where(predicate)]

    return check


def person(field: str = "person") -> OwnerRule:
    """The person the field names, if it names one."""

    def check(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
        entity_uuid = getattr(input, field, None)
        if entity_uuid is None:
            return []
        predicate = employee_predicate(
            info=info,
            filter=EmployeeFilter(
                uuids=[entity_uuid],
                owner=OwnerFilter(owner=actor),
            ),
        )
        return [exists().where(predicate)]

    return check


def detail(collection: Collections) -> OwnerRule:
    """The detail itself, whatever it links to now.

    A detail is owned by whoever owns the org unit or the person it links.
    """

    def check(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
        # The detail collections, each the predicate selecting its objects
        predicates: dict[str, Callable[..., ColumnElement]] = {
            "address": resolvers.address_predicate,
            "association": resolvers.association_predicate,
            "engagement": resolvers.engagement_predicate,
            "ituser": resolvers.it_user_predicate,
            "kle": resolvers.kle_predicate,
            "leave": resolvers.leave_predicate,
            "manager": resolvers.manager_predicate,
            "owner": resolvers.owner_predicate,
            "rolebinding": resolvers.rolebinding_predicate,
        }
        predicate = predicates[collection]
        filter = get_type_hints(predicate)["filter"]
        owner = OwnerFilter(owner=actor)
        entity_uuid = getattr(input, "uuid")
        # Whoever owns what the detail links: its org unit (through any ancestor)
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
            return [via_org_unit]
        # ... or its person
        via_person = exists().where(
            predicate(
                info=info,
                filter=filter(
                    uuids=[entity_uuid], employee=EmployeeFilter(owner=owner)
                ),
            )
        )
        return [or_(via_org_unit, via_person)]

    return check


def first_of(*rules: OwnerRule) -> OwnerRule:
    """The first rule naming an entity decides what must be owned."""

    def combined(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
        rule_checks = (
            [check for check in rule(info, actor, input) if check is not None]
            for rule in rules
        )
        return first(filter(None, rule_checks), [])

    return combined


def all_of(*rules: OwnerRule) -> OwnerRule:
    """Every rule's check must hold."""

    def combined(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
        return list(flatten(rule(info, actor, input) for rule in rules))

    return combined


# The unit or the person an input links to, `employee` being the deprecated
# spelling of `person` that the older input types also know
org_unit_or_person = first_of(org_unit(), person())
org_unit_or_person_employee = first_of(org_unit_or_person, person("employee"))


def check_parent(info: "MOInfo", actor: EmployeeFilter, input: Any) -> Checks:
    """The parent the unit is moved under, if the input names a new one.

    GraphQL edits always contain the full object, so the parent named is just
    as often the one the unit already has, which is no move at all.
    """
    uuid = getattr(input, "uuid")
    parent = getattr(input, "parent", None)
    if parent is None:
        return []
    # Whether the parent named is the one the unit already has
    keeps_parent = exists().where(
        organisation_unit_predicate(
            info=info,
            filter=OrganisationUnitFilter(
                uuids=[parent], child=OrganisationUnitFilter(uuids=[uuid])
            ),
        )
    )
    moved_under = exists().where(
        organisation_unit_predicate(
            info=info,
            filter=OrganisationUnitFilter(
                descendant=OrganisationUnitFilter(uuids=[parent]),
                owner=OwnerFilter(owner=actor),
            ),
        )
    )
    return [or_(keeps_parent, moved_under)]


# What a mutator requires owned. A mutator not listed here is never granted by
# ownership. Plural mutators run their rule on every input object, and all of
# the resulting checks must hold.
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "address_create": org_unit_or_person_employee,
    "address_terminate": detail("address"),
    "address_update": all_of(detail("address"), org_unit_or_person_employee),
    "addresses_create": org_unit_or_person_employee,
    # The unit of the association
    "association_create": org_unit_or_person_employee,
    "association_terminate": detail("association"),
    "association_update": all_of(detail("association"), org_unit_or_person_employee),
    # The employee itself
    "employee_create": person("uuid"),
    "employee_terminate": person("uuid"),
    "employee_update": person("uuid"),
    # The unit of the engagement
    "engagement_create": org_unit_or_person_employee,
    "engagement_terminate": detail("engagement"),
    "engagement_update": all_of(detail("engagement"), org_unit_or_person_employee),
    "engagements_create": org_unit_or_person_employee,
    "engagements_update": all_of(detail("engagement"), org_unit_or_person_employee),
    # The unit of the IT-association
    "itassociation_create": org_unit_or_person,
    "itassociation_terminate": detail("association"),
    "itassociation_update": all_of(detail("association"), org_unit_or_person),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": org_unit_or_person,
    "ituser_terminate": detail("ituser"),
    "ituser_update": all_of(detail("ituser"), org_unit_or_person),
    "itusers_create": org_unit_or_person,
    # The annotated unit
    "kle_create": org_unit(),
    "kle_terminate": detail("kle"),
    "kle_update": all_of(detail("kle"), org_unit()),
    # The person on leave
    "leave_create": person(),
    "leave_terminate": detail("leave"),
    "leave_update": all_of(detail("leave"), person()),
    # The unit of the manager
    "manager_create": org_unit_or_person,
    "manager_terminate": detail("manager"),
    "manager_update": all_of(detail("manager"), org_unit_or_person),
    "managers_create": org_unit_or_person,
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": org_unit("parent"),
    "org_unit_terminate": all_of(org_unit("uuid"), check_parent),
    "org_unit_update": all_of(org_unit("uuid"), check_parent),
    # The unit or the person owned (exactly one is set)
    "owner_create": org_unit_or_person,
    "owner_terminate": detail("owner"),
    "owner_update": all_of(detail("owner"), org_unit_or_person),
    # The origin of the relation
    "related_units_update": org_unit("origin"),
    # The unit of the role-binding, if one is named
    "rolebinding_create": org_unit(),
    "rolebinding_terminate": detail("rolebinding"),
    "rolebinding_update": all_of(detail("rolebinding"), org_unit()),
    "rolebindings_create": org_unit(),
}
