# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from unittest.mock import ANY
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from mora.db.events import DEFAULT_PRIORITY
from mora.mapping import ADMIN
from more_itertools import one

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

DEFAULT_TEST_NS = "ns"


def declare_namespace(
    graphapi_post: GraphAPIPost, name: str, public: bool = False
) -> GQLResponse:
    query = """
      mutation DeclareNS($name: String!, $public: Boolean!) {
        event_namespace_declare(input: { name: $name, public: $public }) {
          name
          public
        }
      }
    """
    return graphapi_post(query, variables={"name": name, "public": public})


def delete_namespace(graphapi_post: GraphAPIPost, name: str) -> None:
    query = """
      mutation DeleteNS($name: String!) {
        event_namespace_delete(input: { name: $name })
      }
    """
    response = graphapi_post(query, variables={"name": name})
    assert response.errors is None


def declare_listener_raw(
    graphapi_post: GraphAPIPost, namespace: str, user_key: str, routing_key: str
) -> GQLResponse:
    query = """
      mutation DeclareListener($namespace: String!, $user_key: String!, $routing_key: String!) {
        event_listener_declare(
          input: { namespace: $namespace, user_key: $user_key, routing_key: $routing_key }
        ) {
          uuid
          owner
        }
      }
    """
    return graphapi_post(
        query,
        variables={
            "namespace": namespace,
            "user_key": user_key,
            "routing_key": routing_key,
        },
    )


def declare_listener(
    graphapi_post: GraphAPIPost, namespace: str, user_key: str, routing_key: str
) -> UUID:
    response = declare_listener_raw(graphapi_post, namespace, user_key, routing_key)
    assert response.errors is None
    assert response.data
    return UUID(response.data["event_listener_declare"]["uuid"])


def send_event(
    graphapi_post: GraphAPIPost,
    namespace: str,
    routing_key: str,
    subject: str,
    priority: int = DEFAULT_PRIORITY,
) -> GQLResponse:
    query = """
      mutation SendEvents($namespace: String!, $routing_key: String!, $subject: String!, $priority: Int) {
        event_send(
          input: {
            namespace: $namespace
            routing_key: $routing_key
            subject: $subject
            priority: $priority
          }
        )
      }
    """
    response = graphapi_post(
        query,
        variables={
            "namespace": namespace,
            "routing_key": routing_key,
            "subject": subject,
            "priority": priority,
        },
    )
    return response


def fetch_event(
    graphapi_post: GraphAPIPost, listener_uuid: UUID
) -> dict[str, Any] | None:
    query = """
      query FetchEvent($listener_uuid: UUID!) {
        event_fetch(filter: { listener: $listener_uuid }) {
          subject
          priority
          token
        }
      }
    """
    response = graphapi_post(query, variables={"listener_uuid": str(listener_uuid)})
    assert response.errors is None
    assert response.data
    return response.data["event_fetch"]


def ack_event(graphapi_post: GraphAPIPost, token: str) -> GQLResponse:
    query = """
      mutation Ack($token: EventToken!) {
        event_acknowledge(
          input: {token: $token}
        )
      }
    """
    response = graphapi_post(query, variables={"token": token})
    return response


def get_namespaces(
    graphapi_post: GraphAPIPost, filter: dict | None = None
) -> list[dict[str, Any]]:
    query = """
      query GetNamespaces($filter: NamespaceFilter!) {
        event_namespaces(filter: $filter) {
          objects {
            name
            owner
            public
          }
        }
      }
    """
    if filter is None:
        filter = {}
    response = graphapi_post(query, variables={"filter": filter})
    assert response.errors is None
    assert response.data
    return response.data["event_namespaces"]["objects"]


def get_listeners(
    graphapi_post: GraphAPIPost,
    filter: dict | None = None,
    event_filter: dict | None = None,
) -> list[dict[str, Any]]:
    query = """
      query GetListeners($filter: ListenerFilter!, $event_filter: ListenersBoundFullEventFilter!) {
        event_listeners(filter: $filter) {
          objects {
            routing_key
            user_key
            uuid
            owner
            events(filter: $event_filter) {
              silenced
              priority
              subject
            }
          }
        }
      }
    """
    if filter is None:
        filter = {}
    if event_filter is None:
        event_filter = {}
    response = graphapi_post(
        query, variables={"filter": filter, "event_filter": event_filter}
    )
    assert response.errors is None
    assert response.data
    return response.data["event_listeners"]["objects"]


def get_events(graphapi_post: GraphAPIPost) -> list[dict[str, Any]]:
    query = """
      query GetEvents {
        events {
          objects {
            priority
            silenced
            subject
          }
        }
      }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    return response.data["events"]["objects"]


def delete_listener(
    graphapi_post: GraphAPIPost,
    listener_uuid: UUID,
    delete_pending_events: bool = False,
) -> GQLResponse:
    query = """
      mutation DeleteListener($listener_uuid: UUID!, $delete_pending_events: Boolean!) {
        event_listener_delete(
          input: {uuid: $listener_uuid, delete_pending_events: $delete_pending_events}
        )
      }
    """
    response = graphapi_post(
        query,
        variables={
            "listener_uuid": str(listener_uuid),
            "delete_pending_events": delete_pending_events,
        },
    )
    return response


def silence_event(graphapi_post: GraphAPIPost, input: dict[str, Any]) -> None:
    query = """
      mutation Silence($input: EventSilenceInput!) {
        event_silence(input: $input)
      }
    """
    response = graphapi_post(query, variables={"input": input})
    assert response.errors is None


def unsilence_event(graphapi_post: GraphAPIPost, input: dict[str, Any]) -> None:
    query = """
      mutation Unsilence($input: EventUnsilenceInput!) {
        event_unsilence(input: $input)
      }
    """
    response = graphapi_post(query, variables={"input": input})
    assert response.errors is None


@pytest.fixture
def namespace(graphapi_post: GraphAPIPost) -> str:
    response = declare_namespace(graphapi_post, DEFAULT_TEST_NS)
    assert response.errors is None
    assert response.data is not None
    return response.data["event_namespace_declare"]["name"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_declare_listener_default_mo(graphapi_post: GraphAPIPost) -> None:
    # Explicitly does not use helper, to make sure default ns = "mo" works
    query = """
      mutation DeclareListener( $user_key: String!, $routing_key: String!) {
        event_listener_declare(
          input: { user_key: $user_key, routing_key: $routing_key }
        ) {
          uuid
          owner
        }
      }
    """
    response = graphapi_post(
        query,
        variables={
            "user_key": "my listener",
            "routing_key": "org_unit",
        },
    )
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_namespace_delete(graphapi_post: GraphAPIPost) -> None:
    mo_ns = {"name": "mo", "owner": ANY, "public": True}
    my_ns = {"name": "my ns", "owner": ANY, "public": False}
    declare_namespace(graphapi_post, my_ns["name"])
    assert list(sorted(get_namespaces(graphapi_post), key=lambda n: n["name"])) == [
        mo_ns,
        my_ns,
    ]
    delete_namespace(graphapi_post, my_ns["name"])
    assert get_namespaces(graphapi_post) == [mo_ns]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_mo_namespace_exists(graphapi_post: GraphAPIPost) -> None:
    assert get_namespaces(graphapi_post) == [
        {"name": "mo", "owner": ANY, "public": True}
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_both_listeners_receive_event(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    routing_key = "rk"
    listener1_uuid = declare_listener(graphapi_post, namespace, "uk1", routing_key)
    listener2_uuid = declare_listener(graphapi_post, namespace, "uk2", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")

    for listener in (listener1_uuid, listener2_uuid):
        subjects = ["alice", "bob"]
        for _ in range(len(subjects)):
            event = fetch_event(graphapi_post, listener)
            assert event is not None
            assert event["subject"] in subjects
            subjects.remove(event["subject"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_different_routing_keys(namespace: str, graphapi_post: GraphAPIPost) -> None:
    listener1_uuid = declare_listener(graphapi_post, namespace, "uk1", "not a person")
    listener2_uuid = declare_listener(graphapi_post, namespace, "uk2", "person")
    send_event(graphapi_post, namespace, "person", "alice")
    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 2, listeners
    for listener in listeners:
        match listener:
            case listener if UUID(listener["uuid"]) == listener1_uuid:
                assert len(listener["events"]) == 0
            case listener if UUID(listener["uuid"]) == listener2_uuid:
                assert len(listener["events"]) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_acknowledgement(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    subjects = ["alice", "bob"]

    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)

    for subject in subjects:
        send_event(graphapi_post, namespace, routing_key, subject)

    for _ in range(len(subjects)):
        event = fetch_event(graphapi_post, listener)
        assert event is not None
        assert event["subject"] in subjects
        subjects.remove(event["subject"])
        ack_event(graphapi_post, event["token"])

    assert fetch_event(graphapi_post, listener) is None

    listeners = get_listeners(graphapi_post)
    assert len(one(listeners)["events"]) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_acknowledgement_with_new_event_sent_while_processing(
    namespace: str,
    graphapi_post: GraphAPIPost,
) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)

    send_event(graphapi_post, namespace, routing_key, "alice")
    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == "alice"
    send_event(graphapi_post, namespace, routing_key, "alice")
    # This ack should't delete the event, as there have been sent a new one in
    # the meantime.
    ack_event(graphapi_post, event["token"])

    # You can receive events instantly, when they are resubmitted in this case.
    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_fetch_same_event_immediately(
    namespace: str,
    graphapi_post: GraphAPIPost,
) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    assert fetch_event(graphapi_post, listener) is not None
    assert fetch_event(graphapi_post, listener) is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_fetch_from_others_listener(
    set_auth: SetAuth,
    namespace: str,
    graphapi_post: GraphAPIPost,
) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    set_auth(ADMIN, uuid4())
    assert fetch_event(graphapi_post, listener) is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_long_subjects_fails(namespace: str, graphapi_post: GraphAPIPost) -> None:
    r = send_event(graphapi_post, namespace, "rk", "A" * 230)
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "Too large subject. Only send identifiers as the subject, not data"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_cannot_send_event_in_non_existant_namespace(
    graphapi_post: GraphAPIPost,
) -> None:
    r = send_event(graphapi_post, "random", "rk", "alice")
    assert r.errors is not None
    assert one(r.errors)["message"] == "Namespace does not exist."


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_cannot_send_event_in_non_others_namespace(
    set_auth: SetAuth, namespace: str, graphapi_post: GraphAPIPost
) -> None:
    set_auth(ADMIN, uuid4())
    r = send_event(graphapi_post, namespace, "rk", "alice")
    assert r.errors is not None
    assert one(r.errors)["message"] == "You are not the owner of that namespace."


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_cannot_create_listener_in_non_existant_namespace(
    graphapi_post: GraphAPIPost,
) -> None:
    r = declare_listener_raw(graphapi_post, "random", "uk", "rk")
    assert r.errors is not None
    assert one(r.errors)["message"] == "Namespace does not exist"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener(namespace: str, graphapi_post: GraphAPIPost) -> None:
    listener = declare_listener(graphapi_post, namespace, "uk", "rk")
    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 1, listeners
    delete_listener(graphapi_post, listener)
    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 0, listeners


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener_with_events_fails(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    listener = declare_listener(graphapi_post, namespace, "uk", "rk")
    send_event(graphapi_post, namespace, "rk", "alice")
    assert len(get_listeners(graphapi_post)) == 1
    r = delete_listener(graphapi_post, listener)
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "There are pending events for this listener. Consider carefully if these need to be handled first. You can delete the listener anyway with `delete_pending_events`."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_nonexisting_listener(graphapi_post: GraphAPIPost) -> None:
    response = delete_listener(graphapi_post, uuid4())
    assert response.errors is None
    assert response.data is not None
    assert response.data["event_listener_delete"] is True


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener_with_events_with_delete_pending(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    listener = declare_listener(graphapi_post, namespace, "uk", "rk")
    send_event(graphapi_post, namespace, "rk", "alice")
    assert len(get_listeners(graphapi_post)) == 1
    r = delete_listener(graphapi_post, listener, delete_pending_events=True)
    assert r.errors is None
    assert len(get_listeners(graphapi_post)) == 0
    assert len(get_events(graphapi_post)) == 0  # make sure events don't leak


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("send_in_reverse", [True, False])
def test_event_priorities(
    namespace: str, graphapi_post: GraphAPIPost, send_in_reverse: bool
) -> None:
    # send_in_reverse makes sure we don't test insert order
    START = 30
    AMOUNT = 58
    listener = declare_listener(graphapi_post, namespace, "uk", "rk")
    for i in range(START, START + AMOUNT):
        priority = START + AMOUNT - i if send_in_reverse else i
        send_event(graphapi_post, "ns", "rk", f"alice_{i}", priority=priority)

    priorities = []
    for _ in range(AMOUNT):
        event = fetch_event(graphapi_post, listener)
        assert event is not None
        priorities.append(event["priority"])

    assert priorities == list(sorted(priorities))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priority_dedup_1(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice", priority=1)
    send_event(graphapi_post, namespace, routing_key, "alice", priority=2)
    event = one(get_events(graphapi_post))
    assert event["priority"] == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priority_dedup_2(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "bob", priority=1)
    send_event(graphapi_post, namespace, routing_key, "alice", priority=3)
    send_event(graphapi_post, namespace, routing_key, "alice", priority=2)
    events = get_events(graphapi_post)
    alice_event, bob_event = sorted(events, key=lambda e: e["subject"])
    assert alice_event["subject"] == "alice"
    assert alice_event["priority"] == 2
    assert bob_event["subject"] == "bob"
    assert bob_event["priority"] == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_not_natural_priority(namespace: str, graphapi_post: GraphAPIPost) -> None:
    r = send_event(graphapi_post, namespace, "rk", "alice", priority=0)
    assert r.errors is not None
    assert one(r.errors)["message"] == "priority must be natural"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_silence(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"

    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    silence_event(
        graphapi_post, {"subjects": ["alice"], "listeners": {"uuids": [str(listener)]}}
    )
    event = fetch_event(graphapi_post, listener)
    assert event is None

    listeners = get_listeners(graphapi_post)
    assert one(one(listeners)["events"])["silenced"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_unsilence(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    silence_event(
        graphapi_post, {"subjects": ["alice"], "listeners": {"uuids": [str(listener)]}}
    )
    unsilence_event(
        graphapi_post, {"subjects": ["alice"], "listeners": {"uuids": [str(listener)]}}
    )
    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_unsilence_resends_immediately(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")

    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == "alice"

    unsilence_event(
        graphapi_post, {"subjects": ["alice"], "listeners": {"uuids": [str(listener)]}}
    )

    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_deduplication(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")
    send_event(graphapi_post, namespace, routing_key, "alice")
    events = get_events(graphapi_post)
    subjects = list(sorted(e["subject"] for e in events))
    assert subjects == ["alice", "bob"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priority_10000(namespace: str, graphapi_post: GraphAPIPost) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["priority"] == 10000


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_idempotent_listener_declare(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    assert one(get_listeners(graphapi_post))
    # Send an event. We want to check that it is still there.
    send_event(graphapi_post, namespace, routing_key, "alice")
    new_listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    assert listener == new_listener
    actual_listener = one(get_listeners(graphapi_post))
    assert UUID(actual_listener["uuid"]) == listener
    assert one(actual_listener["events"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_listener_declare_duplicate_user_key(
    namespace: str, graphapi_post: GraphAPIPost
) -> None:
    user_key = "us"
    declare_listener(graphapi_post, namespace, user_key, "person")
    r = declare_listener_raw(graphapi_post, namespace, user_key, "not a person")
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "There already exists a listener with this user_key and a different routing_key"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_ack_fake_token(graphapi_post: GraphAPIPost) -> None:
    fake_token = "bm90IGEgcmVhbCB0b2tlbgo="
    r = ack_event(graphapi_post, fake_token)
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == f"Variable '$token' got invalid value '{fake_token}'; Expected type 'EventToken'. Could not parse EventToken"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_listeners_filter(namespace: str, graphapi_post: GraphAPIPost) -> None:
    rk1 = "rk1"
    rk2 = "rk2"
    declare_listener(graphapi_post, namespace, "uk", rk1)
    declare_listener(graphapi_post, namespace, "uk2", rk2)
    send_event(graphapi_post, namespace, rk1, "alice", priority=7)
    send_event(graphapi_post, namespace, rk1, "bob")
    send_event(graphapi_post, namespace, rk2, "alice")

    silence_event(
        graphapi_post, {"subjects": ["alice"], "listeners": {"routing_keys": rk2}}
    )

    assert one(get_listeners(graphapi_post, filter={"routing_keys": [rk1]}))
    assert len(get_listeners(graphapi_post, filter={"routing_keys": [rk1, rk2]})) == 2

    assert (
        len(
            one(
                get_listeners(
                    graphapi_post, filter={"routing_keys": [rk1]}, event_filter={}
                )
            )["events"]
        )
        == 2
    )
    assert one(
        one(
            get_listeners(
                graphapi_post,
                filter={"routing_keys": [rk1]},
                event_filter={"priorities": 7},
            )
        )["events"]
    )
    assert one(
        one(
            get_listeners(
                graphapi_post,
                filter={"routing_keys": [rk1]},
                event_filter={"subjects": ["alice"]},
            )
        )["events"]
    )

    assert one(
        one(
            get_listeners(
                graphapi_post, filter={"routing_keys": [rk2]}, event_filter={}
            )
        )["events"]
    )
    assert (
        len(
            one(
                get_listeners(
                    graphapi_post,
                    filter={"routing_keys": [rk2]},
                    event_filter={"silenced": True},
                )
            )["events"]
        )
        == 1
    )
    assert (
        len(
            one(
                get_listeners(
                    graphapi_post,
                    filter={"routing_keys": [rk2]},
                    event_filter={"silenced": False},
                )
            )["events"]
        )
        == 0
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_refresh_person(graphapi_post: GraphAPIPost) -> None:
    # Create root org...
    assert (
        graphapi_post(
            """
        mutation CreateOrg {
            org_create(input: { municipality_code: null }) {
                uuid
            }
        }
        """
        ).errors
        is None
    )

    listener_query = declare_listener_raw(
        graphapi_post, "mo", "person_listener", "person"
    )
    assert listener_query.data is not None
    listener = listener_query.data["event_listener_declare"]["uuid"]
    owner = listener_query.data["event_listener_declare"]["owner"]

    # Create employee
    person_query = graphapi_post(
        """
        mutation CreatePerson {
          employee_create(input: { given_name: "Anders", surname: "And" }) {
            uuid
          }
        }
        """,
    )
    assert person_query.data is not None
    person_uuid = person_query.data["employee_create"]["uuid"]

    # Refresh
    refresh_query = graphapi_post(
        """
        mutation RefreshPerson($owner: UUID!) {
          employee_refresh(owner: $owner) {
            objects
          }
        }
        """,
        variables={
            "owner": owner,
        },
    )
    assert refresh_query.data is not None
    assert refresh_query.data["employee_refresh"]["objects"] == [person_uuid]

    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == person_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "model,filter_uuid",
    [
        ("address", "414044e0-fe5f-4f82-be20-1e107ad50e80"),
        ("association", "c2153d5d-4a2b-492d-a18c-c498f7bb6221"),
        ("class", "06f95678-166a-455a-a2ab-121a8d92ea23"),
        ("engagement", "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"),
        ("facet", "1a6045a2-7a8e-4916-ab27-b2402e64f2be"),
        ("itsystem", "59c135c9-2b15-41cc-97c8-b5dff7180beb"),
        ("ituser", "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66"),
        ("kle", "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5"),
        ("leave", "0895b7f5-86ac-45c5-8fb1-c3047d45b643"),
        ("manager", "05609702-977f-4869-9fb4-50ad74c6999a"),
        ("org_unit", "5942ce50-2be8-476f-914b-6769a888a7c8"),
        ("owner", "c16ff527-3501-42f7-a942-e606c6c1a0a7"),
        ("related_unit", "5c68402c-2a8d-4776-9237-16349fc72648"),
        ("rolebinding", "1b20d0b9-96a0-42a6-b196-293bb86e62e8"),
    ],
)
def test_refresh_mutators(
    graphapi_post: GraphAPIPost, model: str, filter_uuid: str
) -> None:
    listener_query = declare_listener_raw(
        graphapi_post, "mo", f"{model}_listener", model
    )
    assert listener_query.data is not None
    listener = listener_query.data["event_listener_declare"]["uuid"]
    owner = listener_query.data["event_listener_declare"]["owner"]

    mutator = f"{model}_refresh"
    refresh_query = graphapi_post(
        f"""
          mutation RefreshMutation($owner: UUID!, $uuid: UUID!) {{
            {mutator}(owner: $owner, filter: {{uuids: [$uuid]}}) {{
              objects
            }}
          }}
        """,
        variables={
            "owner": owner,
            "uuid": filter_uuid,
        },
    )
    assert refresh_query.data is not None
    assert refresh_query.data[mutator]["objects"] == [filter_uuid]

    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == filter_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_idempotently_create_others_namespace(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    ns = "its only mine"

    user1 = uuid4()
    user2 = uuid4()

    set_auth(ADMIN, user1)
    declare_namespace(graphapi_post, ns)

    set_auth(ADMIN, user2)
    response = declare_namespace(graphapi_post, ns)

    assert response.errors is not None
    assert (
        one(response.errors)["message"] == "Namespace already claimed by another owner."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_changing_public_idempotent_fail(graphapi_post: GraphAPIPost) -> None:
    ns = "private"

    ns1 = declare_namespace(graphapi_post, ns)
    assert ns1.data is not None
    assert not ns1.data["event_namespace_declare"]["public"]

    ns2 = declare_namespace(graphapi_post, ns, public=True)
    assert ns2.data is None
    assert ns2.errors is not None
    assert one(ns2.errors)["message"] == "Namespace already exists with public=false."


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_create_listener_in_nonpublic_namespace(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    ns = "private"

    user1 = uuid4()
    user2 = uuid4()

    set_auth(ADMIN, user1)
    declare_namespace(graphapi_post, ns)
    r = declare_listener_raw(graphapi_post, ns, "uk1", "haha")
    assert r.errors is None

    set_auth(ADMIN, user2)
    r = declare_listener_raw(graphapi_post, ns, "uk2", "haha")
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "Namespace already exists, but is non-public and you are not the owner."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_metrics(graphapi_post: GraphAPIPost, service_client: TestClient) -> None:
    AMOUNT = 58
    ACK_EVENTS = 3

    response = declare_namespace(graphapi_post, "metric_test")
    assert response.data is not None
    namespace = response.data["event_namespace_declare"]["name"]

    listener = declare_listener(graphapi_post, namespace, "uk", "rk")
    declare_listener(graphapi_post, namespace, "uk2", "rk")

    for i in range(AMOUNT):
        send_event(graphapi_post, "metric_test", "rk", f"alice_{i}")

    for i in range(ACK_EVENTS):
        event = fetch_event(graphapi_post, listener)
        assert event is not None
        ack_event(graphapi_post, event["token"])

    silence_event(
        graphapi_post,
        {"subjects": ["alice_10"], "listeners": {"uuids": [str(listener)]}},
    )

    # The metrics are calculated, but not returned on the first request..
    service_client.request("GET", "/metrics")
    response = service_client.request("GET", "/metrics")
    assert response.status_code == 200
    metrics = response.text

    assert (
        f'os2mo_event_sent_total{{namespace="metric_test",routing_key="rk"}} {AMOUNT}.0'
        in metrics
    )
    assert (
        f'os2mo_event_acknowledged_total{{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",user_key="uk"}} {ACK_EVENTS}.0'
        in metrics
    )
    assert (
        'os2mo_events{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="true",user_key="uk"} 1.0'
        in metrics
    )
    assert (
        f'os2mo_events{{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="false",user_key="uk"}} {AMOUNT - ACK_EVENTS - 1}.0'
        in metrics
    )  # -1 for the silenced event
    assert (
        f'os2mo_events{{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="false",user_key="uk2"}} {AMOUNT}.0'
        in metrics
    )
    assert (
        'os2mo_event_oldest{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="false",user_key="uk2"}'
        in metrics
    )
    assert (
        'os2mo_event_oldest{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="false",user_key="uk"}'
        in metrics
    )
    assert (
        'os2mo_event_oldest{namespace="metric_test",owner="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",routing_key="rk",silenced="true",user_key="uk"}'
        in metrics
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_send_in_mo_namespace(graphapi_post: GraphAPIPost) -> None:
    # Only the namespace owner can use `event_send` in it.
    listener = declare_listener(graphapi_post, "mo", "my_listener", "person")
    send_event(graphapi_post, "mo", "person", str(uuid4()))
    event = fetch_event(graphapi_post, listener)
    assert event is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_ns_filter(set_auth: SetAuth, graphapi_post: GraphAPIPost) -> None:
    ns1 = {"name": "ns1", "owner": str(uuid4()), "public": False}
    ns2 = {"name": "ns2", "owner": str(uuid4()), "public": False}
    ns3 = {"name": "ns3", "owner": str(uuid4()), "public": True}

    for ns in (ns1, ns2, ns3):
        set_auth(ADMIN, ns["owner"])
        response = declare_namespace(graphapi_post, ns["name"], public=ns["public"])
        assert response.errors is None

    # Start querying as a random user
    set_auth(ADMIN, uuid4())

    assert get_namespaces(
        graphapi_post, filter={"names": [ns1["name"], ns2["name"]]}
    ) == [ns1, ns2]
    assert get_namespaces(
        graphapi_post,
        filter={"names": [ns1["name"], ns2["name"]], "owners": [ns2["owner"]]},
    ) == [ns2]
    assert (
        get_namespaces(
            graphapi_post,
            filter={"names": [ns1["name"], ns2["name"]], "owners": [ns3["owner"]]},
        )
        == []
    )
    assert get_namespaces(
        graphapi_post, filter={"names": [ns3["name"], ns2["name"]], "public": False}
    ) == [ns2]
    assert get_namespaces(
        graphapi_post, filter={"names": [ns3["name"], ns2["name"]], "public": True}
    ) == [ns3]
