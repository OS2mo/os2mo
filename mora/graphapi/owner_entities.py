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
from sqlalchemy import false
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


def _owner_filter(token: Token) -> OwnerFilter:
    """The owner filter matching the calling actor, by the token's uuid."""
    # A token with no uuid never gets this far, see `deny_tokens_without_uuid`
    assert token.uuid is not None
    return OwnerFilter(owner=EmployeeFilter(uuids=[token.uuid]))


def deny_tokens_without_uuid(rule: OwnerRule) -> OwnerRule:
    """Deny tokens carrying no uuid, before `rule` is evaluated."""

    def check(
        settings: Settings, version: Version, token: Token, arguments: dict[str, Any]
    ) -> ColumnElement | None:
        # A token carrying no uuid names no employee, so it owns nothing
        if token.uuid is None:
            return false()
        return rule(settings, version, token, arguments)

    return check


def deny_requiring_nothing(
    rule: OwnerRule,
) -> Callable[[Settings, Version, Token, dict[str, Any]], ColumnElement]:
    """Deny where `rule` requires nothing."""

    def check(
        settings: Settings, version: Version, token: Token, arguments: dict[str, Any]
    ) -> ColumnElement:
        required = rule(settings, version, token, arguments)
        # Nothing to own is not owned by anybody
        if required is None:
            return false()
        return required

    return check


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
            owner=_owner_filter(token),
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
            owner=_owner_filter(token),
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
                    ancestor=OrganisationUnitFilter(owner=_owner_filter(token))
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
                employee=EmployeeFilter(owner=_owner_filter(token)),
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


# The rule for each collection's detail
engagement = partial(detail, predicate=resolvers.engagement_predicate)
manager = partial(detail, predicate=resolvers.manager_predicate)
owner = partial(detail, predicate=resolvers.owner_predicate)


# What a mutator requires owned, read off its arguments.
# A mutator not listed here or in `OWNER_RULES` is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "addresses_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(
                settings, version, token, input.org_unit, input.person or input.employee
            )
            for input in arguments["input"]
        )
    ),
    # The unit of the engagement
    "engagements_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(
                settings, version, token, input.org_unit, input.person or input.employee
            )
            for input in arguments["input"]
        )
    ),
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
    # The unit or the person the IT-user belongs to (exactly one is set)
    "itusers_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(settings, version, token, input.org_unit, input.person)
            for input in arguments["input"]
        )
    ),
    # The unit of the manager
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
    "org_unit_update": lambda settings, version, token, arguments: and_or_none(
        org_unit(settings, version, token, arguments["input"].uuid),
        check_parent(
            settings, version, token, arguments["input"].uuid, arguments["input"].parent
        ),
    ),
    # The unit or the person owned (exactly one is set)
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
    # The unit of the role-binding, if one is named
    "rolebindings_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit(settings, version, token, input.org_unit)
            for input in arguments["input"]
        )
    ),
}
