# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from collections.abc import Callable
from functools import partial
from typing import Any
from typing import get_type_hints
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from strawberry import UNSET

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.graphapi.version import Version

OwnerRule = Callable[[Settings, Version, Token, dict[str, Any]], ColumnElement | None]


def _actor_filter(token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor, by the token's uuid."""
    # A token with no uuid never gets this far, see `owner_policy`
    assert token.uuid is not None
    return EmployeeFilter(uuids=[token.uuid])


def org_unit(
    settings: Settings, version: Version, token: Token, uuid: UUID | None
) -> ColumnElement | None:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    if uuid is None or uuid is UNSET:
        return None
    predicate = organisation_unit_predicate(
        settings=settings,
        version=version,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[uuid]),
            owner=OwnerFilter(owner=_actor_filter(token)),
        ),
    )
    return exists().where(predicate)


def person(
    settings: Settings, version: Version, token: Token, uuid: UUID | None
) -> ColumnElement | None:
    """Require ownership of the person named, if one is named."""
    if uuid is None or uuid is UNSET:
        return None
    predicate = employee_predicate(
        settings=settings,
        version=version,
        filter=EmployeeFilter(
            uuids=[uuid],
            owner=OwnerFilter(owner=_actor_filter(token)),
        ),
    )
    return exists().where(predicate)


def detail_org_unit(
    settings: Settings,
    version: Version,
    token: Token,
    uuid: UUID,
    *,
    predicate: Callable[..., ColumnElement],
) -> ColumnElement:
    """Require ownership of the org unit the detail links, through any ancestor."""
    filter = get_type_hints(predicate)["filter"]
    return exists().where(
        predicate(
            settings=settings,
            version=version,
            filter=filter(
                uuids=[uuid],
                org_unit=OrganisationUnitFilter(
                    ancestor=OrganisationUnitFilter(
                        owner=OwnerFilter(owner=_actor_filter(token))
                    )
                ),
            ),
        )
    )


def detail_person(
    settings: Settings,
    version: Version,
    token: Token,
    uuid: UUID,
    *,
    predicate: Callable[..., ColumnElement],
) -> ColumnElement:
    """Require ownership of the person the detail links."""
    filter = get_type_hints(predicate)["filter"]
    return exists().where(
        predicate(
            settings=settings,
            version=version,
            filter=filter(
                uuids=[uuid],
                employee=EmployeeFilter(owner=OwnerFilter(owner=_actor_filter(token))),
            ),
        )
    )


def detail(
    settings: Settings,
    version: Version,
    token: Token,
    uuid: UUID,
    *,
    predicate: Callable[..., ColumnElement],
) -> ColumnElement:
    """Require ownership of the org unit or the person the detail links."""
    return or_(
        detail_org_unit(settings, version, token, uuid, predicate=predicate),
        detail_person(settings, version, token, uuid, predicate=predicate),
    )


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
    if parent is None or parent is UNSET:
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


# The rule for each collection's detail. A KLE and a role-binding link no
# person, so owning the unit they link is the only way to own them
association = partial(detail, predicate=resolvers.association_predicate)
engagement = partial(detail, predicate=resolvers.engagement_predicate)
ituser = partial(detail, predicate=resolvers.it_user_predicate)
kle = partial(detail_org_unit, predicate=resolvers.kle_predicate)
leave = partial(detail, predicate=resolvers.leave_predicate)
manager = partial(detail, predicate=resolvers.manager_predicate)
owner = partial(detail, predicate=resolvers.owner_predicate)
rolebinding = partial(detail_org_unit, predicate=resolvers.rolebinding_predicate)


# What a mutator requires owned, read off its arguments. A mutator listed
# neither here nor in `OWNER_RULES` is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit of the engagement
    "engagements_update": lambda settings, version, token, arguments: and_or_none(
        *(
            and_or_none(
                engagement(settings, version, token, input.uuid),
                org_unit_or_person(
                    settings,
                    version,
                    token,
                    input.org_unit,
                    input.person or input.employee,
                ),
            )
            for input in arguments["input"]
        )
    ),
    # The unit of the IT-association, whose update cannot name a person
    "itassociation_create": lambda settings,
    version,
    token,
    arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "itassociation_terminate": lambda settings, version, token, arguments: association(
        settings, version, token, arguments["input"].uuid
    ),
    "itassociation_update": lambda settings, version, token, arguments: and_or_none(
        association(settings, version, token, arguments["input"].uuid),
        org_unit(settings, version, token, arguments["input"].org_unit),
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "ituser_terminate": lambda settings, version, token, arguments: ituser(
        settings, version, token, arguments["input"].uuid
    ),
    "ituser_update": lambda settings, version, token, arguments: and_or_none(
        ituser(settings, version, token, arguments["input"].uuid),
        org_unit_or_person(
            settings,
            version,
            token,
            arguments["input"].org_unit,
            arguments["input"].person,
        ),
    ),
    "itusers_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(settings, version, token, input.org_unit, input.person)
            for input in arguments["input"]
        )
    ),
    # The annotated unit
    "kle_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].org_unit
    ),
    "kle_terminate": lambda settings, version, token, arguments: kle(
        settings, version, token, arguments["input"].uuid
    ),
    "kle_update": lambda settings, version, token, arguments: and_or_none(
        kle(settings, version, token, arguments["input"].uuid),
        org_unit(settings, version, token, arguments["input"].org_unit),
    ),
    # The person on leave
    "leave_create": lambda settings, version, token, arguments: person(
        settings, version, token, arguments["input"].person
    ),
    "leave_terminate": lambda settings, version, token, arguments: leave(
        settings, version, token, arguments["input"].uuid
    ),
    "leave_update": lambda settings, version, token, arguments: and_or_none(
        leave(settings, version, token, arguments["input"].uuid),
        person(settings, version, token, arguments["input"].person),
    ),
    # The unit of the manager
    "manager_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "manager_terminate": lambda settings, version, token, arguments: manager(
        settings, version, token, arguments["input"].uuid
    ),
    "manager_update": lambda settings, version, token, arguments: and_or_none(
        manager(settings, version, token, arguments["input"].uuid),
        org_unit_or_person(
            settings,
            version,
            token,
            arguments["input"].org_unit,
            arguments["input"].person,
        ),
    ),
    "managers_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(settings, version, token, input.org_unit, input.person)
            for input in arguments["input"]
        )
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].parent
    ),
    "org_unit_terminate": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].uuid
    ),
    "org_unit_update": lambda settings, version, token, arguments: and_or_none(
        org_unit(settings, version, token, arguments["input"].uuid),
        check_parent(
            settings, version, token, arguments["input"].uuid, arguments["input"].parent
        ),
    ),
    # The unit or the person owned (exactly one is set)
    "owner_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "owner_terminate": lambda settings, version, token, arguments: owner(
        settings, version, token, arguments["input"].uuid
    ),
    "owner_update": lambda settings, version, token, arguments: and_or_none(
        owner(settings, version, token, arguments["input"].uuid),
        org_unit_or_person(
            settings,
            version,
            token,
            arguments["input"].org_unit,
            arguments["input"].person,
        ),
    ),
    # Related units have a single `origin` field and a list of
    # `destination`s. Originally we required ownership of both the
    # origin and destinations, but that's not compatible with the old
    # service-api owner calculation
    "related_units_update": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].origin
    ),
    # The unit of the role-binding, if one is named
    "rolebinding_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].org_unit
    ),
    "rolebinding_terminate": lambda settings, version, token, arguments: rolebinding(
        settings, version, token, arguments["input"].uuid
    ),
    "rolebinding_update": lambda settings, version, token, arguments: and_or_none(
        rolebinding(settings, version, token, arguments["input"].uuid),
        org_unit(settings, version, token, arguments["input"].org_unit),
    ),
    "rolebindings_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit(settings, version, token, input.org_unit)
            for input in arguments["input"]
        )
    ),
}
