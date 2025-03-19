# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""graphql events

Revision ID: fddce88bc3ac
Revises: b1739b5155aa
Create Date: 2025-03-17 12:55:21.321176
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fddce88bc3ac'
down_revision = 'b1739b5155aa'
branch_labels= None
depends_on= None


def upgrade() -> None:
    op.create_table(
        "listener",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_key", sa.String, nullable=False),
        sa.Column("owner", sa.Uuid, nullable=False),
        sa.Column("namespace", sa.String, nullable=False),
        sa.Column('routing_key', sa.String, nullable=False),
        sa.UniqueConstraint('user_key', 'owner', 'namespace', "routing_key", name='uq_user_key_owner_namespace_routing_key'),
    )

    op.create_table(
        'event',
        sa.Column('pk', sa.Uuid, primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('subject', sa.String, nullable=False),
        sa.Column('priority', sa.Integer, nullable=False),
        sa.Column('last_tried', sa.DateTime(timezone=True), nullable=False),
        sa.Column('silenced', sa.Boolean, nullable=False),
        sa.Column('listener_fk', sa.Uuid, sa.ForeignKey('listener.pk'), nullable=False),
        sa.UniqueConstraint('listener_fk', 'subject', 'priority', name='uq_listener_subject_priority'),
    )


def downgrade() -> None:
    op.drop_table("event")
    op.drop_table("listener")
