# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Fixtures and helpers shared by the policy tests."""

from collections.abc import Awaitable
from collections.abc import Callable

import pytest
from sqlalchemy import update

from mora import db

# (type, field[, condition[, filter]])
Rule = tuple[str, str] | tuple[str, str, str] | tuple[str, str, str, str]
CreatePolicy = Callable[..., Awaitable[None]]


@pytest.fixture
def create_policy(raw_session: db.AsyncSession) -> CreatePolicy:
    def create_rule(
        type: str, field: str, condition: str = "", filter: str = ""
    ) -> db.PolicyRule:
        return db.PolicyRule(type=type, field=field, condition=condition, filter=filter)

    async def inner(
        name: str,
        actors: list[tuple[str, str]],
        rules: list[Rule],
        active: bool = True,
    ) -> None:
        """Insert a policy directly in the database."""
        policy = db.Policy(name=name, active=active)
        policy.actors = [
            db.PolicyActor(kind=db.PolicyActorKind(kind), value=value)
            for kind, value in actors
        ]
        policy.rules = [create_rule(*rule) for rule in rules]
        raw_session.add(policy)
        await raw_session.commit()

    return inner


@pytest.fixture
def deactivate_policy(raw_session: db.AsyncSession) -> Callable[[str], Awaitable[None]]:
    """Turn a built-in policy off, so a test may put its own rules in its place."""

    async def inner(name: str) -> None:
        await raw_session.execute(
            update(db.Policy).where(db.Policy.name == name).values(active=False)
        )
        await raw_session.commit()

    return inner


DEFAULT_POLICIES = {"Public", "Introspection", "RBAC", "Owner", "Policy Administrator"}
