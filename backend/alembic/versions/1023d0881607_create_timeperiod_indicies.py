# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""Create timeperiod indicies.

Revision ID: 1023d0881607
Revises: 4f4da50669ad
Create Date: 2025-07-11 13:05:49.100410
"""

from typing import Sequence
from typing import Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "1023d0881607"
down_revision: Union[str, None] = "4f4da50669ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

gyldighed_tables = [
    "bruger_attr_egenskaber",
    "bruger_relation",
    "bruger_tils_gyldighed",
    "itsystem_attr_egenskaber",
    "itsystem_relation",
    "itsystem_tils_gyldighed",
    "organisation_attr_egenskaber",
    "organisationenhed_attr_egenskaber",
    "organisationenhed_relation",
    "organisationenhed_tils_gyldighed",
    "organisationfunktion_attr_egenskaber",
    "organisationfunktion_relation",
    "organisationfunktion_tils_gyldighed",
    "organisation_relation",
    "organisation_tils_gyldighed",
]
publiceres_tables = [
    "facet_attr_egenskaber",
    "facet_relation",
    "facet_tils_publiceret",
    "klasse_attr_egenskaber",
    "klasse_relation",
    "klasse_tils_publiceret",
    "klassifikation_attr_egenskaber",
    "klassifikation_relation",
    "klassifikation_tils_publiceret",
]
tables = gyldighed_tables + publiceres_tables


def upgrade() -> None:
    for table in tables:
        op.create_index(
            f"{table}_virkning_timeperiod_idx",
            table,
            [text("((virkning).timeperiod)")],
            postgresql_using="gist",
        )


def downgrade() -> None:
    for table in tables:
        op.drop_index(f"{table}_virkning_timeperiod_idx", table)
