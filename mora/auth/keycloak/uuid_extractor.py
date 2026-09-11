# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

from more_itertools import one
from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_

from mora.auth.keycloak.rbac import Check
from mora.auth.keycloak.rbac import _is_owner_detail
from mora.auth.keycloak.rbac import org_unit
from mora.auth.keycloak.rbac import person
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import organisation_unit_predicate

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo


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
            # Otherwise, changes always requires ownership of the org unit itself
            yield from now(org_unit(getattr(input, "uuid")))
            # Additionally, moving an org unit (changing its parent) requires ownership
            # of the new parent. GraphQL edits always contain the full object, so the
            # parent named is just as often the one the unit already has, which is no
            # move at all.
            if parent := getattr(input, "parent", None):
                yield or_(
                    _keeps_parent(info, getattr(input, "uuid"), parent),
                    one(now(org_unit(parent))),
                )
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
            yield from now(_is_owner_detail(collection, getattr(input, "uuid")))

        # Existing object (e.g. update). Again, we prefer org unit over person.
        if org_unit_uuid := getattr(input, "org_unit", None):
            yield from now(org_unit(org_unit_uuid))
            return
        yield from now(person(getattr(input, "employee", None)))
        yield from now(person(getattr(input, "person", None)))

    for input in raw_input:
        yield from extract(input=input)
