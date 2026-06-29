# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap policyadmin policy"""

from collections.abc import Sequence

from alembic import op

revision: str = "426b7b762dae"
down_revision: str | Sequence[str] | None = "6312918462c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Magic UUID; keep in sync with mora.db.policies.POLICYADMIN_UUID.
POLICYADMIN_UUID = "ded1ca7e-9bac-5eed-706f-6c61646d696e"


def upgrade() -> None:
    # Bootstrap policy used to administer policies. Valid from 1900-01-01 and
    # open-ended. Protected from deletion by `policy_delete`.
    op.execute(
        f"""
        INSERT INTO policy (id, name, description, start, "end")
        VALUES (
            '{POLICYADMIN_UUID}',
            'Policy Administrator',
            'Bootstrap policy for administering policies.',
            '1900-01-01T00:00:00+00:00',
            NULL
        )
        ON CONFLICT (id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(f"DELETE FROM policy WHERE id = '{POLICYADMIN_UUID}'")
