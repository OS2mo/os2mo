# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Create the root organisation."""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "a4e0c9b7d312"
down_revision: str | Sequence[str] | None = "7dee637e963a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# OS2mo requires exactly one organisation to exist. It has historically been
# created by OS2mo-init using the `org_create` mutation, or, before that,
# manually through the Service- or LoRa-API.
#
# The whole concept is annoying, and we would like to get rid of it. Perhaps
# move it all to environment variables in the future. This migration is a step
# in that direction; create the Organisation automatically, so you can ignore
# it and still use MO. This is especially useful for integration tests.
def upgrade() -> None:
    connection = op.get_bind()

    # Read the existing information
    organisation = connection.execute(
        sa.text(
            """
            select
                registrering.organisation_id,
                egenskaber.brugervendtnoegle,
                egenskaber.organisationsnavn,
                relation.rel_maal_urn
            from organisation_registrering as registrering
            join organisation_attr_egenskaber as egenskaber
                on egenskaber.organisation_registrering_id = registrering.id
                and upper((egenskaber.virkning).timeperiod) = 'infinity'
            left join organisation_relation as relation
                on relation.organisation_registrering_id = registrering.id
                and relation.rel_type = 'myndighed'
                and upper((relation.virkning).timeperiod) = 'infinity'
            where upper((registrering.registrering).timeperiod) = 'infinity'
            """
        )
    ).one_or_none()
    if organisation is not None:
        organisation_id, brugervendtnoegle, organisationsnavn, rel_maal_urn = (
            organisation
        )
    else:
        organisation_id = uuid4()
        brugervendtnoegle = "root"
        organisationsnavn = "root"
        rel_maal_urn = None

    # Truncate the organisation tables
    connection.execute(
        sa.text(
            """
            truncate
                organisation,
                organisation_registrering,
                organisation_attr_egenskaber,
                organisation_relation,
                organisation_tils_gyldighed
            """
        )
    )

    # Recreate it
    connection.execute(
        sa.text("insert into organisation (id) values (:organisation_id)"),
        {
            "organisation_id": organisation_id,
        },
    )
    registrering_id = connection.execute(
        sa.text(
            """
            insert into organisation_registrering (organisation_id, registrering)
            values (
                :organisation_id,
                row(
                    tstzrange(now(), 'infinity'),
                    'Opstaaet',
                    'a1e11b1c-baad-c0de-1337-a4e0c9b7d312',
                    ''
                )::registreringbase
            )
            returning id
            """
        ),
        {
            "organisation_id": organisation_id,
        },
    ).scalar_one()
    connection.execute(
        sa.text(
            """
            insert into organisation_attr_egenskaber (
                organisation_registrering_id,
                brugervendtnoegle,
                organisationsnavn,
                virkning
            )
            values (
                :registrering_id,
                :brugervendtnoegle,
                :organisationsnavn,
                row(tstzrange('-infinity', 'infinity'), null, null, '')::virkning
            )
            """
        ),
        {
            "registrering_id": registrering_id,
            "brugervendtnoegle": brugervendtnoegle,
            "organisationsnavn": organisationsnavn,
        },
    )
    connection.execute(
        sa.text(
            """
            insert into organisation_tils_gyldighed (
                organisation_registrering_id, gyldighed, virkning
            )
            values (
                :registrering_id,
                'Aktiv',
                row(tstzrange('-infinity', 'infinity'), null, null, '')::virkning
            )
            """
        ),
        {"registrering_id": registrering_id},
    )
    connection.execute(
        sa.text(
            """
            insert into organisation_relation (
                organisation_registrering_id, rel_type, rel_maal_urn, virkning
            )
            values (
                :registrering_id,
                'myndighed',
                :rel_maal_urn,
                row(tstzrange('-infinity', 'infinity'), null, null, '')::virkning
            )
            """
        ),
        {
            "registrering_id": registrering_id,
            "rel_maal_urn": rel_maal_urn,
        },
    )


def downgrade() -> None:
    # OS2mo cannot function without a root organisation, and we cannot tell
    # whether it existed before this migration, so leave it alone. It's fine.
    pass
