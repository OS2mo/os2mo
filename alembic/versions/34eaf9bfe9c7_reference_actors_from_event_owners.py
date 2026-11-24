# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Reference actors from event owners"""

from collections.abc import Sequence

from alembic import op

revision: str = "34eaf9bfe9c7"
down_revision: str | Sequence[str] | None = "0869a860cdf9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The built-in "mo" namespace was created with a random owner, which is not
    # an actor. It is owned by OS2mo itself.
    op.execute(
        """
        INSERT INTO actor (uuid, username)
        SELECT owner, 'os2mo' FROM event_namespace WHERE name = 'mo'
        ON CONFLICT DO NOTHING
        """
    )
    op.create_foreign_key(
        "event_namespace_owner_fkey", "event_namespace", "actor", ["owner"], ["uuid"]
    )
    op.create_foreign_key(
        "event_listener_owner_fkey", "event_listener", "actor", ["owner"], ["uuid"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "event_listener_owner_fkey", "event_listener", type_="foreignkey"
    )
    op.drop_constraint(
        "event_namespace_owner_fkey", "event_namespace", type_="foreignkey"
    )
