# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Version."""

from textwrap import dedent

import strawberry

from mora import config


@strawberry.type(description="MO and DIPEX versions")
class Version:
    @strawberry.field(
        description=dedent(
            """
            OS2mo Version.

            Contains a [semantic version](https://semver.org/) on released versions of OS2mo.
            Contains the string `HEAD` on development builds of OS2mo.

            Examples:
            * `HEAD`
            * `22.2.6`
            * `21.0.0`
            """
        )
    )
    async def mo_version(self) -> str | None:
        """Get the mo version.

        Returns:
            The version.
        """
        return config.get_settings().commit_tag

    @strawberry.field(
        description=dedent(
            """
            OS2mo commit hash.

            Contains a git hash on released versions of OS2mo.
            Contains the empty string on development builds of OS2mo.

            Examples:
            * `""`
            * `880bd2009baccbdf795a8cef3b5b32b42c91c51b`
            * `b29e45449a857cf78725eff10c5856075417ea51`
            """
        )
    )
    async def mo_hash(self) -> str | None:
        """Get the mo commit hash.

        Returns:
            The commit hash.
        """
        return config.get_settings().commit_sha

    @strawberry.field(
        description="LoRa version. Returns the exact same as `mo_version`.",
        deprecation_reason="MO and LoRa are shipped and versioned together",
    )
    async def lora_version(self) -> str | None:
        """Get the lora version.

        Returns:
            The version.
        """
        return config.get_settings().commit_tag
