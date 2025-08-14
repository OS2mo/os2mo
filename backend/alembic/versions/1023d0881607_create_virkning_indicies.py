# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Create timeperiod indicies."""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "1023d0881607"
down_revision: str | Sequence[str] | None = "4f4da50669ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


tables = [
    "bruger_attr_egenskaber",
    "bruger_attr_udvidelser",
    "bruger_relation",
    "bruger_tils_gyldighed",
    "facet_attr_egenskaber",
    "facet_relation",
    "facet_tils_publiceret",
    "itsystem_attr_egenskaber",
    "itsystem_relation",
    "itsystem_tils_gyldighed",
    "klasse_attr_egenskaber",
    "klasse_relation",
    "klasse_tils_publiceret",
    "klassifikation_attr_egenskaber",
    "klassifikation_relation",
    "klassifikation_tils_publiceret",
    "organisation_attr_egenskaber",
    "organisationenhed_attr_egenskaber",
    "organisationenhed_relation",
    "organisationenhed_tils_gyldighed",
    "organisationfunktion_attr_egenskaber",
    "organisationfunktion_attr_udvidelser",
    "organisationfunktion_relation",
    "organisationfunktion_tils_gyldighed",
    "organisation_relation",
    "organisation_tils_gyldighed",
]


def upgrade() -> None:
    for table in tables:
        op.create_index(
            f"{table}_virkning_timeperiod_idx",
            table,
            [text("((virkning).timeperiod)")],
            postgresql_using="gist",
        )
        # lower() and upper() is used by the amqp/graphql event generator
        op.create_index(
            f"{table}_virkning_lower_idx",
            table,
            [text("lower((virkning).timeperiod)")],
        )
        op.create_index(
            f"{table}_virkning_upper_idx",
            table,
            [text("upper((virkning).timeperiod)")],
        )


def downgrade() -> None:
    for table in tables:
        op.drop_index(f"{table}_virkning_timeperiod_idx", table)
        op.drop_index(f"{table}_virkning_lower_idx", table)
        op.drop_index(f"{table}_virkning_upper_idx", table)
