# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.db.policies import POLICYADMIN_UUID
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost

POLICYADMIN = str(POLICYADMIN_UUID)

DECLARE_POLICY = """
  mutation DeclarePolicy($input: PolicyDeclareInput!) {
    policy_declare(input: $input) {
      uuid
      name
      description
      start
      end
    }
  }
"""

READ_POLICIES = """
  query ReadPolicies {
    policies {
      objects {
        uuid
        name
        description
        start
        end
      }
    }
  }
"""

PAGINATE_POLICIES = """
  query PaginatePolicies($limit: int, $cursor: Cursor) {
    policies(limit: $limit, cursor: $cursor) {
      objects {
        uuid
        name
      }
      page_info {
        next_cursor
      }
    }
  }
"""

FILTER_POLICIES = """
  query FilterPolicies($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        name
      }
    }
  }
"""

DELETE_POLICY = """
  mutation DeletePolicy($uuid: UUID!) {
    policy_delete(input: { uuid: $uuid })
  }
"""

ADD_ACTOR = """
  mutation AddActor($input: PolicyActorAddInput!) {
    policy_actor_add(input: $input) {
      uuid
      kind
      value
    }
  }
"""

DELETE_ACTOR = """
  mutation DeleteActor($uuid: UUID!) {
    policy_actor_delete(input: { uuid: $uuid })
  }
"""

READ_POLICY_ACTORS = """
  query ReadPolicyActors($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        actors {
          uuid
          kind
          value
        }
      }
    }
  }
"""

FILTER_BY_ACTOR = """
  query FilterByActor($filter: PolicyFilter) {
    policies(filter: $filter) {
      objects {
        uuid
        name
      }
    }
  }
"""

NOT_FOUND_UUID = "d0d19f81-36e0-46bd-9be5-49d31b1e15a7"


def declare_policy(graphapi_post: GraphAPIPost, **input) -> GQLResponse:
    return graphapi_post(DECLARE_POLICY, variables={"input": input})


def read_policies(graphapi_post: GraphAPIPost) -> list[dict]:
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None
    return response.data["policies"]["objects"]


def create_policy(graphapi_post: GraphAPIPost, name: str) -> str:
    response = declare_policy(
        graphapi_post, name=name, start="2024-01-01T00:00:00+00:00"
    )
    assert response.errors is None
    return response.data["policy_declare"]["uuid"]


def add_actor(
    graphapi_post: GraphAPIPost, policy: str, kind: str, value: str
) -> str:
    response = graphapi_post(
        ADD_ACTOR,
        variables={"input": {"policy": policy, "kind": kind, "value": value}},
    )
    assert response.errors is None
    return response.data["policy_actor_add"]["uuid"]


def policy_names_for_filter(graphapi_post: GraphAPIPost, filter_value) -> set[str]:
    response = graphapi_post(FILTER_BY_ACTOR, variables={"filter": filter_value})
    assert response.errors is None
    return {obj["name"] for obj in response.data["policies"]["objects"]}


@pytest.mark.integration_test
async def test_policyadmin_is_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The migration inserts the policyadmin policy, so it is always present.
    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert POLICYADMIN in policies
    assert policies[POLICYADMIN]["name"] == "Policy Administrator"


@pytest.mark.integration_test
async def test_policyadmin_cannot_be_deleted(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = graphapi_post(DELETE_POLICY, variables={"uuid": POLICYADMIN})
    assert response.errors is not None

    # It is still there.
    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_create_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = declare_policy(
        graphapi_post,
        name="GDPR",
        description="Data protection policy",
        start="2024-01-01T00:00:00+00:00",
    )
    assert response.errors is None
    created = response.data["policy_declare"]
    assert created["name"] == "GDPR"
    assert created["description"] == "Data protection policy"
    assert created["end"] is None

    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert created["uuid"] in policies
    assert policies[created["uuid"]]["name"] == "GDPR"
    # The bootstrap policy coexists with the created one.
    assert POLICYADMIN in policies


@pytest.mark.integration_test
async def test_policy_declare_updates_existing(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    created = declare_policy(
        graphapi_post, name="Initial", start="2024-01-01T00:00:00+00:00"
    )
    uuid = created.data["policy_declare"]["uuid"]

    updated = declare_policy(
        graphapi_post,
        uuid=uuid,
        name="Renamed",
        description="now with a description",
        start="2024-01-01T00:00:00+00:00",
        end="2025-01-01T00:00:00+00:00",
    )
    assert updated.errors is None
    obj = updated.data["policy_declare"]
    assert obj["uuid"] == uuid
    assert obj["name"] == "Renamed"
    assert obj["description"] == "now with a description"
    assert obj["end"] is not None

    # Declaring with a uuid updates rather than creates: bootstrap + the one.
    assert len(read_policies(graphapi_post)) == 2


@pytest.mark.integration_test
async def test_policy_declare_unknown_uuid_fails(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = declare_policy(
        graphapi_post,
        uuid=NOT_FOUND_UUID,
        name="ghost",
        start="2024-01-01T00:00:00+00:00",
    )
    assert response.errors is not None


@pytest.mark.integration_test
async def test_policy_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    created = declare_policy(
        graphapi_post, name="ToDelete", start="2024-01-01T00:00:00+00:00"
    )
    uuid = created.data["policy_declare"]["uuid"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert uuid not in uuids
    # Deleting a normal policy leaves the bootstrap policy untouched.
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_filter_by_uuid(graphapi_post: GraphAPIPost, empty_db) -> None:
    created = declare_policy(
        graphapi_post, name="Filtered", start="2024-01-01T00:00:00+00:00"
    )
    uuid = created.data["policy_declare"]["uuid"]

    response = graphapi_post(FILTER_POLICIES, variables={"uuids": [uuid]})
    assert response.errors is None
    objects = response.data["policies"]["objects"]
    assert len(objects) == 1
    assert objects[0]["uuid"] == uuid
    assert objects[0]["name"] == "Filtered"


@pytest.mark.integration_test
async def test_policy_pagination(graphapi_post: GraphAPIPost, empty_db) -> None:
    # Create a handful of policies to page through (plus the bootstrap one).
    created: set[str] = set()
    for i in range(5):
        response = declare_policy(
            graphapi_post, name=f"policy-{i}", start="2024-01-01T00:00:00+00:00"
        )
        assert response.errors is None
        created.add(response.data["policy_declare"]["uuid"])

    # Page through them two at a time using the keyset cursor.
    seen: list[str] = []
    cursor = None
    for _ in range(10):  # safety bound to avoid an infinite loop
        response = graphapi_post(
            PAGINATE_POLICIES, variables={"limit": 2, "cursor": cursor}
        )
        assert response.errors is None
        page = response.data["policies"]
        seen.extend(obj["uuid"] for obj in page["objects"])
        cursor = page["page_info"]["next_cursor"]
        if cursor is None:
            break
    else:  # pragma: no cover
        raise AssertionError("pagination did not terminate")

    # Every created policy plus the bootstrap policy was returned exactly once.
    assert len(seen) == 6
    assert created <= set(seen)
    assert POLICYADMIN in seen


ACTOR_UUID = "11111111-1111-1111-1111-111111111111"


@pytest.mark.integration_test
async def test_policy_actor_add_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "with-actors")
    add_actor(graphapi_post, policy, "role", "admin")
    add_actor(graphapi_post, policy, "username", "alice")

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    actors = response.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("username", "alice"),
    }


@pytest.mark.integration_test
async def test_policy_actor_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    policy = create_policy(graphapi_post, "with-actor")
    actor_uuid = add_actor(graphapi_post, policy, "role", "admin")

    deleted = graphapi_post(DELETE_ACTOR, variables={"uuid": actor_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_actor_delete"] is True

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    assert response.data["policies"]["objects"][0]["actors"] == []


@pytest.mark.integration_test
async def test_policy_actor_filter_cases(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # role-policy is bound to role "admin"; user-policy is bound to username
    # "alice" and a specific actor uuid. The bootstrap "Policy Administrator"
    # has no actors.
    role_policy = create_policy(graphapi_post, "role-policy")
    add_actor(graphapi_post, role_policy, "role", "admin")
    user_policy = create_policy(graphapi_post, "user-policy")
    add_actor(graphapi_post, user_policy, "username", "alice")
    add_actor(graphapi_post, user_policy, "uuid", ACTOR_UUID)

    everything = {"role-policy", "user-policy", "Policy Administrator"}
    bound = {"role-policy", "user-policy"}

    # No actor constraint -> all policies (incl. the actor-less bootstrap one).
    assert {p["name"] for p in read_policies(graphapi_post)} == everything  # omitted
    assert policy_names_for_filter(graphapi_post, None) == everything  # null
    assert policy_names_for_filter(graphapi_post, {}) == everything  # {}
    assert policy_names_for_filter(graphapi_post, {"actor": None}) == everything

    # Empty actor filter -> policies that have *any* actor (excludes bootstrap).
    assert policy_names_for_filter(graphapi_post, {"actor": {}}) == bound

    # Matching by a single attribute.
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["admin"]}}
    ) == {"role-policy"}
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"usernames": ["alice"]}}
    ) == {"user-policy"}
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"uuids": [ACTOR_UUID]}}
    ) == {"user-policy"}

    # An empty list matches nothing for that attribute.
    assert policy_names_for_filter(graphapi_post, {"actor": {"roles": []}}) == set()

    # Multiple attributes are OR'ed together.
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["admin"], "usernames": ["alice"]}}
    ) == bound

    # No actor matches a non-existent role.
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["nobody"]}}
    ) == set()
