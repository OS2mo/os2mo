# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from more_itertools import one

from mora.graphapi.rolebinding_rules import add_revision
from mora.graphapi.rolebinding_rules import current_revision
from mora.mapping import ADMIN

from ..conftest import AnotherTransaction
from ..conftest import GraphAPIPost
from ..conftest import SetAuth

CREATE_RULE = """
    mutation CreateRule($input: RolebindingRuleCreateInput!) {
        rolebinding_rule_create(input: $input) { uuid }
    }
"""
UPDATE_RULE = """
    mutation UpdateRule($input: RolebindingRuleUpdateInput!) {
        rolebinding_rule_update(input: $input) { uuid }
    }
"""
DELETE_RULE = """
    mutation DeleteRule($input: RolebindingRuleDeleteInput!) {
        rolebinding_rule_delete(input: $input)
    }
"""
READ_RULES = """
    query ReadRules($filter: RolebindingRuleFilter) {
        rolebinding_rules(filter: $filter) {
            objects {
                uuid
                current {
                    name
                    expression
                    active
                    role { uuid }
                    actor { uuid }
                }
            }
        }
    }
"""

NURSES = (
    "ituser.engagement != null && "
    'ituser.engagement.job_function.uuid == "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa"'
)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_create_update_and_delete_rule(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    itsystem: UUID,
    role: UUID,
    alice: UUID,
    bob: UUID,
) -> None:
    """Every change writes a revision as the actor who made the change."""
    # Alice creates a rule, which is active by default
    set_auth(ADMIN, alice)
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = response.data["rolebinding_rule_create"]["uuid"]

    created = {
        "name": "nurses",
        "expression": NURSES,
        "active": True,
        "role": {"uuid": str(role)},
        "actor": {"uuid": str(alice)},
    }
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": created}
    ]

    # The role resolves to the class, and through the class to the IT-system
    response = graphapi_post(
        """
        query ReadRole {
            rolebinding_rules {
                objects { current { role { current { name it_system_uuid } } } }
            }
        }
        """
    )
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {
            "current": {
                "role": {"current": {"name": "Read", "it_system_uuid": str(itsystem)}}
            }
        }
    ]

    # Bob changes the expression and deactivates the rule. The name and the
    # role carry over from the previous revision.
    set_auth(ADMIN, bob)
    response = graphapi_post(
        UPDATE_RULE, {"input": {"uuid": uuid, "expression": "true", "active": False}}
    )
    assert response.errors is None

    updated = {
        **created,
        "expression": "true",
        "active": False,
        "actor": {"uuid": str(bob)},
    }
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": updated}
    ]

    # Bob deletes the rule, which is then gone
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": uuid}})
    assert response.errors is None
    assert response.data == {"rolebinding_rule_delete": uuid}

    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == []

    # A deleted rule cannot be changed, just like a rule that never existed
    for mutation, input in [
        (UPDATE_RULE, {"uuid": uuid, "active": True}),
        (DELETE_RULE, {"uuid": uuid}),
    ]:
        response = graphapi_post(mutation, {"input": input})
        assert response.errors is not None
        assert one(response.errors)["message"] == (
            f"No rolebinding rule with UUID '{uuid}'."
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, {"nurses", "inactive"}),
        ({"uuids": ["inactive"]}, {"inactive"}),
        ({"names": ["nurses"]}, {"nurses"}),
        ({"roles": ["read"]}, {"nurses"}),
        ({"roles": ["ldap_read"]}, {"inactive"}),
        ({"active": False}, {"inactive"}),
        # Deleted rules never match
        ({"uuids": ["deleted"]}, set()),
        ({"names": ["deleted"]}, set()),
    ],
)
def test_filter_rules(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    role: UUID,
    ldap_itsystem: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Filters refer to rules and roles by name, as their UUIDs are random."""
    ldap_read = create_class(
        {
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(ldap_itsystem),
            "user_key": "ldap_read",
            "name": "LDAP Read",
            "validity": {"from": "1970-01-01"},
        }
    )
    roles = {"read": str(role), "ldap_read": str(ldap_read)}

    uuids = {}
    for input in [
        {"name": "nurses", "role": roles["read"], "expression": NURSES},
        {
            "name": "inactive",
            "role": roles["ldap_read"],
            "expression": "true",
            "active": False,
        },
        {"name": "deleted", "role": roles["read"], "expression": "true"},
    ]:
        response = graphapi_post(CREATE_RULE, {"input": input})
        assert response.errors is None
        assert response.data
        uuids[input["name"]] = response.data["rolebinding_rule_create"]["uuid"]
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": uuids["deleted"]}})
    assert response.errors is None

    if "uuids" in filter:
        filter = {**filter, "uuids": [uuids[name] for name in filter["uuids"]]}
    if "roles" in filter:
        filter = {**filter, "roles": [roles[name] for name in filter["roles"]]}
    response = graphapi_post(
        """
        query FilterRules($filter: RolebindingRuleFilter) {
            rolebinding_rules(filter: $filter) { objects { uuid } }
        }
        """,
        {"filter": filter},
    )
    assert response.errors is None
    assert response.data
    found = {obj["uuid"] for obj in response.data["rolebinding_rules"]["objects"]}
    assert found == {uuids[name] for name in expected}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "expression,message",
    [
        (
            "",
            "the expression is empty",
        ),
        (
            "ituser.person != null &&",
            "Syntax error: mismatched input",
        ),
        (
            'employee.uuid == "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa"',
            "undeclared reference to 'employee.uuid'",
        ),
        (
            "ituser.engagment != null",
            'Key not found in map : "engagment"',
        ),
        (
            "ituser.person",
            "the expression must be true or false, but is dyn",
        ),
    ],
)
def test_reject_unrunnable_expression(
    graphapi_post: GraphAPIPost, role: UUID, expression: str, message: str
) -> None:
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": expression}},
    )
    assert response.errors is not None
    assert message in one(response.errors)["message"]

    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = response.data["rolebinding_rule_create"]["uuid"]

    response = graphapi_post(
        UPDATE_RULE, {"input": {"uuid": uuid, "expression": expression}}
    )
    assert response.errors is not None
    assert message in one(response.errors)["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "change,message",
    [
        (
            {"expression": "ituser.engagment != null"},
            'Key not found in map : "engagment"',
        ),
        ({"expression": None}, "Fields cannot be null: expression."),
    ],
)
def test_rejected_update_writes_no_revision(
    graphapi_post: GraphAPIPost, role: UUID, change: dict[str, Any], message: str
) -> None:
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = response.data["rolebinding_rule_create"]["uuid"]

    response = graphapi_post(UPDATE_RULE, {"input": {"uuid": uuid, **change}})
    assert response.errors is not None
    assert message in one(response.errors)["message"]

    response = graphapi_post(READ_RULES, {"filter": {"uuids": [uuid]}})
    assert response.errors is None
    assert response.data
    revision = {
        "name": "nurses",
        "expression": NURSES,
        "active": True,
        "role": {"uuid": str(role)},
        "actor": {"uuid": ANY},
    }
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": revision}
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "change",
    [
        {},
        {"name": "nurses"},
        {"expression": NURSES, "active": True},
    ],
)
def test_noop_update_writes_no_revision(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    role: UUID,
    alice: UUID,
    bob: UUID,
    change: dict[str, Any],
) -> None:
    set_auth(ADMIN, alice)
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = response.data["rolebinding_rule_create"]["uuid"]

    set_auth(ADMIN, bob)
    response = graphapi_post(UPDATE_RULE, {"input": {"uuid": uuid, **change}})
    assert response.errors is None

    # Bob wrote nothing, so the current revision is still Alice's
    response = graphapi_post(READ_RULES, {"filter": {"uuids": [uuid]}})
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {
            "uuid": uuid,
            "current": {
                "name": "nurses",
                "expression": NURSES,
                "active": True,
                "role": {"uuid": str(role)},
                "actor": {"uuid": str(alice)},
            },
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_reject_concurrent_write(
    graphapi_post: GraphAPIPost, another_transaction: AnotherTransaction, role: UUID
) -> None:
    """A write based on a revision that is no longer current is rejected."""
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = UUID(response.data["rolebinding_rule_create"]["uuid"])

    async with another_transaction() as (_, session):
        current = await current_revision(session, uuid)
        assert current is not None

        # Someone else changes the rule while our transaction is running
        response = graphapi_post(
            UPDATE_RULE, {"input": {"uuid": str(uuid), "active": False}}
        )
        assert response.errors is None

        with pytest.raises(ValueError, match="was changed concurrently"):
            await add_revision(
                session,
                uuid,
                current,
                name=current.name,
                role=current.role,
                expression=current.expression,
                active=True,
            )
