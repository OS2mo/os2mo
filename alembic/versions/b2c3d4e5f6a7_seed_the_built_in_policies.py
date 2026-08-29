# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Seed the built-in policies.

Loads the hardcoded `POLICIES` from `mora.graphapi.policies_builtin` into the
policy tables, so the database holds the same access the code enforces today.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from mora.db._policies import Policy as PolicyRow
from mora.db._policies import PolicyMutator
from mora.db._policies import PolicyReader
from mora.db._policies import PolicySelector
from mora.db._policies import PolicySelectorKind
from mora.db._policies import PolicyTypeGrant
from mora.graphapi.policies_builtin import POLICIES

revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _to_row(policy) -> PolicyRow:
    row = PolicyRow(
        name=policy.name,
        active=True,
        selectors=[
            PolicySelector(
                kind=PolicySelectorKind(policy.selector.kind.value),
                value=policy.selector.value,
            )
        ],
        readers=[
            PolicyReader(
                collection=r.collection,
                fields=sorted(r.fields),
                k=r.k,
                condition=r.condition,
            )
            for r in policy.readers
        ],
        mutators=[PolicyMutator(name=m.name, mk=m.mk, k=m.k) for m in policy.mutators],
        type_grants=[
            PolicyTypeGrant(type=t, field=f) for t, f in sorted(policy.types.grants)
        ],
    )
    return row


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    session.add_all(_to_row(p) for p in POLICIES)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    for name in (p.name for p in POLICIES):
        row = session.query(PolicyRow).filter_by(name=name).one_or_none()
        if row is not None:
            session.delete(row)
    session.commit()
