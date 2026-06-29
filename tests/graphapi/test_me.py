# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest

from mora.graphapi.actor import HardcodedActor

from ..conftest import BRUCE_UUID
from ..conftest import GraphAPIPost
from ..conftest import SetAuth
from ..conftest import admin_auth


@pytest.fixture
def declare_namespace(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], str]:
    def inner(input: dict[str, Any]) -> str:
        namespace_declare_mutation = """
          mutation NamespaceDeclare($input: NamespaceCreateInput!) {
            event_namespace_declare(input: $input) {
              name
            }
          }
        """
        response = graphapi_post(namespace_declare_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["event_namespace_declare"]["name"]

    return inner


@pytest.fixture
def delete_namespace(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], bool]:
    def inner(input: dict[str, Any]) -> bool:
        namespace_delete_mutation = """
          mutation NamespaceDelete($input: NamespaceDeleteInput!) {
            event_namespace_delete(input: $input)
          }
        """
        response = graphapi_post(namespace_delete_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["event_namespace_delete"]

    return inner


@pytest.fixture
def read_my_namespaces(
    graphapi_post: GraphAPIPost,
) -> Callable[[], set[UUID]]:
    def inner() -> set[UUID]:
        my_listener_query = """
            query MyNamespaces {
              me {
                actor {
                  event_namespaces {
                    name
                  }
                }
              }
            }
        """
        response = graphapi_post(my_listener_query)
        assert response.errors is None
        assert response.data
        return {
            namespace["name"]
            for namespace in response.data["me"]["actor"]["event_namespaces"]
        }

    return inner


@pytest.fixture
def declare_listener(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        listener_declare_mutation = """
          mutation ListenerDeclare($input: ListenerCreateInput!) {
            event_listener_declare(input: $input) {
              uuid
            }
          }
        """
        response = graphapi_post(listener_declare_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["event_listener_declare"]["uuid"])

    return inner


@pytest.fixture
def delete_listener(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], bool]:
    def inner(input: dict[str, Any]) -> bool:
        listener_delete_mutation = """
          mutation ListenerDelete($input: ListenerDeleteInput!) {
            event_listener_delete(input: $input)
          }
        """
        response = graphapi_post(listener_delete_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["event_listener_delete"]

    return inner


@pytest.fixture
def read_my_listeners(
    graphapi_post: GraphAPIPost,
) -> Callable[[], set[UUID]]:
    def inner() -> set[UUID]:
        my_listener_query = """
            query MyListeners {
              me {
                actor {
                  event_listeners {
                    uuid
                  }
                }
              }
            }
        """
        response = graphapi_post(my_listener_query)
        assert response.errors is None
        assert response.data
        return {
            UUID(listener["uuid"])
            for listener in response.data["me"]["actor"]["event_listeners"]
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_token_information(graphapi_post: GraphAPIPost) -> None:
    me_query = """
        query WhoAmI {
          me {
            actor {
              uuid
              ... on UnknownActor {
                __typename
                error
              }
            }
            email
            roles
            username
          }
        }
    """
    response = graphapi_post(me_query)
    assert response.errors is None
    assert response.data

    token = await admin_auth()

    assert response.data == {
        "me": {
            "actor": {
                "uuid": str(token.uuid),
                "__typename": "UnknownActor",
                "error": ANY,
            },
            "roles": sorted(token.realm_access.roles),
            "username": token.preferred_username,
            "email": token.email,
        }
    }
    error = response.data["me"]["actor"]["error"]
    assert "The actor could not be translated." in error


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_my_namespaces(
    declare_namespace: Callable[[dict[str, Any]], str],
    delete_namespace: Callable[[dict[str, Any]], bool],
    read_my_namespaces: Callable[[], set[str]],
) -> None:
    # No namespaces at start
    assert read_my_namespaces() == set()

    # Declare a namespace and check that we can see it
    ldap = declare_namespace({"name": "LDAP"})
    assert read_my_namespaces() == {ldap}

    # Redeclare the namespace and check that it only occurs once
    ldap_redeclare = declare_namespace({"name": "LDAP"})
    assert ldap == ldap_redeclare
    assert read_my_namespaces() == {ldap}

    # Declare another namespace and check that we can see both
    ad = declare_namespace({"name": "AD"})
    assert read_my_namespaces() == {ldap, ad}

    # Get rid of AD and check that we can only see LDAP
    deleted = delete_namespace({"name": ad})
    assert deleted is True
    assert read_my_namespaces() == {ldap}

    # Redeclare the deleted AD namespace and check we can see both again
    ad_redeclare = declare_namespace({"name": "AD"})
    assert ad == ad_redeclare
    assert read_my_namespaces() == {ldap, ad}

    # Tear down and check that namespaces disappear
    deleted = delete_namespace({"name": ldap})
    assert deleted is True
    assert read_my_namespaces() == {ad}

    deleted = delete_namespace({"name": ad})
    assert deleted is True
    assert read_my_namespaces() == set()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_my_listeners(
    declare_namespace: Callable[[dict[str, Any]], str],
    read_my_namespaces: Callable[[], set[str]],
    declare_listener: Callable[[dict[str, Any]], UUID],
    delete_listener: Callable[[dict[str, Any]], bool],
    read_my_listeners: Callable[[], set[UUID]],
) -> None:
    # No namespaces nor listeners at start
    assert read_my_namespaces() == set()
    assert read_my_listeners() == set()

    # Declare a BorgerPC namespace and a listener
    bpc_ns = declare_namespace({"name": "borgerpc"})
    assert read_my_namespaces() == {bpc_ns}

    # Declare a listener on the "mo" namespace
    mo2bpc = declare_listener({"routing_key": "person", "user_key": "mo2bpc"})
    assert read_my_listeners() == {mo2bpc}

    # Redeclare the listener and check that it only occurs once
    mo2bpc_redeclare = declare_listener({"routing_key": "person", "user_key": "mo2bpc"})
    assert mo2bpc == mo2bpc_redeclare
    assert read_my_listeners() == {mo2bpc}

    # Declare a listener on the "bpc" namespace
    bpc2mo = declare_listener(
        {"namespace": bpc_ns, "routing_key": "person", "user_key": "mo"}
    )
    assert read_my_listeners() == {mo2bpc, bpc2mo}

    # Get rid of mo2bpc and check that we can only see bpc2mo
    deleted = delete_listener({"uuid": str(mo2bpc)})
    assert deleted is True
    assert read_my_listeners() == {bpc2mo}

    # Tear down bpc2mo and check that we end up with no listenres
    deleted = delete_listener({"uuid": str(bpc2mo)})
    assert deleted is True
    assert read_my_listeners() == set()
    assert read_my_namespaces() == {bpc_ns}


DECLARE_POLICY = """
  mutation DeclarePolicy($input: PolicyDeclareInput!) {
    policy_declare(input: $input) {
      uuid
    }
  }
"""

DECLARE_ACTOR = """
  mutation DeclareActor($input: PolicyActorDeclareInput!) {
    policy_actor_declare(input: $input) {
      uuid
    }
  }
"""

MY_POLICIES = """
    query MyPolicies($filter: ActorBoundPolicyFilter) {
      me {
        policies(filter: $filter) {
          uuid
          name
        }
      }
    }
"""


@pytest.fixture
def create_policy(
    graphapi_post: GraphAPIPost,
) -> Callable[..., str]:
    """Create a policy with a single actor binding and return its UUID."""

    def inner(
        name: str,
        kind: str,
        value: str,
        start: str = "2024-01-01T00:00:00+00:00",
        end: str | None = None,
    ) -> str:
        response = graphapi_post(
            DECLARE_POLICY,
            variables={"input": {"name": name, "start": start, "end": end}},
        )
        assert response.errors is None
        assert response.data
        uuid = response.data["policy_declare"]["uuid"]

        response = graphapi_post(
            DECLARE_ACTOR,
            variables={"input": {"policy": uuid, "kind": kind, "value": value}},
        )
        assert response.errors is None
        return uuid

    return inner


@pytest.fixture
def read_my_policies(
    graphapi_post: GraphAPIPost,
) -> Callable[..., set[str]]:
    def inner(filter: dict[str, Any] | None = None) -> set[str]:
        response = graphapi_post(MY_POLICIES, variables={"filter": filter})
        assert response.errors is None
        assert response.data
        return {policy["name"] for policy in response.data["me"]["policies"]}

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_my_policies(
    create_policy: Callable[..., str],
    read_my_policies: Callable[..., set[str]],
) -> None:
    # The admin token (username "bruce", role "admin") sees the bootstrap
    # "Policy Administrator" policy, which is hard-bound to the "admin" role.
    assert read_my_policies() == {"Policy Administrator"}

    # A policy bound to our username, uuid or one of our roles becomes visible.
    by_username = create_policy("by-username", "username", "bruce")
    create_policy("by-uuid", "uuid", str(BRUCE_UUID))
    create_policy("by-role", "role", "owner")

    # A policy bound to attributes we don't have stays hidden.
    create_policy("not-mine", "role", "nobody")

    mine = {"Policy Administrator", "by-username", "by-uuid", "by-role"}
    assert read_my_policies() == mine

    # The caller can restrict the (already actor-seeded) result by policy UUID.
    assert read_my_policies(filter={"uuids": [by_username]}) == {"by-username"}

    # ... and by validity window. An expired policy for us is applicable in
    # general (no window) but excluded by a "now" window.
    create_policy(
        "expired",
        "username",
        "bruce",
        start="2020-01-01T00:00:00+00:00",
        end="2021-01-01T00:00:00+00:00",
    )
    assert "expired" in read_my_policies()
    now = "2026-06-29T00:00:00+00:00"
    current = read_my_policies(filter={"start": now, "end": now})
    assert current == mine
    assert "expired" not in current


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "name,token_uuid", [(entity.name, entity.value) for entity in HardcodedActor]
)
async def test_token_information_special(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    name: str,
    token_uuid: UUID,
) -> None:
    set_auth(None, token_uuid)

    me_query = """
        query WhoAmI {
          me {
            actor {
              uuid
              ... on SpecialActor {
                __typename
                key
              }
            }
            email
            roles
            username
          }
        }
    """
    response = graphapi_post(me_query)
    assert response.errors is None
    assert response.data

    assert response.data == {
        "me": {
            "actor": {
                "uuid": str(token_uuid),
                "__typename": "SpecialActor",
                "key": name,
            },
            "roles": [],
            "username": "bruce",
            "email": "bruce@kung.fu",
        }
    }
