# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Move the read rules into the policy tables"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from alembic_helpers.read_rules import READ_RULES

revision: str = "b93e5c17af08"
down_revision: str | Sequence[str] | None = "c4d81f0a7b32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"

policy = sa.table(
    "policy",
    sa.column("pk", sa.Uuid),
    sa.column("name", sa.Text),
    sa.column("description", sa.Text),
    sa.column("role", sa.Text),
)
policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("pk", sa.Uuid),
    sa.column(
        "collection", postgresql.ENUM(name="policycollection", create_type=False)
    ),
    sa.column("policy_fk", sa.Uuid),
)
policy_read_rule_field = sa.table(
    "policy_read_rule_field",
    sa.column("field", sa.Text),
    sa.column("rule_fk", sa.Uuid),
)


def upgrade() -> None:
    rule_pks = {collection: uuid4() for collection in READ_RULES}

    op.bulk_insert(
        policy,
        [
            {
                "pk": READER_UUID,
                "name": "Reader",
                "description": "Read access to the fields of every collection",
                "role": "reader",
            }
        ],
    )
    op.bulk_insert(
        policy_read_rule,
        [
            {
                "pk": rule_pks[collection],
                "collection": collection,
                "policy_fk": READER_UUID,
            }
            for collection in READ_RULES
        ],
    )
    op.bulk_insert(
        policy_read_rule_field,
        [
            {
                "field": field,
                "rule_fk": rule_pks[collection],
            }
            for collection, fields in READ_RULES.items()
            for field in fields
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_read_rule_field.delete().where(
            policy_read_rule_field.c.rule_fk == policy_read_rule.c.pk,
            policy_read_rule.c.policy_fk == READER_UUID,
        )
    )
    op.execute(
        policy_read_rule.delete().where(policy_read_rule.c.policy_fk == READER_UUID)
    )
    op.execute(policy.delete().where(policy.c.pk == READER_UUID))
