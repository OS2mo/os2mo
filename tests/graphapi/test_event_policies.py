# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of event namespaces and listeners are guarded by read policies."""

from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import Collection
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules


@pytest.fixture
def listener(graphapi_post: GraphAPIPost) -> UUID:
    """A listener in a namespace of its own, declared by an admin."""
    response = graphapi_post(
        """
        mutation {
          event_namespace_declare(input: { name: "ns", public: false }) { name }
          event_listener_declare(
            input: { namespace: "ns", user_key: "listener", routing_key: "key" }
          ) { uuid }
        }
        """
    )
    assert response.errors is None
    assert response.data
    return UUID(response.data["event_listener_declare"]["uuid"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_reads_the_fields_of_a_listener(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, listener: UUID
) -> None:
    """The seeded Reader policy grants a reader what the role used to."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          event_listeners(filter: { namespaces: { names: ["ns"] } }) {
            objects { uuid user_key routing_key }
          }
        }
        """
    )

    assert response.errors is None
    assert response.data == {
        "event_listeners": {
            "objects": [
                {"uuid": str(listener), "user_key": "listener", "routing_key": "key"}
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "listener")
async def test_a_listener_field_no_rule_grants_is_denied(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_rules: SetRules
) -> None:
    """A field of a listener no rule grants is denied where it is read."""
    await set_rules("policy_reader", Collection.Listener, {"uuid", "user_key"})
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          event_listeners(filter: { namespaces: { names: ["ns"] } }) {
            objects { uuid user_key routing_key }
          }
        }
        """
    )

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["event_listeners", "objects", 0, "routing_key"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "listener")
async def test_a_reader_reads_the_fields_of_a_namespace(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    """The seeded Reader policy grants a reader what the role used to."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          event_namespaces(filter: { names: ["ns"] }) {
            objects { name public listeners { user_key } }
          }
        }
        """
    )

    assert response.errors is None
    assert response.data == {
        "event_namespaces": {
            "objects": [
                {"name": "ns", "public": False, "listeners": [{"user_key": "listener"}]}
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "listener")
async def test_a_namespace_field_no_rule_grants_is_denied(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_rules: SetRules
) -> None:
    """A field of a namespace no rule grants is denied where it is read."""
    await set_rules("policy_reader", Collection.Namespace, {"name"})
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          event_namespaces(filter: { names: ["ns"] }) { objects { name public } }
        }
        """
    )

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["event_namespaces", "objects", 0, "public"]
