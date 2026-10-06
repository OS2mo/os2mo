# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Grant readers the fields of rolebinding rules"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "726f6c656269"
down_revision: str | Sequence[str] | None = "c7a41f0b93d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
FIELDS_OF_COLLECTION = {
    "RolebindingRule": frozenset({"created_at", "current", "uuid"}),
    "RolebindingRuleRevision": frozenset(
        {"active", "actor", "created_at", "expression", "name", "role"}
    ),
}


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
    rule_pks = {collection: uuid4() for collection in FIELDS_OF_COLLECTION}
    op.bulk_insert(
        policy_read_rule,
        [
            {
                "pk": rule_pk,
                "collection": collection,
                "condition": "true",
                "graphql_version": 30,
                "policy_fk": READER_UUID,
            }
            for collection, rule_pk in rule_pks.items()
        ],
    )
    op.bulk_insert(
        policy_read_rule_field,
        [
            {"field": field, "rule_fk": rule_pks[collection]}
            for collection, fields in FIELDS_OF_COLLECTION.items()
            for field in fields
        ],
    )


def downgrade() -> None:
    # The rules of EVERY policy on these collections go, as no rule may name an
    # unknown collection
    op.execute(
        policy_read_rule.delete().where(
            policy_read_rule.c.collection.in_(FIELDS_OF_COLLECTION)
        )
    )
