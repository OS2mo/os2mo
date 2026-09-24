# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The rules of the owner policy, translated into CEL."""

from string import Template
from typing import TypeAlias
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists
from strawberry import UNSET

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.policy_cel import CEL
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.graphapi.version import Version


def _owner_filter(requirements: str) -> str:
    """Bind the owner filter matching the calling actor, by the token's uuid."""
    # A token with no uuid never gets this far, see `deny_tokens_without_uuid`
    return Template(
        'cel.bind(owner_filter, {"owner": {"uuids": [token.uuid]}}, $requirements)'
    ).substitute(requirements=requirements)


def deny_tokens_without_uuid(rule: str) -> str:
    """Deny tokens carrying no uuid, before `rule` is evaluated."""
    # A token carrying no uuid names no employee, so it owns nothing
    return Template("token.uuid == null ? false : $rule").substitute(rule=rule)


def deny_requiring_nothing(rule: str) -> str:
    """Deny where `rule` requires nothing."""
    return Template(
        "cel.bind(required, dyn($rule), "
        # Nothing to own is not owned by anybody
        "required == null ? false : required)"
    ).substitute(rule=rule)


def owner_rule(requirements: str) -> CEL:
    """The owner rule requiring what `requirements` names owned."""
    return CEL(
        deny_tokens_without_uuid(deny_requiring_nothing(_owner_filter(requirements)))
    )


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


def person(uuid_expr: str) -> str:
    """Require ownership of the person named, if one is named."""
    return Template("""cel.bind(uuid, $uuid_expr, uuid == null ? null : dyn({
        "collection": "Employee",
        "filter": {"uuids": [uuid], "owner": owner_filter}
    }))""").substitute(uuid_expr=uuid_expr)


MutatorName: TypeAlias = str

OWNER_RULES: list[tuple[MutatorName, CEL]] = [
    # The employee itself
    ("employee_create", owner_rule(person("args.input.uuid"))),
    ("employee_terminate", owner_rule(person("args.input.uuid"))),
    ("employee_update", owner_rule(person("args.input.uuid"))),
    # The person on leave
    ("leave_create", owner_rule(person("args.input.person"))),
]
