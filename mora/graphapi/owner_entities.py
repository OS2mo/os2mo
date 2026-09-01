# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from typing import TYPE_CHECKING
from typing import Any

from more_itertools import first
from more_itertools import flatten
from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_

from mora.graphapi import resolvers
from mora.graphapi.filters import AddressFilter
from mora.graphapi.filters import AssociationFilter
from mora.graphapi.filters import BaseFilter
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import EngagementFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.filters import KLEFilter
from mora.graphapi.filters import LeaveFilter
from mora.graphapi.filters import ManagerFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.filters import RoleBindingFilter
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


def detail(
    info: "MOInfo",
    actor: EmployeeFilter,
    input: Any,
    *,
    resolver: Callable[..., ColumnElement],
    filter_class: Callable[..., BaseFilter],
    person: bool = True,
) -> Checks:
    """The detail itself, whatever it links to now.

    A detail is owned by whoever owns what it links: its org unit, through
    any ancestor, or its person. Every detail links an org unit; the few
    that cannot also name a person say so in the partials below, pinned
    against the filters by a test.
    """
    owner = OwnerFilter(owner=actor)
    uuid = getattr(input, "uuid")
    # Whoever owns what the detail links: its org unit (through any ancestor)
    via_org_unit = exists().where(
        resolver(
            info=info,
            filter=filter_class(
                uuids=[uuid],
                org_unit=OrganisationUnitFilter(
                    ancestor=OrganisationUnitFilter(owner=owner)
                ),
            ),
        )
    )
    if not person:
        return [via_org_unit]
    # ... or its person
    via_person = exists().where(
        resolver(
            info=info,
            filter=filter_class(uuids=[uuid], employee=EmployeeFilter(owner=owner)),
        )
    )
    return [or_(via_org_unit, via_person)]


# The rule for each collection's detail. KLEs and role-bindings cannot name
# a person; every other detail can
address: OwnerRule = partial(
    detail, resolver=resolvers.address_predicate, filter_class=AddressFilter
)
association: OwnerRule = partial(
    detail, resolver=resolvers.association_predicate, filter_class=AssociationFilter
)
engagement: OwnerRule = partial(
    detail, resolver=resolvers.engagement_predicate, filter_class=EngagementFilter
)
ituser: OwnerRule = partial(
    detail, resolver=resolvers.it_user_predicate, filter_class=ITUserFilter
)
kle: OwnerRule = partial(
    detail,
    resolver=resolvers.kle_predicate,
    filter_class=KLEFilter,
    person=False,
)
leave: OwnerRule = partial(
    detail, resolver=resolvers.leave_predicate, filter_class=LeaveFilter
)
manager: OwnerRule = partial(
    detail, resolver=resolvers.manager_predicate, filter_class=ManagerFilter
)
owner: OwnerRule = partial(
    detail, resolver=resolvers.owner_predicate, filter_class=OwnerFilter
)
rolebinding: OwnerRule = partial(
    detail,
    resolver=resolvers.rolebinding_predicate,
    filter_class=RoleBindingFilter,
    person=False,
)


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
    "address_terminate": address,
    "address_update": all_of(address, org_unit_or_person_employee),
    "addresses_create": org_unit_or_person_employee,
    # The unit of the association
    "association_create": org_unit_or_person_employee,
    "association_terminate": association,
    "association_update": all_of(association, org_unit_or_person_employee),
    # The employee itself
    "employee_create": person("uuid"),
    "employee_terminate": person("uuid"),
    "employee_update": person("uuid"),
    # The unit of the engagement
    "engagement_create": org_unit_or_person_employee,
    "engagement_terminate": engagement,
    "engagement_update": all_of(engagement, org_unit_or_person_employee),
    "engagements_create": org_unit_or_person_employee,
    "engagements_update": all_of(engagement, org_unit_or_person_employee),
    # The unit of the IT-association
    "itassociation_create": org_unit_or_person,
    "itassociation_terminate": association,
    "itassociation_update": all_of(association, org_unit_or_person),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": org_unit_or_person,
    "ituser_terminate": ituser,
    "ituser_update": all_of(ituser, org_unit_or_person),
    "itusers_create": org_unit_or_person,
    # The annotated unit
    "kle_create": org_unit(),
    "kle_terminate": kle,
    "kle_update": all_of(kle, org_unit()),
    # The person on leave
    "leave_create": person(),
    "leave_terminate": leave,
    "leave_update": all_of(leave, person()),
    # The unit of the manager
    "manager_create": org_unit_or_person,
    "manager_terminate": manager,
    "manager_update": all_of(manager, org_unit_or_person),
    "managers_create": org_unit_or_person,
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": org_unit("parent"),
    "org_unit_terminate": all_of(org_unit("uuid"), check_parent),
    "org_unit_update": all_of(org_unit("uuid"), check_parent),
    # The unit or the person owned (exactly one is set)
    "owner_create": org_unit_or_person,
    "owner_terminate": owner,
    "owner_update": all_of(owner, org_unit_or_person),
    # The origin of the relation
    "related_units_update": org_unit("origin"),
    # The unit of the role-binding, if one is named
    "rolebinding_create": org_unit(),
    "rolebinding_terminate": rolebinding,
    "rolebinding_update": all_of(rolebinding, org_unit()),
    "rolebindings_create": org_unit(),
}
