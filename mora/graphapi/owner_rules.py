# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The write rules of the owner policy."""

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


def org_unit_or_person(org_unit_uuid: str, person_uuid: str) -> str:
    """Require ownership of the unit if one is named, else of the person."""
    return Template("cel.bind(unit, $unit, unit != null ? unit : $person)").substitute(
        unit=org_unit(org_unit_uuid), person=person(person_uuid)
    )


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
]
