# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Key actors by username"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0869a860cdf9"
down_revision: str | Sequence[str] | None = "d476d403bccc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Some systems have several actors sharing a username, e.g. when a Keycloak
    # user was deleted and recreated with the same username. We keep all of
    # them. Since we don't know which one is the current one, one of them is
    # arbitrarily chosen to keep the plain username, while the others are
    # disambiguated by appending their UUID.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                uuid,
                row_number() OVER (PARTITION BY username ORDER BY uuid) AS rank
            FROM actor
        )
        UPDATE actor
        SET username = actor.username || ' (' || actor.uuid || ')'
        FROM ranked
        WHERE ranked.uuid = actor.uuid AND ranked.rank > 1
        """
    )
    op.create_unique_constraint("actor_username_key", "actor", ["username"])

    # Actors are identified by their username. Existing actors keep their UUID,
    # while new actors get a random one.
    op.alter_column("actor", "uuid", server_default=sa.text("gen_random_uuid()"))


def downgrade() -> None:
    op.alter_column("actor", "uuid", server_default=None)
    op.drop_constraint("actor_username_key", "actor", type_="unique")
