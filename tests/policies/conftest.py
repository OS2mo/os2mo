# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Fixtures and helpers shared by the policy tests."""

from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

import pytest

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
