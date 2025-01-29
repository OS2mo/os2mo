# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org related helper functions."""

import logging
from textwrap import dedent
from uuid import UUID

import strawberry

from mora import common

from .orgmodel import Organisation

logger = logging.getLogger(__name__)


@strawberry.input
class OrganisationCreate:
    """Input model for creating org-units."""

    municipality_code: int | None = strawberry.field(
        description=dedent(
            """\
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


async def create_org(input: OrganisationCreate) -> UUID:
    org_scope = common.get_connector().organisation

    # Ensure that no root organisation already exists
    # NOTE: This code does a direct lookup in LoRa as OS2mo code usually has the
    #       invariant that a root organisation always exists.
    organisations = list(await org_scope.fetch(bvn="%"))
    if len(organisations) != 0:
        raise ValueError("Root organisation already exists")

    model = Organisation.from_simplified_fields(
        name="root",
        user_key="root",
        municipality_code=input.municipality_code,
    )
    payload = model.dict(by_alias=True, exclude={"uuid"}, exclude_none=True)
    uuid = await org_scope.create(payload)
    return UUID(uuid)
