# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Descriptions shared by the filter arguments across the GraphQL API."""

from textwrap import dedent


def gen_filter_string(title: str, key: str) -> str:
    return dedent(
        f"""\
        {title} filter limiting which entries are returned.
        """
    ) + gen_filter_table(key)


def gen_filter_table(key: str) -> str:
    return dedent(
        f"""\

        | `{key}`      | Elements returned                            |
        |--------------|----------------------------------------------|
        | not provided | All                                          |
        | `null`       | All                                          |
        | `[]`         | None                                         |
        | `"x"`        | `["x"]` or `[]` (`*`)                        |
        | `["x", "y"]` | `["x", "y"]`, `["x"]`, `["y"]` or `[]` (`*`) |

        `*`: Elements returned depends on which elements were found.
        """
    )
