# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of how policy rules match a (type, field)."""

import pytest

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted
from tests.policies.conftest import CreatePolicy
from tests.policies.helpers import assert_access


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_denies_gated_field_without_grant(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """A field granted by no policy is rejected."""
    set_auth(role="nobody")
    assert_denied(graphapi_post("query { org_units { objects { uuid } } }"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_grants_gated_field_by_role(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
) -> None:
    """A policy grants its (type, field) rules to actors matching by role."""
    await create_policy(
        "unit-reader",
        actors=[("role", "reader")],
        rules=[("Query", "org_units")],
    )
    set_auth(role="reader")

    assert_granted(graphapi_post("query { org_units { objects { uuid } } }"))
    # The role was not granted the employees collection
    assert_denied(graphapi_post("query { employees { objects { uuid } } }"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("active", [True, False])
async def test_policy_grants_only_when_active(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    active: bool,
) -> None:
    """A policy only grants access while active."""
    await create_policy(
        "unit-reader",
        actors=[("role", "reader")],
        rules=[("Query", "org_units")],
        active=active,
    )
    set_auth(role="reader")
    assert_access(graphapi_post("query { org_units { objects { uuid } } }"), active)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "rule,reaches_other_fields",
    [
        # A field wildcard covers every field of the type it names, a type
        # wildcard only the field it names, and both wildcards everything
        (("Query", "*"), True),
        (("*", "org_units"), False),
        (("*", "*"), True),
    ],
)
async def test_wildcard_rule(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    rule: tuple[str, str],
    reaches_other_fields: bool,
) -> None:
    """A rule may use the wildcard "*" for either component, or for both."""
    await create_policy(
        "wildcard-reader",
        actors=[("role", "reader")],
        rules=[rule],
    )
    set_auth(role="reader")

    # Every one of them grants the org-units query the rule names
    assert_granted(graphapi_post("query { org_units { objects { uuid } } }"))
    # Only a field wildcard reaches past it, to the rest of the Query type
    assert_access(
        graphapi_post("query { employees { objects { uuid } } }"), reaches_other_fields
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_all_actor_policy_grants_everyone(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
) -> None:
    """An "all" actor matches every token, whatever its roles."""
    await create_policy(
        "everyone-reader",
        actors=[("all", "")],
        rules=[("Query", "employees")],
    )
    set_auth(role="nobody")
    assert_granted(graphapi_post("query { employees { objects { uuid } } }"))
