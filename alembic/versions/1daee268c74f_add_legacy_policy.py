# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add Legacy policy"""

# TODO: Before release, consider folding this into the prior policy migrations.

from collections.abc import Sequence

from alembic import op

revision: str = "1daee268c74f"
down_revision: str | Sequence[str] | None = "401749b213fe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# "legacy" encoded in the UUID tail (6c6567616379).
LEGACY_UUID = "0b50137e-9bac-5eed-0000-6c6567616379"


def upgrade() -> None:
    # The Legacy policy reproduces the old RBAC behaviour inside the policy
    # system: it applies to everyone and grants every query and mutator, but
    # each grant is gated by a CEL condition requiring the field's RBAC role to
    # be present on the token -- i.e. the classic `if permission_role in
    # token_roles: return True`. The `permission` variable is the role the
    # accessed field requires (e.g. "read_employee", "create_address").
    op.execute(
        f"""
        INSERT INTO policy (id, name, description, start, "end")
        VALUES (
          '{LEGACY_UUID}',
          'Legacy',
          'Reproduces legacy RBAC: grants any field whose required role is on the token.',
          '1900-01-01T00:00:00+00:00',
          NULL
        )
        """
    )
    # Applies to everyone (an "all" actor matches every actor).
    op.execute(
        f"""
        INSERT INTO policy_actor (kind, value, policy_fk)
        VALUES ('all', '', '{LEGACY_UUID}')
        """
    )
    # All queries and all mutators, each subject to the role check.
    op.execute(
        f"""
        INSERT INTO policy_rule (type, field, condition, policy_fk)
        VALUES
          ('Query', '*', 'permission in token.roles', '{LEGACY_UUID}'),
          ('Mutation', '*', 'permission in token.roles', '{LEGACY_UUID}')
        """
    )


def downgrade() -> None:
    op.execute(f"DELETE FROM policy_rule WHERE policy_fk = '{LEGACY_UUID}'")
    op.execute(f"DELETE FROM policy_actor WHERE policy_fk = '{LEGACY_UUID}'")
    op.execute(f"DELETE FROM policy WHERE id = '{LEGACY_UUID}'")
