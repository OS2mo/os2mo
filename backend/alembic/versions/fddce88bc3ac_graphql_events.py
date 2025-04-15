# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""graphql events

Revision ID: fddce88bc3ac
Revises: b1739b5155aa
Create Date: 2025-03-17 12:55:21.321176
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fddce88bc3ac"
down_revision = "b1739b5155aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_namespace",
        sa.Column(
            "name",
            sa.String(length=255),
            primary_key=True,
        ),
        sa.Column("owner", sa.Uuid, nullable=False),
        sa.Column("public", sa.Boolean, nullable=False),
    )

    op.create_table(
        "event_listener",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_key", sa.String(length=255), nullable=False),
        sa.Column("owner", sa.Uuid, nullable=False),
        sa.Column("routing_key", sa.String(length=255), nullable=False),
        sa.Column(
            "namespace_fk",
            sa.String,
            sa.ForeignKey("event_namespace.name"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_key",
            "owner",
            "namespace_fk",
            name="uq_user_key_owner_namespace",
        ),
    )

    op.create_table(
        "event",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("subject", sa.String, nullable=False),
        sa.Column("priority", sa.Integer, nullable=False),
        sa.Column(
            "generation",
            sa.Uuid,
            nullable=False,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "last_tried",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("'1970-01-01'::timestamptz"),
        ),
        sa.Column(
            "fetched_count", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column("silenced", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "listener_fk", sa.Uuid, sa.ForeignKey("event_listener.pk"), nullable=False
        ),
        sa.UniqueConstraint("listener_fk", "subject", name="uq_listener_subject"),
    )

    op.execute("insert into event_namespace values ('mo', uuid_generate_v4(), true)")


def downgrade() -> None:
    op.drop_table("event")
    op.drop_table("event_listener")
    op.drop_table("event_namespace")
