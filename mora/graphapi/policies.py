# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from functools import partial

from more_itertools import one
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from strawberry.dataloader import DataLoader

from mora import db
from mora.db import AsyncSession
from mora.graphapi.policy_cel import CEL

POLICY_LOADER_KEY = "policy_loader"


async def policy_rules_resolver(
    session: AsyncSession, keys: list[frozenset[str]]
) -> list[dict[tuple[str, str], list[CEL]]]:
    """The applicable rules for the caller's roles."""
    # The loader is cached per request, and the token never changes per request,
    # so we only ever get called with one set of roles
    roles = one(keys)
    query = (
        select(
            db.PolicyRule.type,
            db.PolicyRule.field,
            db.PolicyRule.condition,
        )
        .join(db.Policy)
        .where(db.Policy.active)
        .where(
            exists().where(
                db.PolicyActor.policy_fk == db.Policy.id,
                or_(
                    db.PolicyActor.kind == db.PolicyActorKind.all,
                    and_(
                        db.PolicyActor.kind == db.PolicyActorKind.role,
                        db.PolicyActor.value.in_(roles),
                    ),
                ),
            )
        )
    )
    rows = (await session.execute(query)).all()
    index: dict[tuple[str, str], list[CEL]] = defaultdict(list)
    for row in rows:
        index[(row.type, row.field)].append(row.condition)
    return [index]


def get_policy_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        POLICY_LOADER_KEY: DataLoader(load_fn=partial(policy_rules_resolver, session))
    }
