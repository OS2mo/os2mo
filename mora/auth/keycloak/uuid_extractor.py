# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import get_type_hints
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import ITSystemFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.graphapi.version import Version


def _actor_filter(settings: Settings, token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor.

    With `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configured, the
    actor is the employee holding the token's uuid as an external id in that
    IT system; otherwise the employee with the token's uuid itself.
    """
    # A token with no uuid never gets this far, see `owner_policy`
    assert token.uuid is not None
    it_system = settings.keycloak_rbac_authoritative_it_system_for_owners
    if it_system is not None:
        return EmployeeFilter(
            ituser=ITUserFilter(
                itsystem=ITSystemFilter(uuids=[it_system]),
                external_ids=[str(token.uuid)],
            )
        )
    return EmployeeFilter(uuids=[token.uuid])


def org_unit(
    settings: Settings, version: Version, token: Token, uuid: UUID | None
) -> ColumnElement | None:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    if uuid is None:
        return None
    predicate = organisation_unit_predicate(
        settings=settings,
        version=version,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[uuid]),
            owner=OwnerFilter(owner=_actor_filter(settings, token)),
        ),
    )
    return exists().where(predicate)


def person(
    settings: Settings, version: Version, token: Token, uuid: UUID | None
) -> ColumnElement | None:
    """Require ownership of the person named, if one is named."""
    if uuid is None:
        return None
    predicate = employee_predicate(
        settings=settings,
        version=version,
        filter=EmployeeFilter(
            uuids=[uuid],
            owner=OwnerFilter(owner=_actor_filter(settings, token)),
        ),
    )
    return exists().where(predicate)


def detail(
    settings: Settings,
    version: Version,
    token: Token,
    collection: Collections,
    uuid: UUID,
) -> ColumnElement:
    """Require ownership of the detail itself, whatever it links to now.

    A detail is owned by whoever owns the org unit or the person it links.
    """
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
    owner = OwnerFilter(owner=_actor_filter(settings, token))
    # Whoever owns what the detail links: its org unit (through any ancestor)
    via_org_unit = exists().where(
        predicate(
            settings=settings,
            version=version,
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
            settings=settings,
            version=version,
            filter=filter(uuids=[uuid], employee=EmployeeFilter(owner=owner)),
        )
    )
    return or_(via_org_unit, via_person)


def and_or_none(*checks: ColumnElement | None) -> ColumnElement | None:
    """Require all of the checks, or nothing if there is nothing to check."""
    clauses = [check for check in checks if check is not None]
    if not clauses:
        return None
    return and_(*clauses)


def org_unit_or_person(
    settings: Settings,
    version: Version,
    token: Token,
    org_unit_uuid: UUID | None,
    person_uuid: UUID | None,
) -> ColumnElement | None:
    """Require ownership of the unit if one is named, else of the person."""
    if (unit := org_unit(settings, version, token, org_unit_uuid)) is not None:
        return unit
    return person(settings, version, token, person_uuid)


def check_parent(
    settings: Settings, version: Version, token: Token, uuid: UUID, parent: UUID | None
) -> ColumnElement | None:
    """Require ownership of the parent a unit is moved under, if it is moved.

    GraphQL edits always contain the full object, so the parent named is just
    as often the one the unit already has, which is no move at all.
    """
    if parent is None:
        return None
    # Whether the parent named is the one the unit already has
    keeps_parent = exists().where(
        organisation_unit_predicate(
            settings=settings,
            version=version,
            filter=OrganisationUnitFilter(
                uuids=[parent], child=OrganisationUnitFilter(uuids=[uuid])
            ),
        )
    )
    # ... or the actor owns the parent it is moved under
    moved_under = org_unit(settings, version, token, parent)
    assert moved_under is not None
    return or_(keeps_parent, moved_under)


def get_entities_graphql(
    settings: Settings,
    version: Version,
    token: Token,
    raw_input: list[Any],
    collection: Collections,
    permission_type: CollectionPermissionType,
) -> ColumnElement | None:
    """The ownership checks of the relevant entities (org unit or employee).

    Args:
        settings: The settings the predicates take.
        version: The GraphQL schema version the predicates take.
        token: The token of the calling actor.
        raw_input: The list of `input` objects from the GraphQL mutator. The
            schema-level RBAC extension always normalises this to a list (see
            `mora.graphapi.schema.owner_policy`).
        collection: The object collection (address, employee, org_unit, etc.).
        permission_type: The operation type (create, update, terminate, delete).

    Returns:
        The check for `owner_policy` to evaluate, or None with nothing to check.
    """

    def rule(input: Any) -> ColumnElement | None:
        # Allow both employee and person to avoid bugs in the future
        if collection in {"employee", "person"}:
            return person(settings, version, token, getattr(input, "uuid"))

        if collection == "org_unit":
            # Create requires ownership of the parent we are trying to insert under
            if permission_type == "create":
                return org_unit(
                    settings, version, token, getattr(input, "parent", None)
                )
            # Otherwise, changes always requires ownership of the org unit itself,
            # and moving it (changing its parent) that of the new parent as well
            uuid = getattr(input, "uuid")
            return and_or_none(
                org_unit(settings, version, token, uuid),
                check_parent(
                    settings, version, token, uuid, getattr(input, "parent", None)
                ),
            )

        if collection == "related_unit":
            # Related units have a single `origin` field and a list of
            # `destination`s. Originally we required ownership of both the
            # origin and destinations, but that's not compatible with the old
            # service-api owner calculation
            return org_unit(settings, version, token, getattr(input, "origin", None))

        # Even though most of the remaining object types (addresses,
        # associations, engagements, IT-users, leaves, managers, owners and
        # role-bindings, at time of writing) can reference both employees and
        # org units, we prefer org units and short-circuit if that is set.
        # Everything (except creates) requires ownership of both the existing
        # database object as well as the new object from the input.
        linked = org_unit_or_person(
            settings,
            version,
            token,
            getattr(input, "org_unit", None),
            getattr(input, "person", None) or getattr(input, "employee", None),
        )
        if permission_type == "create":
            return linked
        return and_or_none(
            detail(settings, version, token, collection, getattr(input, "uuid")), linked
        )

    return and_or_none(*(rule(input) for input in raw_input))
