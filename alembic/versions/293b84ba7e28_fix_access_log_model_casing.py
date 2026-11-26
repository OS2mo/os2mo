# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Fix access log model casing"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "293b84ba7e28"
down_revision: str | Sequence[str] | None = "68559a270001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# The models known by the access log. Other casings of these, e.g. "ITSystem"
# and "itsystem" for "ItSystem", have been logged, but cannot be read.
MODELS = [
    "AccessLog",
    "Actor",
    "Bruger",
    "CPRPerson",
    "Facet",
    "File",
    "ItSystem",
    "Klasse",
    "Organisation",
    "OrganisationEnhed",
    "OrganisationFunktion",
    "Registration",
]

access_log_operation = sa.table(
    "access_log_operation",
    sa.column("model", sa.Text),
)


def upgrade() -> None:
    models = sa.values(sa.column("model", sa.Text), name="models").data(
        [(model,) for model in MODELS]
    )
    op.execute(
        access_log_operation.update()
        .where(
            sa.func.lower(access_log_operation.c.model)
            == sa.func.lower(models.c.model),
            access_log_operation.c.model != models.c.model,
        )
        .values(model=models.c.model)
    )


def downgrade() -> None:
    pass
