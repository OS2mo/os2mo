# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The rules of the owner policy, translated into CEL."""

from collections.abc import Callable
from string import Template
from typing import TypeAlias
from typing import get_type_hints
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.policy_cel import CEL
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


def org_unit(uuid_expr: str) -> str:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    # An unset uuid is absent from the arguments, so `uuid_expr` must be a field
    return Template("""(!has($uuid_expr) ? null : $uuid_expr == null ? null : dyn({
        "collection": "OrganisationUnit",
        "filter": {"descendant": {"uuids": [$uuid_expr]}, "owner": owner_filter}
    }))""").substitute(uuid_expr=uuid_expr)


def person(uuid_expr: str) -> str:
    """Require ownership of the person named, if one is named."""
    return Template("""cel.bind(uuid, $uuid_expr, uuid == null ? null : dyn({
        "collection": "Employee",
        "filter": {"uuids": [uuid], "owner": owner_filter}
    }))""").substitute(uuid_expr=uuid_expr)


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


def org_unit_or_person(org_unit_uuid_expr: str, person_uuid_expr: str) -> str:
    """Require ownership of the unit if one is named, else of the person."""
    return Template("cel.bind(unit, $unit, unit != null ? unit : $person)").substitute(
        unit=org_unit(org_unit_uuid_expr), person=person(person_uuid_expr)
    )


MutatorName: TypeAlias = str

OWNER_RULES: list[tuple[MutatorName, CEL]] = [
    # The unit or the person the address links to (exactly one is set)
    (
        "address_create",
        owner_rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    # The unit of the association
    (
        "association_create",
        owner_rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    # The employee itself
    ("employee_create", owner_rule(person("args.input.uuid"))),
    ("employee_terminate", owner_rule(person("args.input.uuid"))),
    ("employee_update", owner_rule(person("args.input.uuid"))),
    # The unit of the engagement
    (
        "engagement_create",
        owner_rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    # The unit of the IT-association, whose update cannot name a person
    (
        "itassociation_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    (
        "ituser_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    # The annotated unit
    ("kle_create", owner_rule(org_unit("args.input.org_unit"))),
    # The person on leave
    ("leave_create", owner_rule(person("args.input.person"))),
    # The unit of the manager
    (
        "manager_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    ("org_unit_create", owner_rule(org_unit("args.input.parent"))),
    ("org_unit_terminate", owner_rule(org_unit("args.input.uuid"))),
    # The unit or the person owned (exactly one is set)
    (
        "owner_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    # Related units have a single `origin` field and a list of
    # `destination`s. Originally we required ownership of both the
    # origin and destinations, but that's not compatible with the old
    # service-api owner calculation
    ("related_units_update", owner_rule(org_unit("args.input.origin"))),
    # The unit of the role-binding, if one is named
    ("rolebinding_create", owner_rule(org_unit("args.input.org_unit"))),
]
