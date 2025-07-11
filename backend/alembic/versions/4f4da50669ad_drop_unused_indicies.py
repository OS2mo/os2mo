# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""Drop unused indices.

Revision ID: 4f4da50669ad
Revises: fddce88bc3ac
Create Date: 2025-07-11 12:16:18.249846
"""

from typing import Sequence
from typing import Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "4f4da50669ad"
down_revision: Union[str, None] = "fddce88bc3ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


collections = [
    "bruger",
    "facet",
    "itsystem",
    "klasse",
    "klassifikation",
    "organisation",
    "organisationenhed",
    "organisationfunktion",
]
tables = [f"{collection}_registrering" for collection in collections]


def upgrade() -> None:
    for table in tables:
        op.drop_index(f"{table}_idx_note", table)
        op.drop_index(f"{table}_pat_note", table)


def downgrade() -> None:
    for table in tables:
        op.create_index(f"{table}_idx_note", table, [text("(((registrering).note))")])
        op.create_index(
            f"{table}_pat_note", table, [text("(((registrering).note) gin_trgm_ops)")]
        )
