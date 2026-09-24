# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The write rules of the owner policy."""

from string import Template


def rule(requirements: str) -> str:
    """Bind the caller's `seat`; a token without a uuid owns nothing."""
    return Template(
        "token.uuid == null ? false : "
        'cel.bind(seat, {"owner": {"uuids": [token.uuid]}}, cel.bind(required, '
        # Nothing to own is not owned by anybody, so requiring nothing (`null`)
        # grants nothing
        "dyn($requirements), required == null ? false : required))"
    ).substitute(requirements=requirements)


def person(uuid: str) -> str:
    """Require ownership of the person named, if one is named.

    No person is ever unset, but `uuid` may choose between the person and the
    employee, so it is bound rather than repeated.
    """
    return Template("""cel.bind(uuid, $uuid, uuid != null ? dyn({
        "collection": "Employee",
        "filter": {"uuids": [uuid], "owner": seat}
    }) : null)""").substitute(uuid=uuid)


# What each mutator requires owned, read off its arguments, moving here from
# `OWNER_ENTITIES` one mutator at a time
OWNER_RULES: list[tuple[str, str]] = [
    # The employee itself
    ("employee_create", rule(person("args.input.uuid"))),
    ("employee_terminate", rule(person("args.input.uuid"))),
    ("employee_update", rule(person("args.input.uuid"))),
]
