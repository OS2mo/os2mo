# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Drop unused indices."""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "4f4da50669ad"
down_revision: str | Sequence[str] | None = "fddce88bc3ac"
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
        op.drop_index(f"{table}_idx_note", table)
        op.drop_index(f"{table}_pat_note", table)


def downgrade() -> None:
    for table in tables:
        op.create_index(f"{table}_idx_note", table, [text("(((registrering).note))")])
        op.create_index(
            f"{table}_pat_note", table, [text("(((registrering).note) gin_trgm_ops)")]
        )
