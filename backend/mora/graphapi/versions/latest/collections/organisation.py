# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Organisation."""

import re
from textwrap import dedent
from uuid import UUID

import strawberry

from mora import common
from mora.graphapi.gmodels.mo import OrganisationRead

MUNICIPALITY_CODE_PATTERN = re.compile(r"urn:dk:kommune:(\d+)")


@strawberry.type(description="Root organisation - one and only one of these can exist")
class Organisation:
    # TODO: Eliminate the OrganisationRead model from here. Use self instead.

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: OrganisationRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Examples:
            * `root`
            * `0751` (municipality code)
            * `3b866d97-0b1f-48e0-8078-686d96f430b3` (copied entity UUID)
            * `Kolding Kommune` (municipality name)
            * `Magenta ApS` (company name)
            """
        )
    )
    async def user_key(self, root: OrganisationRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            Name of the organisation.

            Examples:
            * `root`
            * `Kolding Kommune` (or similar municipality name)
            * `Magenta ApS` (or similar company name)
            """
        )
    )
    async def name(self, root: OrganisationRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `organisation`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: OrganisationRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(
        description=dedent(
            """
            The municipality code.

            In Denmark; a 3 digit number uniquely identifying a municipality.
            Generally used to map the Local administrative units (LAU) of the
            Nomenclature of Territorial Units for Statistics (NUTS) standard.

            A list of all danish municipality codes can be found here:
            * https://danmarksadresser.dk/adressedata/kodelister/kommunekodeliste

            Examples:
            * `null` (unset)
            * `101` (Copenhagen)
            * `461` (Odense)
            * `751` (Aarhus)
            """
        )
    )
    async def municipality_code(self, root: OrganisationRead) -> int | None:
        """Get the municipality code for the organisation unit (if any).

        Returns:
            The municipality code, if any is found.
        """
        org = await common.get_connector().organisation.get(root.uuid)
        if org is None:  # pragma: no cover
            return None
        authorities = org.get("relationer", {}).get("myndighed", [])
        for authority in authorities:
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(authority.get("urn"))
            if m:
                return int(m.group(1))
        return None  # pragma: no cover
