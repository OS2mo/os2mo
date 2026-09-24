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


# What each mutator requires owned, read off its arguments, moving here from
# `OWNER_ENTITIES` one mutator at a time
OWNER_RULES: list[tuple[str, str]] = []
