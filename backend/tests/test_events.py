from uuid import UUID

import pytest
from tests.conftest import GraphAPIPost


def create_listener(
    graphapi_post: GraphAPIPost, namespace: str, user_key: str, routing_key: str
) -> UUID:
    query = """
      mutation CreateListener($namespace: String!, $user_key: String!, $routing_key: String!) {
        event_listener_create(
          input: { namespace: $namespace, user_key: $user_key, routing_key: $routing_key }
        ) {
          uuid
        }
      }
    """
    response = graphapi_post(
        query,
        variables={
            "namespace": namespace,
            "user_key": user_key,
            "routing_key": routing_key,
        },
    )
    assert response.errors is None
    assert response.data
    return UUID(response.data["event_listener_create"]["uuid"])


def send_event(
    graphapi_post: GraphAPIPost,
    namespace: str,
    routing_key: str,
    subject: str,
    priority: int = 10,
):
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


def fetch_event(graphapi_post: GraphAPIPost, listener_uuid: UUID) -> dict:
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


def ack_event(graphapi_post: GraphAPIPost, token: str) -> None:
    query = """
      mutation Ack($token: EventToken!) {
        event_acknowledge(
          input: {token: $token}
        )
      }
    """
    response = graphapi_post(query, variables={"token": token})
    assert response.errors is None


def get_listeners(graphapi_post: GraphAPIPost) -> dict:
    query = """
      query GetListeners {
        event_listeners {
          objects {
            routing_key
            user_key
            uuid
            namespace
            owner
            events {
              silenced
              priority
              subject
              uuid
            }
          }
        }
      }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    return response.data["event_listeners"]["objects"]


def delete_listener(
    graphapi_post: GraphAPIPost,
    listener_uuid: UUID,
    delete_pending_events: bool = False,
):
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
    graphapi_post(query, variables={"uuid": str(event_uuid)})


def unsilence_event(graphapi_post: GraphAPIPost, event_uuid: UUID):
    query = """
      mutation Unsilence($uuid: UUID!) {
        event_unsilence(input: { uuids: [$uuid] })
      }
    """
    graphapi_post(query, variables={"uuid": str(event_uuid)})


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_both_listeners_receive_event(graphapi_post: GraphAPIPost):
    namespace = "ns"
    routing_key = "rk"
    listener1_uuid = create_listener(graphapi_post, namespace, "uk1", routing_key)
    listener2_uuid = create_listener(graphapi_post, namespace, "uk2", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")

    seen_events = set()
    for listener in (listener1_uuid, listener2_uuid):
        subjects = ["alice", "bob"]
        event = fetch_event(graphapi_post, listener)
        assert event["uuid"] not in seen_events
        seen_events.add(event["uuid"])
        assert event["subject"] in subjects
        subjects.remove(event["subject"])


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_acknowledgement(graphapi_post: GraphAPIPost):
    namespace = "ns"
    routing_key = "rk"
    listener = create_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    send_event(graphapi_post, namespace, routing_key, "bob")

    subjects = ["alice", "bob"]
    for _ in range(2):
        event = fetch_event(graphapi_post, listener)
        assert event["subject"] in subjects
        subjects.remove(event["subject"])
        ack_event(graphapi_post, event["token"])

    assert fetch_event(graphapi_post, listener) is None

    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 1
    assert len(listeners[0]["events"]) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_acknowledgement_with_new_event_sent_while_processing(
    graphapi_post: GraphAPIPost,
):
    namespace = "ns"
    routing_key = "rk"
    listener = create_listener(graphapi_post, namespace, "uk", routing_key)

    send_event(graphapi_post, namespace, routing_key, "alice")
    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"
    send_event(graphapi_post, namespace, routing_key, "alice")
    # This ack should't delete the event, as there have been sent a new one in
    # the meantime.
    ack_event(graphapi_post, event["token"])

    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_long_subjects_fails(graphapi_post: GraphAPIPost):
    r = send_event(graphapi_post, "ns", "rk", "A" * 230)
    assert r.errors is not None
    assert len(r.errors) == 1
    assert (
        r.errors[0]["message"]
        == "Too large subject. Only send identifiers as the subject, not data"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_mo_namespace_banned(graphapi_post: GraphAPIPost):
    r = send_event(graphapi_post, "mo", "rk", "alice")
    assert r.errors is not None
    assert len(r.errors) == 1
    assert (
        r.errors[0]["message"]
        == 'You are not allowed to send events in the "mo" namespace'
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_delete_listener(graphapi_post: GraphAPIPost):
    listener = create_listener(graphapi_post, "ns", "uk", "rk")
    assert len(get_listeners(graphapi_post)) == 1
    delete_listener(graphapi_post, listener)
    assert len(get_listeners(graphapi_post)) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_delete_listener_with_events_fails(graphapi_post: GraphAPIPost):
    listener = create_listener(graphapi_post, "ns", "uk", "rk")
    send_event(graphapi_post, "ns", "rk", "alice")
    assert len(get_listeners(graphapi_post)) == 1
    r = delete_listener(graphapi_post, listener)
    assert r.errors is not None
    assert len(r.errors) == 1
    assert (
        r.errors[0]["message"]
        == "There are pending events for this listener. Consider carefully if these need to be handled first. You can delete the listener anyway with `delete_pending_events`."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_delete_listener_with_events_with_delete_pending(graphapi_post: GraphAPIPost):
    listener = create_listener(graphapi_post, "ns", "uk", "rk")
    send_event(graphapi_post, "ns", "rk", "alice")
    assert len(get_listeners(graphapi_post)) == 1
    r = delete_listener(graphapi_post, listener, delete_pending_events=True)
    assert r.errors is None
    assert len(get_listeners(graphapi_post)) == 0


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_event_priorities(graphapi_post: GraphAPIPost):
    listener = create_listener(graphapi_post, "ns", "uk", "rk")
    for i in range(200):
        send_event(graphapi_post, "ns", "rk", f"alice_{i}")
    send_event(graphapi_post, "ns", "rk", f"bob", priority=4)

    subjects = set()
    for _ in range(6):
        event = fetch_event(graphapi_post, listener)
        subjects.add(event["subject"])

    assert "bob" in subjects, (
        "Did this test fail on you with unrelated code changes? Buy a lotto ticket. There is only a 0.001% chance of this happening if you didn't screw up."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_event_silence(graphapi_post: GraphAPIPost):
    namespace = "ns"
    routing_key = "rk"

    listener = create_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    event_id = get_listeners(graphapi_post)[0]["events"][0]["uuid"]
    silence_event(graphapi_post, event_id)
    event = fetch_event(graphapi_post, listener)
    assert event is None

    listeners = get_listeners(graphapi_post)
    assert len(listeners) == 1
    assert listeners[0]["events"][0]["silenced"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_event_unsilence(graphapi_post: GraphAPIPost):
    namespace = "ns"
    routing_key = "rk"
    listener = create_listener(graphapi_post, namespace, "uk", routing_key)
    send_event(graphapi_post, namespace, routing_key, "alice")
    event_id = get_listeners(graphapi_post)[0]["events"][0]["uuid"]
    silence_event(graphapi_post, event_id)
    unsilence_event(graphapi_post, event_id)
    event = fetch_event(graphapi_post, listener)
    assert event["subject"] == "alice"
