# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org related helper functions."""

from textwrap import dedent

import strawberry
from sqlalchemy import update

from mora import db
from mora.db import AsyncSession


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


async def create_org(session: AsyncSession, input: OrganisationCreate) -> None:
    """Set the municipality code of the root organisation.

    The root organisation itself is created by an alembic migration, so there
    is always exactly one - with exactly one registrering holding exactly one
    `myndighed` relation - and all this has to do is update that relation.
    """
    urn = (
        None
        if input.municipality_code is None
        else f"urn:dk:kommune:{input.municipality_code}"
    )
    await session.execute(
        update(db.OrganisationRelation)
        .where(
            db.OrganisationRelation.rel_type == db.OrganisationRelationKode.myndighed
        )
        .values(rel_maal_urn=urn)
    )
