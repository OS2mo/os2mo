# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Health."""

from textwrap import dedent

import strawberry

from ..health import health_map


@strawberry.type(description="Status on whether a specific subsystem is working")
class Health:
    identifier: str = strawberry.field(
        description=dedent(
            """
        Healthcheck identifier.

        Examples:
        * `"dataset"`
        * `"dar"`
        * `"amqp"`
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """
        Healthcheck status.

        Returns:
        * `true` if the healthcheck passed
        * `false` if the healthcheck failed
        * `null` if the healthcheck is irrelevant (submodule not loaded, etc)

        Note:
        Querying the healthcheck status executes the underlying healthcheck directly.
        Excessively querying this endpoint may have performance implications.
        """
        )
    )
    async def status(self) -> bool | None:
        return await health_map[self.identifier]()
