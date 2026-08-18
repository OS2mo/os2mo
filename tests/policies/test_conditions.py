# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of rule conditions (CEL)."""

from uuid import UUID

import pytest
from more_itertools import one

from mora.db import AsyncSession
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted
from tests.policies.conftest import CreatePolicy
from tests.policies.helpers import assert_access


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("username,granted", [("bruce", True), ("alice", False)])
async def test_condition_gates_the_rule(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    username: str,
    granted: bool,
) -> None:
    """A rule applies only while its condition holds."""
    # The policy applies to the "conditional-role" role either way, but only
    # grants employees to the caller its condition names
    await create_policy(
        "conditional",
        actors=[("role", "conditional-role")],
        rules=[("Query", "employees", 'token.preferred_username == "bruce"')],
    )
    set_auth(role="conditional-role", preferred_username=username)
    assert_access(graphapi_post("query { employees { objects { uuid } } }"), granted)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_unconditional_rule_grants_despite_false_condition(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
) -> None:
    # Two rules for the same field: one with a false condition, one
    # unconditional. The unconditional one grants access regardless
    await create_policy(
        "conditional",
        actors=[("role", "conditional-role")],
        rules=[("Query", "employees", "false"), ("Query", "employees")],
    )
    set_auth(role="conditional-role")
    assert_granted(graphapi_post("query { employees { objects { uuid } } }"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_condition_fails_hard_when_not_boolean(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
) -> None:
    # A condition that errors (here: a misspelt field) must not grant access,
    # nor silently deny; it surfaces as an error
    await create_policy(
        "conditional",
        actors=[("role", "reader")],
        rules=[("Query", "employees", "token.misspelt.field")],
    )
    set_auth(role="reader")
    response = graphapi_post("query { employees { objects { uuid } } }")
    assert response.errors is not None
    assert one(response.errors)["message"] == (
        "CEL condition 'token.misspelt.field' result is not boolean: "
        'NOT_FOUND: Key not found in map : "misspelt"'
    )


@pytest.mark.integration_test
async def test_condition_reads_the_mutator_input(
    empty_db: AsyncSession,
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    alice: UUID,
    bob: UUID,
) -> None:
    """A condition may read the arguments the call carries, through `args`."""
    await create_policy(
        "self-service",
        actors=[("all", "")],
        rules=[("Mutation", "employee_update", "args.input.uuid == token.uuid")],
    )
    set_auth(user_uuid=alice)

    def update(person: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateEmployee($input: EmployeeUpdateInput!) {
                employee_update(input: $input) {
                    uuid
                }
            }
            """,
            variables={
                "input": {"uuid": str(person), "validity": {"from": "2020-01-01"}}
            },
        )

    # Alice is the caller, so the input naming her matches the condition
    assert_granted(update(alice))
    assert_denied(update(bob))
