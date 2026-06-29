# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add Administrator and Reader policies"""

# TODO: Before release, consider folding this into the prior policy migrations.

from collections.abc import Sequence

from alembic import op

revision: str = "54bce9fff984"
down_revision: str | Sequence[str] | None = "1a80105acf1d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Normal (removable, editable) policies, unlike the protected policyadmin one.
# "admin"/"reader" encoded in the UUID tails (61646d696e / 726561646572).
ADMINISTRATOR_UUID = "e5ca1a7e-9bac-5eed-0000-0061646d696e"
READER_UUID = "acce5500-9bac-5eed-0000-726561646572"


def upgrade() -> None:
    # Two convenience policies, valid for all time. Each is bound to a role
    # below (see the policy_actor inserts), so it grants access to actors
    # holding that role.
    op.execute(
        f"""
        INSERT INTO policy (id, name, description, start, "end")
        VALUES
          (
            '{ADMINISTRATOR_UUID}',
            'Administrator',
            'Grants access to all queries and mutators.',
            '1900-01-01T00:00:00+00:00',
            NULL
          ),
          (
            '{READER_UUID}',
            'Reader',
            'Grants read access to all queries.',
            '1900-01-01T00:00:00+00:00',
            NULL
          )
        """
    )
    # "*" matches every field/mutator on the type.
    op.execute(
        f"""
        INSERT INTO policy_rule (type, field, policy_fk)
        VALUES
          ('Query', '*', '{ADMINISTRATOR_UUID}'),
          ('Mutation', '*', '{ADMINISTRATOR_UUID}'),
          ('Query', '*', '{READER_UUID}')
        """
    )
    # Administrator is bound to the "admin" role; Reader to the "reader" role.
    op.execute(
        f"""
        INSERT INTO policy_actor (kind, value, policy_fk)
        VALUES
          ('role', 'admin', '{ADMINISTRATOR_UUID}'),
          ('role', 'reader', '{READER_UUID}')
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        DELETE FROM policy_rule
        WHERE policy_fk IN ('{ADMINISTRATOR_UUID}', '{READER_UUID}')
        """
    )
    op.execute(
        f"""
        DELETE FROM policy_actor
        WHERE policy_fk IN ('{ADMINISTRATOR_UUID}', '{READER_UUID}')
        """
    )
    op.execute(
        f"DELETE FROM policy WHERE id IN ('{ADMINISTRATOR_UUID}', '{READER_UUID}')"
    )
