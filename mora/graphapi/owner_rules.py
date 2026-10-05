# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The rules of the owner policy, translated into CEL."""

from collections.abc import Callable
from typing import Any
from typing import TypeAlias
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import false

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.policy_cel import CEL
from mora.graphapi.resolvers import employee_predicate
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


MutatorName: TypeAlias = str

OWNER_RULES: list[tuple[MutatorName, CEL]] = []
