"""Change Config's value from String to Text

This changes our ORM model to helpers/config_v2

Revision ID: 9c3ee7c575c0
Revises: 97b811d05c40
Create Date: 2020-11-13 16:11:30.547087
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9c3ee7c575c0"
down_revision = "97b811d05c40"
branch_labels = None
depends_on = None


def upgrade():
    """Alter value to Text."""
    op.alter_column(
        "orgunit_settings",
        "value",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade():
    """Alter value to VARCHAR.

    Note: This may be not be lossless.
    """
    op.alter_column(
        "orgunit_settings",
        "value",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )
