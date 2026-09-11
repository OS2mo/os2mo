# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
from typing import get_type_hints
from uuid import UUID

from more_itertools import first
from more_itertools import one
from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_

from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

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


def first_of(*checks: list[Check]) -> list[Check]:
    """Require only the first of the checks that requires anything."""
    return first(filter(None, checks), [])


def org_unit_or_person(
    org_unit_uuid: UUID | None, person_uuid: UUID | None
) -> list[Check]:
    """Require ownership of the unit if one is named, else of the person."""
    return first_of(org_unit(org_unit_uuid), person(person_uuid))


def _keeps_parent(info: "MOInfo", uuid: UUID, parent: UUID) -> ColumnElement:
    """Whether the parent named is the one the org unit already has."""
    return exists().where(
        organisation_unit_predicate(
            info=info,
            filter=OrganisationUnitFilter(
                uuids=[parent], child=OrganisationUnitFilter(uuids=[uuid])
            ),
        )
    )


def check_parent(uuid: UUID, parent: UUID | None) -> list[Check]:
    """Require ownership of the parent a unit is moved under, if it is moved.

    GraphQL edits always contain the full object, so the parent named is just
    as often the one the unit already has, which is no move at all.
    """
    if parent is None:
        return []

    def check(info: "MOInfo", actor: EmployeeFilter) -> ColumnElement:
        moved_under = one(org_unit(parent))(info, actor)
        return or_(_keeps_parent(info, uuid, parent), moved_under)

    return [check]


def get_entities_graphql(
    info: "MOInfo",
    actor: EmployeeFilter,
    raw_input: list[Any],
    collection: Collections,
    permission_type: CollectionPermissionType,
) -> Iterable[ColumnElement]:
    """Check the ownership of the relevant entities (org unit or employee).

    Args:
        info: The resolver info, carrying the session the checks read.
        actor: The employee filter naming the owner to check against.
        raw_input: The list of `input` objects from the GraphQL mutator. The
            schema-level RBAC extension always normalises this to a list (see
            `mora.graphapi.schema.owner_policy`).
        collection: The object collection (address, employee, org_unit, etc.).
        permission_type: The operation type (create, update, terminate, delete).

    Returns:
        An iterable of checks, all of which must hold, for check_owner().
    """

    def now(checks: list[Check]) -> Iterable[ColumnElement]:
        """The clauses of the checks, run against the request at hand."""
        return (check(info, actor) for check in checks)

    def extract(input) -> Iterable[ColumnElement]:
        # Allow both employee and person to avoid bugs in the future
        if collection in {"employee", "person"}:
            yield from now(person(getattr(input, "uuid")))
            return

        if collection == "org_unit":
            # Create requires ownership of the parent we are trying to insert under
            if permission_type == "create":
                yield from now(org_unit(getattr(input, "parent", None)))
                return
            # Otherwise, changes always requires ownership of the org unit itself,
            # and moving it (changing its parent) that of the new parent as well
            uuid = getattr(input, "uuid")
            yield from now(org_unit(uuid))
            yield from now(check_parent(uuid, getattr(input, "parent", None)))
            return

        if collection == "related_unit":
            # Related units have a single `origin` field and a list of
            # `destination`s. Originally we required ownership of both the
            # origin and destinations, but that's not compatible with the old
            # service-api owner calculation
            yield from now(org_unit(getattr(input, "origin", None)))
            return

        # Even though most of the remaining object types (addresses,
        # associations, engagements, IT-users, leaves, managers, owners and
        # role-bindings, at time of writing) can reference both employees and
        # org units, we prefer org units and short-circuit if that is set.
        # Everything (except creates) requires ownership of both the existing
        # database object as well as the new object from the input.
        if permission_type != "create":
            yield from now(detail(getattr(input, "uuid"), collection))

        yield from now(
            org_unit_or_person(
                getattr(input, "org_unit", None),
                getattr(input, "person", None) or getattr(input, "employee", None),
            )
        )

    for input in raw_input:
        yield from extract(input=input)
