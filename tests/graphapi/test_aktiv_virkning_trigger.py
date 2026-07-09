# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession

from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering

from ..conftest import AnotherTransaction
from ..conftest import GraphAPIPost


@pytest.mark.integration_test
async def test_aktiv_virkning_tracks_writes_to_either_table(
    empty_db: AsyncSession,
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
    create_org_unit: Callable[..., UUID],
) -> None:
    unit = create_org_unit(
        "unit",
        None,
        {"from": "2000-01-01T00:00:00+01:00", "to": "2030-01-01T00:00:00+01:00"},
    )

    async def aktiv_virkning() -> list[Range]:
        result = await empty_db.execute(
            select(OrganisationEnhedAttrEgenskaber.aktiv_virkning)
            .join(
                OrganisationEnhedRegistrering,
                OrganisationEnhedRegistrering.id
                == OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id,
            )
            .where(OrganisationEnhedRegistrering.organisationenhed_id == str(unit))
            # Each mutation appends a new registration, so take the most recent.
            .order_by(OrganisationEnhedRegistrering.id.desc())
            .limit(1)
        )
        return list(result.scalars().one())

    # The period-table trigger filled the column on insert. The unit is active
    # for the whole of its validity, so that is the whole of aktiv_virkning.
    assert await aktiv_virkning() == [
        Range(
            datetime.fromisoformat("2000-01-01T00:00:00+01:00"),
            datetime.fromisoformat("2030-01-01T00:00:00+01:00"),
            bounds="[)",
        )
    ]

    # Terminating for 2010-2020 leaves the registration active before and after.
    response = graphapi_post(
        """
        mutation Terminate($input: OrganisationUnitTerminateInput!) {
            org_unit_terminate(input: $input) { uuid }
        }
        """,
        {
            "input": {
                "uuid": str(unit),
                "from": "2010-01-01T00:00:00+01:00",
                "to": "2020-01-01T00:00:00+01:00",
            }
        },
    )
    assert response.errors is None

    assert await aktiv_virkning() == [
        Range(
            datetime.fromisoformat("2000-01-01T00:00:00+01:00"),
            datetime.fromisoformat("2010-01-01T00:00:00+01:00"),
            bounds="[)",
        ),
        Range(
            datetime.fromisoformat("2020-01-01T00:00:00+01:00"),
            datetime.fromisoformat("2030-01-01T00:00:00+01:00"),
            bounds="[)",
        ),
    ]

    # Flip the later period to Inaktiv, exercising the tils-table trigger on its
    # own: the egenskaber row is untouched. In SQL because this updates a tils
    # row in place, which LoRa never does, so no mutation produces it.
    async with another_transaction() as (_sessionmaker, session):
        await session.execute(
            text(
                "UPDATE organisationenhed_tils_gyldighed t SET gyldighed = 'Inaktiv' "
                "FROM organisationenhed_registrering r "
                "WHERE r.id = t.organisationenhed_registrering_id "
                "AND r.organisationenhed_id = :unit "
                "AND lower((t.virkning).timeperiod) = :lower"
            ),
            {
                "unit": str(unit),
                "lower": datetime.fromisoformat("2020-01-01T00:00:00+01:00"),
            },
        )

    assert await aktiv_virkning() == [
        Range(
            datetime.fromisoformat("2000-01-01T00:00:00+01:00"),
            datetime.fromisoformat("2010-01-01T00:00:00+01:00"),
            bounds="[)",
        )
    ]
