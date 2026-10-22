# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import AsyncSession
from mora.db import Collection
from mora.db import Policy
from mora.db import PolicyReadRule
from mora.db import PolicyReadRuleField
from mora.db import PolicySelector
from mora.db import PolicySelectorKind
from mora.db import add_rolebinding_rule_revision
from mora.db import current_rolebinding_rule_revision
from mora.graphapi.version import LATEST_VERSION
from mora.mapping import ADMIN

from ..conftest import BRUCE_UUID
from ..conftest import AnotherTransaction
from ..conftest import GraphAPIPost
from ..conftest import SetAuth
from ..test_events import ack_event
from ..test_events import declare_listener
from ..test_events import fetch_event

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
    "ituser.engagements.exists(e, "
    'e.job_function.uuid == "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa")'
)


@pytest.fixture
def rule(graphapi_post: GraphAPIPost, role: UUID) -> UUID:
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    assert response.data
    return UUID(response.data["rolebinding_rule_create"]["uuid"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_create_update_and_delete_rule(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    itsystem: UUID,
    role: UUID,
    rule: UUID,
    bob: UUID,
) -> None:
    """Every change writes a revision as the actor who made the change."""
    created = {
        "name": "nurses",
        "expression": NURSES,
        "active": True,
        "role": {"uuid": str(role)},
        "actor": {"uuid": str(BRUCE_UUID)},
    }
    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"uuid": str(rule), "current": created}
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
        UPDATE_RULE,
        {"input": {"uuid": str(rule), "expression": "true", "active": False}},
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
        {"uuid": str(rule), "current": updated}
    ]

    # Bob deletes the rule, which is then gone
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": str(rule)}})
    assert response.errors is None
    assert response.data == {"rolebinding_rule_delete": str(rule)}

    response = graphapi_post(READ_RULES)
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == []

    # A deleted rule cannot be changed, just like a rule that never existed
    for mutation, input in [
        (UPDATE_RULE, {"uuid": str(rule), "active": True}),
        (DELETE_RULE, {"uuid": str(rule)}),
    ]:
        response = graphapi_post(mutation, {"input": input})
        assert response.errors is not None
        assert one(response.errors)["message"] == (
            f"No rolebinding rule with UUID '{rule}'."
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_changes_send_events(graphapi_post: GraphAPIPost, rule: UUID) -> None:
    listener = declare_listener(graphapi_post, "mo", "rules", "rolebinding_rule")

    def assert_event() -> None:
        event = fetch_event(graphapi_post, listener)
        assert event is not None
        assert event["subject"] == str(rule)
        assert ack_event(graphapi_post, event["token"]).errors is None

    assert fetch_event(graphapi_post, listener) is None

    deactivate = {"input": {"uuid": str(rule), "active": False}}
    response = graphapi_post(UPDATE_RULE, deactivate)
    assert response.errors is None
    assert_event()

    response = graphapi_post(UPDATE_RULE, deactivate)
    assert response.errors is None
    assert fetch_event(graphapi_post, listener) is None

    response = graphapi_post(DELETE_RULE, {"input": {"uuid": str(rule)}})
    assert response.errors is None
    assert_event()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_filter_rules(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    role: UUID,
    ldap_itsystem: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    ldap_read = create_class(
        {
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(ldap_itsystem),
            "user_key": "ldap_read",
            "name": "LDAP Read",
            "validity": {"from": "1970-01-01"},
        }
    )

    def create_rule(input: dict[str, Any]) -> str:
        response = graphapi_post(CREATE_RULE, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["rolebinding_rule_create"]["uuid"]

    def filter_rules(filter: dict[str, Any]) -> set[str]:
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
        return {obj["uuid"] for obj in response.data["rolebinding_rules"]["objects"]}

    nurses = create_rule({"name": "nurses", "role": str(role), "expression": NURSES})
    inactive = create_rule(
        {
            "name": "inactive",
            "role": str(ldap_read),
            "expression": "true",
            "active": False,
        }
    )
    deleted = create_rule({"name": "deleted", "role": str(role), "expression": "true"})
    response = graphapi_post(DELETE_RULE, {"input": {"uuid": deleted}})
    assert response.errors is None

    assert filter_rules({}) == {nurses, inactive}
    assert filter_rules({"uuids": [inactive]}) == {inactive}
    assert filter_rules({"names": ["nurses"]}) == {nurses}
    assert filter_rules({"roles": [str(role)]}) == {nurses}
    assert filter_rules({"roles": [str(ldap_read)]}) == {inactive}
    assert filter_rules({"active": False}) == {inactive}

    # Deleted rules never match
    assert filter_rules({"uuids": [deleted]}) == set()
    assert filter_rules({"names": ["deleted"]}) == set()


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
            "size(ituser.engagements) == 0 &&",
            "Syntax error: mismatched input",
        ),
        (
            'employee.uuid == "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa"',
            "undeclared reference to 'employee.uuid'",
        ),
        (
            "has(ituser.engagment)",
            "undefined field 'engagment' not found in struct 'mo.rolebinding.ITUser'",
        ),
        (
            "ituser.engagements",
            "the expression must be true or false, but is "
            "LIST<mo.rolebinding.Engagement>",
        ),
        (
            "ituser.uuid",
            "the expression must be true or false, but is STRING",
        ),
    ],
)
def test_reject_unrunnable_expression(
    graphapi_post: GraphAPIPost, rule: UUID, role: UUID, expression: str, message: str
) -> None:
    # fails on create:
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": expression}},
    )
    assert response.errors is not None
    assert message in one(response.errors)["message"]

    # fails on update:
    response = graphapi_post(
        UPDATE_RULE, {"input": {"uuid": str(rule), "expression": expression}}
    )
    assert response.errors is not None
    assert message in one(response.errors)["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_reject_unknown_role(graphapi_post: GraphAPIPost, rule: UUID) -> None:
    unknown = uuid4()

    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(unknown), "expression": NURSES}},
    )
    assert response.errors is not None
    assert one(response.errors)["message"] == f"Role '{unknown}' does not exist."

    response = graphapi_post(
        UPDATE_RULE, {"input": {"uuid": str(rule), "role": str(unknown)}}
    )
    assert response.errors is not None
    assert one(response.errors)["message"] == f"Role '{unknown}' does not exist."


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
    rule: UUID,
    bob: UUID,
    change: dict[str, Any],
) -> None:
    set_auth(ADMIN, bob)
    response = graphapi_post(UPDATE_RULE, {"input": {"uuid": str(rule), **change}})
    assert response.errors is None

    # Bob wrote nothing, so the current revision is still Bruce's
    response = graphapi_post(READ_RULES, {"filter": {"uuids": [str(rule)]}})
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {
            "uuid": str(rule),
            "current": {
                "name": "nurses",
                "expression": NURSES,
                "active": True,
                "role": {"uuid": str(role)},
                "actor": {"uuid": str(BRUCE_UUID)},
            },
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_reject_concurrent_write(
    graphapi_post: GraphAPIPost, another_transaction: AnotherTransaction, rule: UUID
) -> None:
    """A write based on a revision that is no longer current is rejected."""
    async with another_transaction() as (_, session):
        current = await current_rolebinding_rule_revision(session, str(rule))
        assert current is not None

        # Someone else changes the rule while our transaction is running
        response = graphapi_post(
            UPDATE_RULE, {"input": {"uuid": str(rule), "active": False}}
        )
        assert response.errors is None

        with pytest.raises(ValueError, match="was changed concurrently"):
            await add_rolebinding_rule_revision(
                session, current, actor=current.actor, active=True
            )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_a_reader_reads_the_fields_of_a_rule(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, rule: UUID
) -> None:
    """The seeded Reader policy grants a reader the fields of rules."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(
        """
        query {
            rolebinding_rules {
                objects {
                    uuid
                    created_at
                    current { created_at name expression active role { uuid } }
                }
            }
        }
        """
    )

    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {
            "uuid": str(rule),
            "created_at": ANY,
            "current": {
                "created_at": ANY,
                "name": "nurses",
                "expression": NURSES,
                "active": True,
                "role": {"uuid": ANY},
            },
        }
    ]


@pytest.mark.integration_test
async def test_the_fields_of_a_revision_are_granted_apart_from_the_rule(
    empty_db: AsyncSession, set_auth: SetAuth, graphapi_post: GraphAPIPost, role: UUID
) -> None:
    """Being granted the current revision of a rule grants none of its fields."""
    response = graphapi_post(
        CREATE_RULE,
        {"input": {"name": "nurses", "role": str(role), "expression": NURSES}},
    )
    assert response.errors is None
    empty_db.add(
        Policy(
            name="Rule Auditor",
            description="Allows rule auditors to read the names of rules",
            active=True,
            selectors=[PolicySelector(kind=PolicySelectorKind.role, value="auditor")],
            read_rules=[
                PolicyReadRule(
                    collection=collection,
                    condition="true",
                    graphql_version=LATEST_VERSION,
                    fields=[PolicyReadRuleField(field=field) for field in fields],
                )
                for collection, fields in [
                    (Collection.RolebindingRule, ["uuid", "current"]),
                    (Collection.RolebindingRuleRevision, ["name"]),
                ]
            ],
        )
    )
    await empty_db.commit()
    set_auth({"auditor"}, uuid4())

    response = graphapi_post(
        """
        query {
            rolebinding_rules {
                objects { uuid current { name expression } }
            }
        }
        """
    )

    # The denied field is non-null, so the null propagates to the root
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["rolebinding_rules", "objects", 0, "current", "expression"]
