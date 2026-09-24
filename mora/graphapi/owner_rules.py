# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The write rules of the owner policy."""

from functools import partial
from string import Template


def rule(requirements: str) -> str:
    """Bind the caller's `seat`; a token without a uuid owns nothing.

    Nothing to own is not owned by anybody, so requiring nothing (`null`)
    grants nothing.
    """
    return Template(
        "token.uuid == null ? false : "
        'cel.bind(seat, {"owner": {"uuids": [token.uuid]}}, cel.bind(required, '
        "dyn($requirements), required == null ? false : required))"
    ).substitute(requirements=requirements)


def org_unit(uuid: str) -> str:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors. An unset `uuid` is absent from
    the arguments, so `uuid` must be a field.
    """
    return Template("""(has($uuid) && $uuid != null ? dyn({
        "collection": "OrganisationUnit",
        "filter": {"descendant": {"uuids": [$uuid]}, "owner": seat}
    }) : null)""").substitute(uuid=uuid)


def person(uuid: str) -> str:
    """Require ownership of the person named, if one is named.

    No person is ever unset, but `uuid` may choose between the person and the
    employee, so it is bound rather than repeated.
    """
    return Template("""cel.bind(uuid, $uuid, uuid != null ? dyn({
        "collection": "Employee",
        "filter": {"uuids": [uuid], "owner": seat}
    }) : null)""").substitute(uuid=uuid)


def detail_org_unit(uuid: str, *, collection: str) -> str:
    """Require ownership of the org unit the detail links, through any ancestor."""
    return Template("""dyn({
        "collection": "$collection",
        "filter": {"uuids": [$uuid], "org_unit": {"ancestor": {"owner": seat}}}
    })""").substitute(collection=collection, uuid=uuid)


def detail_person(uuid: str, *, collection: str) -> str:
    """Require ownership of the person the detail links."""
    return Template("""dyn({
        "collection": "$collection",
        "filter": {"uuids": [$uuid], "employee": {"owner": seat}}
    })""").substitute(collection=collection, uuid=uuid)


def detail(uuid: str, *, collection: str) -> str:
    """Require ownership of the org unit or the person the detail links."""
    return Template('dyn({"or": [$org_unit, $person]})').substitute(
        org_unit=detail_org_unit(uuid, collection=collection),
        person=detail_person(uuid, collection=collection),
    )


def and_or_none(*checks: str) -> str:
    """Require all of the checks, or nothing if there is nothing to check."""
    return Template("""cel.bind(clauses, [$checks].filter(clause, clause != null),
        clauses.size() == 0 ? null : dyn({"and": clauses}))""").substitute(
        checks=", ".join(checks)
    )


def and_or_none_each(check: str) -> str:
    """Require the check of each `input`, or nothing if there is nothing to check."""
    return Template("""cel.bind(clauses, args.input.map(input, $check)
        .filter(clause, clause != null),
        clauses.size() == 0 ? null : dyn({"and": clauses}))""").substitute(check=check)


def org_unit_or_person(org_unit_uuid: str, person_uuid: str) -> str:
    """Require ownership of the unit if one is named, else of the person."""
    return Template("cel.bind(unit, $unit, unit != null ? unit : $person)").substitute(
        unit=org_unit(org_unit_uuid), person=person(person_uuid)
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


# What each mutator requires owned, read off its arguments, moving here from
# `OWNER_ENTITIES` one mutator at a time
OWNER_RULES: list[tuple[str, str]] = [
    # The unit or the person the address links to (exactly one is set)
    (
        "address_create",
        rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    ("address_terminate", rule(address("args.input.uuid"))),
    (
        "address_update",
        rule(
            and_or_none(
                address("args.input.uuid"),
                org_unit_or_person(
                    "args.input.org_unit",
                    "args.input.person != null ? args.input.person : args.input.employee",
                ),
            )
        ),
    ),
    (
        "addresses_create",
        rule(
            and_or_none_each(
                org_unit_or_person(
                    "input.org_unit",
                    "input.person != null ? input.person : input.employee",
                )
            )
        ),
    ),
    # The unit of the association
    (
        "association_create",
        rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    ("association_terminate", rule(association("args.input.uuid"))),
    (
        "association_update",
        rule(
            and_or_none(
                association("args.input.uuid"),
                org_unit_or_person(
                    "args.input.org_unit",
                    "args.input.person != null ? args.input.person : args.input.employee",
                ),
            )
        ),
    ),
    # The employee itself
    ("employee_create", rule(person("args.input.uuid"))),
    ("employee_terminate", rule(person("args.input.uuid"))),
    ("employee_update", rule(person("args.input.uuid"))),
    # The unit of the engagement
    (
        "engagement_create",
        rule(
            org_unit_or_person(
                "args.input.org_unit",
                "args.input.person != null ? args.input.person : args.input.employee",
            )
        ),
    ),
    ("engagement_terminate", rule(engagement("args.input.uuid"))),
    (
        "engagement_update",
        rule(
            and_or_none(
                engagement("args.input.uuid"),
                org_unit_or_person(
                    "args.input.org_unit",
                    "args.input.person != null ? args.input.person : args.input.employee",
                ),
            )
        ),
    ),
    (
        "engagements_create",
        rule(
            and_or_none_each(
                org_unit_or_person(
                    "input.org_unit",
                    "input.person != null ? input.person : input.employee",
                )
            )
        ),
    ),
    (
        "engagements_update",
        rule(
            and_or_none_each(
                and_or_none(
                    engagement("input.uuid"),
                    org_unit_or_person(
                        "input.org_unit",
                        "input.person != null ? input.person : input.employee",
                    ),
                )
            )
        ),
    ),
    # The unit of the IT-association, whose update cannot name a person
    (
        "itassociation_create",
        rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("itassociation_terminate", rule(association("args.input.uuid"))),
    (
        "itassociation_update",
        rule(
            and_or_none(association("args.input.uuid"), org_unit("args.input.org_unit"))
        ),
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    (
        "ituser_create",
        rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("ituser_terminate", rule(ituser("args.input.uuid"))),
    (
        "ituser_update",
        rule(
            and_or_none(
                ituser("args.input.uuid"),
                org_unit_or_person("args.input.org_unit", "args.input.person"),
            )
        ),
    ),
    (
        "itusers_create",
        rule(and_or_none_each(org_unit_or_person("input.org_unit", "input.person"))),
    ),
    # The annotated unit
    ("kle_create", rule(org_unit("args.input.org_unit"))),
    ("kle_terminate", rule(kle("args.input.uuid"))),
    (
        "kle_update",
        rule(and_or_none(kle("args.input.uuid"), org_unit("args.input.org_unit"))),
    ),
    # The person on leave
    ("leave_create", rule(person("args.input.person"))),
    ("leave_terminate", rule(leave("args.input.uuid"))),
    (
        "leave_update",
        rule(and_or_none(leave("args.input.uuid"), person("args.input.person"))),
    ),
    # The unit of the manager
    (
        "manager_create",
        rule(org_unit_or_person("args.input.org_unit", "args.input.person")),
    ),
    ("manager_terminate", rule(manager("args.input.uuid"))),
]
