# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The rules of the owner policy, translated into CEL."""

from functools import partial
from string import Template
from typing import TypeAlias

from mora.graphapi.policy_cel import CEL


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


def detail_org_unit(uuid_expr: str, *, collection: str) -> str:
    """Require ownership of the org unit the detail links, through any ancestor."""
    return Template("""dyn({
        "collection": "$collection",
        "filter": {"uuids": [$uuid_expr], "org_unit": {
            "ancestor": {"owner": owner_filter}
        }}
    })""").substitute(collection=collection, uuid_expr=uuid_expr)


def detail_person(uuid_expr: str, *, collection: str) -> str:
    """Require ownership of the person the detail links."""
    return Template("""dyn({
        "collection": "$collection",
        "filter": {"uuids": [$uuid_expr], "employee": {"owner": owner_filter}}
    })""").substitute(collection=collection, uuid_expr=uuid_expr)


def detail(uuid_expr: str, *, collection: str) -> str:
    """Require ownership of the org unit or the person the detail links."""
    return Template('dyn({"or": [$org_unit, $person]})').substitute(
        org_unit=detail_org_unit(uuid_expr, collection=collection),
        person=detail_person(uuid_expr, collection=collection),
    )


def org_unit_or_person(org_unit_uuid_expr: str, person_uuid_expr: str) -> str:
    """Require ownership of the unit if one is named, else of the person."""
    return Template("cel.bind(unit, $unit, unit != null ? unit : $person)").substitute(
        unit=org_unit(org_unit_uuid_expr), person=person(person_uuid_expr)
    )


# The rule for each collection's detail. A KLE and a role-binding link no
# person, so owning the unit they link is the only way to own them
address = partial(detail, collection="Address")
association = partial(detail, collection="Association")
engagement = partial(detail, collection="Engagement")
ituser = partial(detail, collection="ITUser")
kle = partial(detail_org_unit, collection="KLE")
leave = partial(detail, collection="Leave")
manager = partial(detail, collection="Manager")
owner = partial(detail, collection="Owner")
rolebinding = partial(detail_org_unit, collection="RoleBinding")


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
    ("address_terminate", owner_rule(address("args.input.uuid"))),
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
    ("association_terminate", owner_rule(association("args.input.uuid"))),
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
    ("engagement_terminate", owner_rule(engagement("args.input.uuid"))),
    # The unit of the IT-association, whose update cannot name a person
    (
        "itassociation_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("itassociation_terminate", owner_rule(association("args.input.uuid"))),
    # The unit or the person the IT-user belongs to (exactly one is set)
    (
        "ituser_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("ituser_terminate", owner_rule(ituser("args.input.uuid"))),
    # The annotated unit
    ("kle_create", owner_rule(org_unit("args.input.org_unit"))),
    ("kle_terminate", owner_rule(kle("args.input.uuid"))),
    # The person on leave
    ("leave_create", owner_rule(person("args.input.person"))),
    ("leave_terminate", owner_rule(leave("args.input.uuid"))),
    # The unit of the manager
    (
        "manager_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("manager_terminate", owner_rule(manager("args.input.uuid"))),
    # The parent, or the unit itself and its new parent if it is being moved
    ("org_unit_create", owner_rule(org_unit("args.input.parent"))),
    ("org_unit_terminate", owner_rule(org_unit("args.input.uuid"))),
    # The unit or the person owned (exactly one is set)
    (
        "owner_create",
        owner_rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("owner_terminate", owner_rule(owner("args.input.uuid"))),
    # Related units have a single `origin` field and a list of
    # `destination`s. Originally we required ownership of both the
    # origin and destinations, but that's not compatible with the old
    # service-api owner calculation
    ("related_units_update", owner_rule(org_unit("args.input.origin"))),
    # The unit of the role-binding, if one is named
    ("rolebinding_create", owner_rule(org_unit("args.input.org_unit"))),
    ("rolebinding_terminate", owner_rule(rolebinding("args.input.uuid"))),
]
