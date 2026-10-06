# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from more_itertools import one

from mora.mapping import ADMIN

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
        rolebinding_rule_delete(input: $input) { uuid }
    }
"""
READ_RULES = """
    query ReadRules($filter: RolebindingRuleFilter) {
        rolebinding_rules(filter: $filter) {
            objects {
                uuid
                current { ...Revision }
                history { ...Revision }
            }
        }
    }

    fragment Revision on RolebindingRuleRevision {
        user_key
        expression
        active
        deleted
        role { uuid }
        actor { uuid }
    }
"""

NURSES = (
    "ituser.engagement != null && "
    'ituser.engagement.job_function.uuid == "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa"'
)

ALICE = UUID("8a3a8c3e-5a8e-4b1e-9f53-0d0b8f7d6a11")
BOB = UUID("1f0c2b7d-3e4a-4c59-8d6e-7a9b0c1d2e33")


@pytest.fixture
def itsystem(create_itsystem: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def role(
    role_facet: UUID, itsystem: UUID, create_class: Callable[[dict[str, Any]], UUID]
) -> UUID:
    return create_class(
        {
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem),
            "user_key": "ad_read",
            "name": "AD Read",
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_create_update_and_delete_rule(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, itsystem: UUID, role: UUID
) -> None:
    """Every change writes a revision as the actor who made the change. Deleting
    a rule keeps the rule's history."""
    # Alice creates a rule, which is active by default
    set_auth(ADMIN, ALICE)
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"user_key": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    uuid = response.data["rolebinding_rule_create"]["uuid"]

    created = {
        "user_key": "nurses",
        "expression": NURSES,
        "active": True,
        "deleted": False,
        "role": {"uuid": str(role)},
        "actor": {"uuid": str(ALICE)},
    }
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": created, "history": [created]}
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
                "role": {
                    "current": {"name": "AD Read", "it_system_uuid": str(itsystem)}
                }
            }
        }
    ]

    # Bob changes the expression and deactivates the rule. The user-key and the
    # role carry over from the previous revision.
    set_auth(ADMIN, BOB)
    response = graphapi_post(
        UPDATE_RULE, {"input": {"uuid": uuid, "expression": "true", "active": False}}
    )
    assert response.errors is None

    updated = {
        **created,
        "expression": "true",
        "active": False,
        "actor": {"uuid": str(BOB)},
    }
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": updated, "history": [created, updated]}
    ]

    # Bob deletes the rule. The rule has no current revision any more, but
    # the history remains.
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": uuid}})
    assert response.errors is None

    deleted = {**updated, "deleted": True}
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": None, "history": [created, updated, deleted]}
    ]

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
def test_filter_rules(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    role: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    sap = create_itsystem(
        {"user_key": "SAP", "name": "SAP", "validity": {"from": "1970-01-01"}}
    )
    sap_read = create_class(
        {
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(sap),
            "user_key": "sap_read",
            "name": "SAP Read",
            "validity": {"from": "1970-01-01"},
        }
    )

    uuids = {}
    for input in [
        {"user_key": "nurses", "role": str(role), "expression": NURSES},
        {
            "user_key": "inactive",
            "role": str(sap_read),
            "expression": "true",
            "active": False,
        },
        {"user_key": "deleted", "role": str(role), "expression": "true"},
    ]:
        response = graphapi_post(CREATE_RULE, {"input": input})
        assert response.errors is None
        assert response.data
        uuids[input["user_key"]] = response.data["rolebinding_rule_create"]["uuid"]
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": uuids["deleted"]}})
    assert response.errors is None

    for filter, expected in [
        ({}, {"nurses", "inactive", "deleted"}),
        ({"uuids": [uuids["inactive"]]}, {"inactive"}),
        ({"user_keys": ["nurses"]}, {"nurses"}),
        ({"roles": [str(role)]}, {"nurses"}),
        ({"roles": [str(sap_read)]}, {"inactive"}),
        ({"active": False}, {"inactive"}),
        # Filters on contents read the current revision, which a deleted rule
        # does not have
        ({"user_keys": ["deleted"]}, set()),
        ({"deleted": True}, {"deleted"}),
        ({"deleted": False}, {"nurses", "inactive"}),
    ]:
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
        assert found == {uuids[user_key] for user_key in expected}, filter


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
        {"input": {"user_key": "nurses", "role": str(role), "expression": expression}},
    )
    assert response.errors is not None
    assert message in one(response.errors)["message"]

    response = graphapi_post(
        CREATE_RULE,
        {"input": {"user_key": "nurses", "role": str(role), "expression": NURSES}},
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
        ({}, "Nothing to update."),
    ],
)
def test_rejected_update_writes_no_revision(
    graphapi_post: GraphAPIPost, role: UUID, change: dict[str, Any], message: str
) -> None:
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"user_key": "nurses", "role": str(role), "expression": NURSES}},
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
        "user_key": "nurses",
        "expression": NURSES,
        "active": True,
        "deleted": False,
        "role": {"uuid": str(role)},
        "actor": {"uuid": ANY},
    }
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": uuid, "current": revision, "history": [revision]}
    ]
