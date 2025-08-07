# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""rename audit-log to access-log."""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1739b5155aa"
down_revision: str | Sequence[str] | None = "68ccf4b69392"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


table_map = {
    "audit_log_operation": "access_log_operation",
    "audit_log_read": "access_log_read",
}
index_map = {
    "audit_log_operation_pkey": "access_log_operation_pkey",
    "ix_audit_log_operation_actor": "ix_access_log_operation_actor",
    "ix_audit_log_operation_model": "ix_access_log_operation_model",
    "ix_audit_log_operation_time": "ix_access_log_operation_time",
    "audit_log_read_pkey": "access_log_read_pkey",
    "ix_audit_log_read_uuid": "ix_access_log_read_uuid",
}
constraint_map = {
    "audit_log_read_operation_id_fkey": "access_log_read_operation_id_fkey",
}


def upgrade() -> None:
    for old, new in table_map.items():
        op.rename_table(old, new)
    for old, new in index_map.items():
        op.execute(f"alter index {old} rename to {new};")
    for old, new in constraint_map.items():
        op.execute(f"alter table access_log_read rename constraint {old} to {new};")


def downgrade() -> None:
    for old, new in table_map.items():
        op.rename_table(new, old)
    for old, new in index_map.items():
        op.execute(f"alter index {new} rename to {old};")
    for old, new in constraint_map.items():
        op.execute(f"alter table access_log_read rename constraint {new} to {old};")
