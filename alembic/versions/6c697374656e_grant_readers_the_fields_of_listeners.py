# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Grant readers the fields of listeners"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "6c697374656e"
down_revision: str | Sequence[str] | None = "617374657874"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
COLLECTION = "Listener"
# The fields a reader could read before listeners became a collection
FIELDS = frozenset({"events", "namespace", "owner", "routing_key", "user_key", "uuid"})

policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("pk", sa.Uuid),
    sa.column("collection", sa.Text),
    sa.column("condition", sa.Text),
    sa.column("graphql_version", sa.Integer),
    sa.column("policy_fk", sa.Uuid),
)
policy_read_rule_field = sa.table(
    "policy_read_rule_field",
    sa.column("field", sa.Text),
    sa.column("rule_fk", sa.Uuid),
)


def upgrade() -> None:
    rule_pk = uuid4()
    op.bulk_insert(
        policy_read_rule,
        [
            {
                "pk": rule_pk,
                "collection": COLLECTION,
                "condition": "true",
                "graphql_version": 30,
                "policy_fk": READER_UUID,
            }
        ],
    )
    op.bulk_insert(
        policy_read_rule_field,
        [{"field": field, "rule_fk": rule_pk} for field in FIELDS],
    )


def downgrade() -> None:
    # The rules of every policy go, as no rule may name an unknown collection
    op.execute(
        policy_read_rule.delete().where(policy_read_rule.c.collection == COLLECTION)
    )
