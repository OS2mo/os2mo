# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterable
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

from sqlalchemy import ColumnElement

from mora import common
from mora.auth.keycloak.rbac import _is_owner_employee
from mora.auth.keycloak.rbac import _is_owner_org_unit
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections
from mora.mapping import ASSOCIATED_ORG_UNITS_FIELD
from mora.mapping import PARENT_FIELD
from mora.mapping import USER_FIELD

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo


def _org_unit(
    info: "MOInfo", actor: EmployeeFilter, uuid: UUID | None
) -> ColumnElement | None:
    """Check the ownership of the org unit, if one is named."""
    if uuid is None:
        return None
    return _is_owner_org_unit(info, actor, uuid)


def _employee(
    info: "MOInfo", actor: EmployeeFilter, uuid: UUID | None
) -> ColumnElement | None:
    """Check the ownership of the employee, if one is named."""
    if uuid is None:
        return None
    return _is_owner_employee(info, actor, uuid)


async def get_entities_graphql(
    info: "MOInfo",
    actor: EmployeeFilter,
    raw_input: list[Any],
    collection: Collections,
    permission_type: CollectionPermissionType,
) -> AsyncIterable[ColumnElement]:
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

    async def extract(input) -> AsyncIterable[ColumnElement | None]:
        # Allow both employee and person to avoid bugs in the future
        if collection in {"employee", "person"}:
            yield _employee(info, actor, getattr(input, "uuid"))
            return

        if collection == "org_unit":
            # Create requires ownership of the parent we are trying to insert under
            if permission_type == "create":
                yield _org_unit(info, actor, getattr(input, "parent", None))
                return
            # Otherwise, changes always requires ownership of the org unit itself
            yield _org_unit(info, actor, getattr(input, "uuid"))
            # Additionally, moving an org unit (changing its parent) requires ownership
            # of the new parent. GraphQL edits always contain the full object, so we
            # must compare with the current parent in the database to figure out if it
            # was changed.
            if parent := getattr(input, "parent", None):
                current = await _get_org_unit(getattr(input, "uuid"))
                current_parent = PARENT_FIELD.get_uuid(current)
                if str(parent) != current_parent:
                    yield _org_unit(info, actor, parent)
            return

        if collection == "related_unit":
            # Related units have a single `origin` field and a list of
            # `destination`s. Originally we required ownership of both the
            # origin and destinations, but that's not compatible with the old
            # service-api owner calculation
            yield _org_unit(info, actor, getattr(input, "origin", None))
            return

        # Even though most of the remaining object types (addresses,
        # associations, engagements, IT-users, leaves, managers, owners and
        # role-bindings, at time of writing) can reference both employees and
        # org units, we prefer org units and short-circuit if that is set.
        # Everything (except creates) requires ownership of both the existing
        # database object as well as the new object from the input.
        if permission_type != "create":
            org_function = await _get_org_function(getattr(input, "uuid"))
            if org_unit_str := ASSOCIATED_ORG_UNITS_FIELD.get_uuid(org_function):
                yield _org_unit(info, actor, UUID(org_unit_str))
            elif person_str := USER_FIELD.get_uuid(org_function):
                yield _employee(info, actor, UUID(person_str))

        # Existing object (e.g. update). Again, we prefer org unit over person.
        if org_unit := getattr(input, "org_unit", None):
            yield _org_unit(info, actor, org_unit)
            return
        yield _employee(info, actor, getattr(input, "employee", None))
        yield _employee(info, actor, getattr(input, "person", None))

    for input in raw_input:
        async for check in extract(input=input):
            # Make sure we don't check a None UUID! Doing so makes the later code behave
            # wrongly and may grant too wide access.
            if check is not None:
                yield check


async def _get_org_unit(uuid: UUID) -> dict | None:
    c = common.get_connector()
    return await c.organisationenhed.get(uuid=uuid)


async def _get_org_function(uuid: UUID) -> dict | None:
    c = common.get_connector()
    return await c.organisationfunktion.get(uuid=uuid)
