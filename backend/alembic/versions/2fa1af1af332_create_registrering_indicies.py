# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""Create registration indicies.

Revision ID: 2fa1af1af332
Revises: 1023d0881607
Create Date: 2025-07-31 11:39:11.182346
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2fa1af1af332"
down_revision: str | None = "1023d0881607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


tables = [
    "bruger_registrering",
    "facet_registrering",
    "itsystem_registrering",
    "klasse_registrering",
    "klassifikation_registrering",
    "organisation_registrering",
    "organisationenhed_registrering",
    "organisationfunktion_registrering",
]


def upgrade() -> None:
    for table in tables:
        op.create_index(
            f"{table}_registrering_timeperiod_idx",
            table,
            [sa.text("((registrering).timeperiod)")],
            postgresql_using="gist",
        )
        # lower() is used by the amqp/graphql event generator
        op.create_index(
            f"{table}_registrering_lower_idx",
            table,
            [sa.text("lower((registrering).timeperiod)")],
        )


def downgrade() -> None:
    for table in tables:
        op.drop_index(f"{table}_registrering_timeperiod_idx", table)
        op.drop_index(f"{table}_registrering_lower_idx", table)
