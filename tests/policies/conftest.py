# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Fixtures and helpers shared by the policy tests."""

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import update

from mora import db
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost

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


@pytest.fixture
def make_owner(
    create_owner: Callable[[dict[str, Any]], UUID],
) -> Callable[..., None]:
    """Record that `owner` (a person) owns the given org-unit or person."""

    def inner(
        owner: UUID | str,
        org_unit: UUID | str | None = None,
        person: UUID | str | None = None,
    ) -> None:
        input: dict = {"owner": str(owner), "validity": {"from": "2020-01-01"}}
        if org_unit is not None:
            input["org_unit"] = str(org_unit)
        if person is not None:
            input["person"] = str(person)
        create_owner(input)

    return inner


@pytest.fixture
def employee_update(graphapi_post: GraphAPIPost) -> Callable[[UUID | str], GQLResponse]:
    """Attempt a person edit, for a test to assert whether a policy allowed it."""

    def inner(person: UUID | str) -> GQLResponse:
        mutate_query = """
            mutation UpdateEmployee($input: EmployeeUpdateInput!) {
                employee_update(input: $input) {
                    uuid
                }
            }
        """
        return graphapi_post(
            mutate_query,
            variables={
                "input": {"uuid": str(person), "validity": {"from": "2020-01-01"}}
            },
        )

    return inner
