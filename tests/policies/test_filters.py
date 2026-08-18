# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of rule entity filters."""

from collections.abc import Callable
from textwrap import dedent
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import AsyncSession
from tests.conftest import GQLResponse
from tests.conftest import SetAuth
from tests.policies.conftest import CreatePolicy
from tests.policies.helpers import assert_access
from tests.policies.helpers import assert_denied
from tests.policies.helpers import assert_granted


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "filter,filter_matches",
    [
        # A rule without a filter applies to every entity
        ("", True),
        # An employee exists with the caller's uuid, so this filter matches
        ('[{"collection": "employee", "filter": {"uuids": [token.uuid]}}]', True),
        # No employee carries this user-key, so this filter matches nothing
        (
            '[{"collection": "employee", "filter": {"user_keys": ["nonexistent"]}}]',
            False,
        ),
    ],
)
@pytest.mark.parametrize(
    "condition,condition_holds",
    [("", True), ("true", True), ("false", False)],
)
async def test_rule_needs_both_its_condition_and_its_filter(
    empty_db: AsyncSession,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    alice: UUID,
    employee_update: Callable[[UUID | str], GQLResponse],
    condition: str,
    condition_holds: bool,
    filter: str,
    filter_matches: bool,
) -> None:
    """A rule grants only if its condition and its filter both hold."""
    await create_policy(
        "conditional-filter",
        actors=[("all", "")],
        rules=[("Mutation", "employee_update", condition, filter)],
    )
    set_auth(user_uuid=alice)

    assert_access(employee_update(alice), condition_holds and filter_matches)


@pytest.mark.integration_test
async def test_rule_filter_requires_owning_the_named_entity(
    empty_db: AsyncSession,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    alice: UUID,
    bob: UUID,
    create_owner: Callable[[dict[str, Any]], UUID],
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    create_owner(
        {
            "owner": str(alice),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )

    await create_policy(
        "person-owner",
        actors=[("all", "")],
        rules=[
            (
                "Mutation",
                "employee_update",
                "",
                # The caller must own the person being edited
                """
                [args.input].map(i, {
                    "collection": "employee",
                    "filter": {
                        "uuids": [i.uuid],
                        "owner": {"owner": {"uuids": [token.uuid]}}
                    }
                })
                """,
            )
        ],
    )
    set_auth(user_uuid=alice)

    # Alice owns Bob, so she may edit him
    assert_granted(employee_update(bob))
    # Nobody owns Alice, so she may not edit herself
    assert_denied(employee_update(alice))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_rule_filter_fails_hard_when_cel_errors(
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    """A filter erroring in CEL surfaces the error, and grants nothing."""
    await create_policy(
        "erroring-filter",
        actors=[("role", "editor")],
        rules=[("Mutation", "employee_update", "", "token.misspelt.field")],
    )
    set_auth(role="editor")

    response = employee_update(uuid4())
    assert response.errors is not None
    assert one(response.errors)["message"] == (
        "failed to evaluate CEL filter 'token.misspelt.field': "
        'NOT_FOUND: Key not found in map : "misspelt"'
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_rule_filter_fails_hard_when_not_check_specs(
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    """A filter yielding anything but check-specs surfaces the model's error."""
    await create_policy(
        "not-check-specs",
        actors=[("role", "editor")],
        rules=[("Mutation", "employee_update", "", '"not-a-check-spec"')],
    )
    set_auth(role="editor")

    response = employee_update(uuid4())
    assert response.errors is not None
    expected = dedent(
        """
        1 validation error for ParsingModel[list[mora.graphapi.policies.CheckSpec]]
        __root__
          value is not a valid list (type=type_error.list)
        """
    ).strip()
    assert one(response.errors)["message"] == expected
