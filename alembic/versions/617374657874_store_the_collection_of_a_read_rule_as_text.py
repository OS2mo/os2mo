# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Store the collection of a read rule as text"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "617374657874"
down_revision: str | Sequence[str] | None = "b45b3fbb0cbf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COLLECTION = sa.Enum(
    "Address",
    "Association",
    "Class",
    "Employee",
    "Engagement",
    "Facet",
    "ITSystem",
    "ITUser",
    "KLE",
    "Leave",
    "Manager",
    "Organisation",
    "OrganisationUnit",
    "Owner",
    "RelatedUnit",
    "RoleBinding",
    name="policycollection",
)


def upgrade() -> None:
    op.alter_column(
        "policy_read_rule",
        "collection",
        type_=sa.Text,
        postgresql_using="collection::text",
    )
    COLLECTION.drop(op.get_bind())


def downgrade() -> None:
    COLLECTION.create(op.get_bind())
    op.alter_column(
        "policy_read_rule",
        "collection",
        type_=COLLECTION,
        postgresql_using="collection::policycollection",
    )
