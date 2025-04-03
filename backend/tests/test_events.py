from uuid import uuid4
from uuid import UUID
from typing import Any

import pytest
from more_itertools import one
from tests.conftest import GraphAPIPost
from tests.conftest import GQLResponse


def declare_listener_raw(
    graphapi_post: GraphAPIPost, namespace: str, user_key: str, routing_key: str
) -> GQLResponse:
    query = """
      mutation DeclareListener($namespace: String!, $user_key: String!, $routing_key: String!) {
        event_listener_declare(
          input: { namespace: $namespace, user_key: $user_key, routing_key: $routing_key }
        ) {
          uuid
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
    priority: int = 10,
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
    assert response.data
    return response


def fetch_event(graphapi_post: GraphAPIPost, listener_uuid: UUID) -> dict[str, Any]:
    query = """
      query FetchEvent($listener_uuid: UUID!) {
        event_fetch(filter: { listener: $listener_uuid }) {
          uuid
          subject
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


def get_listeners(graphapi_post: GraphAPIPost, filter: dict | None = None, event_filter: dict | None = None) -> list[dict[str, Any]]:
    query = """
      query GetListeners($filter: ListenerFilter!, $event_filter: ListenerBoundFullEventFilter!) {
        event_listeners(filter: $filter) {
          objects {
            routing_key
            user_key
            uuid
            namespace
            owner
            events(filter: $event_filter) {
              silenced
              priority
              subject
              uuid
            }
          }
        }
      }
    """
    if filter is None:
        filter = {}
    if event_filter is None:
        event_filter = {}
    response = graphapi_post(query, variables={"filter": filter, "event_filter": event_filter})
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
            uuid
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


def silence_event(graphapi_post: GraphAPIPost, event_uuid: UUID):
    query = """
      mutation Silence($uuid: UUID!) {
        event_silence(input: { uuid: $uuid })
      }
    """
    response = graphapi_post(query, variables={"uuid": str(event_uuid)})
    assert response.errors is None


def unsilence_event(graphapi_post: GraphAPIPost, event_uuid: UUID):
    query = """
      mutation Unsilence($uuid: UUID!) {
        event_unsilence(input: { uuids: [$uuid] })
      }
    """
    response = graphapi_post(query, variables={"uuid": str(event_uuid)})
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_both_listeners_receive_event(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    listener1_uuid = declare_listener(graphapi_post, namespace, "uk1", routing_key)
    listener2_uuid = declare_listener(graphapi_post, namespace, "uk2", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")

    seen_events = set()
    for listener in (listener1_uuid, listener2_uuid):
        subjects = ["alice", "bob"]
        for _ in range(len(subjects)):
            event = fetch_event(graphapi_post, listener)
            assert event["uuid"] not in seen_events
            seen_events.add(event["uuid"])
            assert event["subject"] in subjects
            subjects.remove(event["subject"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_different_routing_keys(graphapi_post: GraphAPIPost) -> None:
    namespace= "ns"
    listener1_uuid = declare_listener(graphapi_post, namespace, "uk1", "employee")
    listener2_uuid = declare_listener(graphapi_post, namespace, "uk2", "person")
    send_event(graphapi_post, namespace, "person", "alice")
    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 2
    for listener in listeners:
        match listener:
            case listener if UUID(listener["uuid"]) == listener1_uuid:
                assert len(listener["events"]) == 0
            case listener if UUID(listener["uuid"]) == listener2_uuid:
                assert len(listener["events"]) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_acknowledgement(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    subjects = ["alice", "bob"]

    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)

    for subject in subjects:
        send_event(graphapi_post, namespace, routing_key, subject)

    for _ in range(len(subjects)):
        event = fetch_event(graphapi_post, listener)
        assert event["subject"] in subjects
        subjects.remove(event["subject"])
        ack_event(graphapi_post, event["token"])

    assert fetch_event(graphapi_post, listener) is None

    listeners = get_listeners(graphapi_post)
    assert len(one(listeners)["events"]) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_acknowledgement_with_new_event_sent_while_processing(
    graphapi_post: GraphAPIPost,
) -> None:
    namespace = "ns"
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)

    send_event(graphapi_post, namespace, routing_key, "alice")
    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"
    send_event(graphapi_post, namespace, routing_key, "alice")
    # This ack should't delete the event, as there have been sent a new one in
    # the meantime.
    ack_event(graphapi_post, event["token"])

    # You can receive events instantly, when they are resubmitted in this case.
    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_you_cannot_fetch_same_event_immediately(
    graphapi_post: GraphAPIPost,
) -> None:
    namespace = "ns"
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    assert fetch_event(graphapi_post, listener) is not None
    assert fetch_event(graphapi_post, listener) is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_long_subjects_fails(graphapi_post: GraphAPIPost) -> None:
    r = send_event(graphapi_post, "ns", "rk", "A" * 230)
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "Too large subject. Only send identifiers as the subject, not data"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_mo_namespace_banned(graphapi_post: GraphAPIPost) -> None:
    r = send_event(graphapi_post, "mo", "rk", "alice")
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == 'You are not allowed to send events in the "mo" namespace'
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener(graphapi_post: GraphAPIPost) -> None:
    listener = declare_listener(graphapi_post, "ns", "uk", "rk")
    assert len(get_listeners(graphapi_post)) == 1
    delete_listener(graphapi_post, listener)
    assert len(get_listeners(graphapi_post)) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener_with_events_fails(graphapi_post: GraphAPIPost) -> None:
    listener = declare_listener(graphapi_post, "ns", "uk", "rk")
    send_event(graphapi_post, "ns", "rk", "alice")
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_delete_listener_with_events_with_delete_pending(graphapi_post: GraphAPIPost) -> None:
    listener = declare_listener(graphapi_post, "ns", "uk", "rk")
    send_event(graphapi_post, "ns", "rk", "alice")
    assert len(get_listeners(graphapi_post)) == 1
    r = delete_listener(graphapi_post, listener, delete_pending_events=True)
    assert r.errors is None
    assert len(get_listeners(graphapi_post)) == 0
    assert len(get_events(graphapi_post)) == 0  # make sure events don't leak


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priorities(graphapi_post: GraphAPIPost) -> None:
    listener = declare_listener(graphapi_post, "ns", "uk", "rk")
    for i in range(200):
        send_event(graphapi_post, "ns", "rk", f"alice_{i}")
    send_event(graphapi_post, "ns", "rk", f"bob", priority=4)

    subjects = set()
    for _ in range(7):
        event = fetch_event(graphapi_post, listener)
        subjects.add(event["subject"])

    assert "bob" in subjects, (
        "Did this test fail on you with unrelated code changes? Buy a lotto ticket. There is only a 0.0002% chance of this happening if you didn't screw up."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priority_dedup_1(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, f"alice", priority=1)
    send_event(graphapi_post, namespace, routing_key, f"alice", priority=2)
    event = one(get_events(graphapi_post))
    assert event["priority"] == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_priority_dedup_2(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, f"bob", priority=1)
    send_event(graphapi_post, namespace, routing_key, f"alice", priority=3)
    send_event(graphapi_post, namespace, routing_key, f"alice", priority=2)
    events = get_events(graphapi_post)
    alice_event, bob_event = sorted(events, key=lambda e: e["subject"])
    assert alice_event["subject"] == "alice"
    assert alice_event["priority"] == 2
    assert bob_event["subject"] == "bob"
    assert bob_event["priority"] == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_fetch_random_event(graphapi_post: GraphAPIPost) -> None:
    # Sometimes MO will return a random event instead of the highest
    # priority. Make sure this happens.
    namespace = "ns"
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)

    for _ in range(1000):
        send_event(graphapi_post, namespace, routing_key, "alice")
        send_event(graphapi_post, namespace, routing_key, "bob", priority=9000)
        first_fetch = fetch_event(graphapi_post, listener)
        fetch_event(graphapi_post, listener)
        if first_fetch["subject"] == "bob":
            break
    else:
        assert False, "We never received the low priority event"

@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_not_natural_priority(graphapi_post: GraphAPIPost) -> None:
    r = send_event(graphapi_post, "ns", "rk", "alice", priority=0)
    assert r.errors is not None
    assert (
        one(r.errors)["message"]
        == "priority must be natural"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_silence(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"

    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    event_id = one(one(get_listeners(graphapi_post))["events"])["uuid"]
    silence_event(graphapi_post, event_id)
    event = fetch_event(graphapi_post, listener)
    assert event is None

    listeners = get_listeners(graphapi_post)
    assert one(one(listeners)["events"])["silenced"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_unsilence(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    listener = declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    event_id = one(one(get_listeners(graphapi_post))["events"])["uuid"]
    silence_event(graphapi_post, event_id)
    unsilence_event(graphapi_post, event_id)
    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_event_deduplication(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    routing_key = "rk"
    declare_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")
    send_event(graphapi_post, namespace, routing_key, "alice")
    events = get_events(graphapi_post)
    assert len(events) == 2
    

@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_idempotent_listener_declare(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
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
def test_listener_declare_duplicate_user_key(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    user_key = "us"
    declare_listener(graphapi_post, namespace, user_key, "person")
    r = declare_listener_raw(graphapi_post, namespace, user_key, "employee")
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
def test_listeners_filter(graphapi_post: GraphAPIPost) -> None:
    namespace = "ns"
    rk1 = "rk1"
    rk2 = "rk2"
    declare_listener(graphapi_post, namespace, "uk", rk1)
    declare_listener(graphapi_post, namespace, "uk2", rk2)
    send_event(graphapi_post, namespace, rk1, "alice", priority=7)
    send_event(graphapi_post, namespace, rk1, "bob")
    send_event(graphapi_post, namespace, rk2, "alice")

    event_id = one(one(get_listeners(graphapi_post, filter={"routing_keys": [rk2]}))["events"])["uuid"]
    silence_event(graphapi_post, event_id)

    assert one(get_listeners(graphapi_post, filter={"routing_keys": [rk1]}))
    assert len(get_listeners(graphapi_post, filter={"routing_keys": [rk1, rk2]})) == 2

    assert len(one(get_listeners(graphapi_post, filter={"routing_keys": [rk1]}, event_filter={}))["events"]) == 2
    assert one(one(get_listeners(graphapi_post, filter={"routing_keys": [rk1]}, event_filter={"priorities": 7}))["events"])
    assert one(one(get_listeners(graphapi_post, filter={"routing_keys": [rk1]}, event_filter={"subjects": ["alice"]}))["events"])

    assert one(one(get_listeners(graphapi_post, filter={"routing_keys": [rk2]}, event_filter={}))["events"])
    assert len(one(get_listeners(graphapi_post, filter={"routing_keys": [rk2]}, event_filter={"silenced": True}))["events"]) == 1
    assert len(one(get_listeners(graphapi_post, filter={"routing_keys": [rk2]}, event_filter={"silenced": False}))["events"]) == 0


# test filters

# test refresh
# TODO add refresh mutator to docs
