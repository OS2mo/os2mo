# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of event namespaces, listeners and events are guarded by read policies."""

from unittest.mock import ANY
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import Collection
from mora.db.events import DEFAULT_PRIORITY
from tests.conftest import BRUCE_UUID
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules
from tests.conftest import SetWriteRules


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


@pytest.fixture
def event(graphapi_post: GraphAPIPost, listener: UUID) -> None:
    """An event for the listener, sent by the admin owning its namespace."""
    response = graphapi_post(
        """
        mutation {
          event_send(input: { namespace: "ns", routing_key: "key", subject: "subject" })
        }
        """
    )
    assert response.errors is None


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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "event")
async def test_a_reader_reads_the_fields_of_an_event(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, listener: UUID
) -> None:
    """Only the owner of a listener sees its events, so the reader owns it."""
    set_auth({"reader"}, BRUCE_UUID)

    response = graphapi_post(
        """
        query {
          events {
            objects { subject priority silenced created_at listener { uuid } }
          }
        }
        """
    )

    assert response.errors is None
    assert response.data == {
        "events": {
            "objects": [
                {
                    "subject": "subject",
                    "priority": DEFAULT_PRIORITY,
                    "silenced": False,
                    "created_at": ANY,
                    "listener": {"uuid": str(listener)},
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "event")
async def test_a_reader_reads_the_fields_of_a_rerun_event(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_write_rules: SetWriteRules
) -> None:
    """A reader reads the fields of the events a rerun hands back."""
    await set_write_rules(role="rerunner", mutator="event_rerun", condition="true")
    set_auth({"rerunner", "reader"}, uuid4())

    response = graphapi_post("mutation { event_rerun(input: {}) { subject } }")

    assert response.errors is None
    assert response.data == {"event_rerun": [{"subject": "subject"}]}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "event")
async def test_an_event_field_no_rule_grants_is_denied(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_rules: SetRules
) -> None:
    """A field of an event no rule grants is denied where it is read."""
    await set_rules("policy_reader", Collection.FullEvent, {"subject"})
    set_auth({"policy_reader"}, BRUCE_UUID)

    response = graphapi_post("query { events { objects { subject priority } } }")

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["events", "objects", 0, "priority"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "event")
async def test_an_event_gets_the_fields_of_the_rules_matching_it(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    """An event is matched by its filter, reaching into the namespace of its listener."""
    response = graphapi_post(
        """
        mutation SendEvent($namespace: String!, $routing_key: String!) {
          event_namespace_declare(input: { name: $namespace, public: false }) { name }
          event_listener_declare(
            input: { namespace: $namespace, user_key: "listener", routing_key: $routing_key }
          ) { uuid }
          event_send(
            input: { namespace: $namespace, routing_key: $routing_key, subject: "other" }
          )
        }
        """,
        variables={"namespace": "other", "routing_key": "key"},
    )
    assert response.errors is None
    response = graphapi_post(
        """
        mutation Declare($uuid: UUID!, $state: PolicyStateInput) {
          policy_declare(uuid: $uuid, state: $state) { uuid }
        }
        """,
        variables={
            "uuid": str(uuid4()),
            "state": {
                "name": "Event Auditor",
                "selectors": [{"kind": "role", "value": "event_auditor"}],
                "read_rules": [
                    {
                        "collection": "FullEvent",
                        "fields": ["subject"],
                        "condition": '{"listeners": {"namespaces": {"names": ["ns"]}}}',
                        "graphql_version": "VERSION_30",
                    }
                ],
            },
        },
    )
    assert response.errors is None
    set_auth({"event_auditor"}, BRUCE_UUID)

    response = graphapi_post(
        'query { events(filter: { subjects: ["subject"] }) { objects { subject } } }'
    )
    assert response.errors is None
    assert response.data == {"events": {"objects": [{"subject": "subject"}]}}

    response = graphapi_post(
        'query { events(filter: { subjects: ["other"] }) { objects { subject } } }'
    )
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["events", "objects", 0, "subject"]
