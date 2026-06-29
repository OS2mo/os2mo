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

DECLARE_ACTOR = """
  mutation DeclareActor($input: PolicyActorDeclareInput!) {
    policy_actor_declare(input: $input) {
      uuid
      kind
      value
    }
  }
"""

DECLARE_ACTORS = """
  mutation DeclareActors($input: PolicyActorsDeclareInput!) {
    policy_actors_declare(input: $input) {
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


def declare_actor(
    graphapi_post: GraphAPIPost, policy: str, kind: str, value: str
) -> str:
    response = graphapi_post(
        DECLARE_ACTOR,
        variables={"input": {"policy": policy, "kind": kind, "value": value}},
    )
    assert response.errors is None
    return response.data["policy_actor_declare"]["uuid"]


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
    baseline = len(read_policies(graphapi_post))
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

    # Declaring with a uuid updates rather than creates: just one new policy.
    assert len(read_policies(graphapi_post)) == baseline + 1


@pytest.mark.integration_test
async def test_policy_declare_with_uuid_creates(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Declaring with a client-supplied UUID that does not exist creates it (this
    # is what lets the create flow generate the UUID up front).
    response = declare_policy(
        graphapi_post,
        uuid=NOT_FOUND_UUID,
        name="client-uuid",
        start="2024-01-01T00:00:00+00:00",
    )
    assert response.errors is None
    assert response.data["policy_declare"]["uuid"] == NOT_FOUND_UUID

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert NOT_FOUND_UUID in uuids


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
    # Create a handful of policies to page through (plus the bootstrap ones).
    baseline = len(read_policies(graphapi_post))
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

    # Every created policy plus the bootstrap ones was returned exactly once.
    assert len(seen) == baseline + 5
    assert created <= set(seen)
    assert POLICYADMIN in seen


ACTOR_UUID = "11111111-1111-1111-1111-111111111111"


@pytest.mark.integration_test
async def test_policy_actor_declare_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "with-actors")
    declare_actor(graphapi_post, policy, "role", "admin")
    declare_actor(graphapi_post, policy, "username", "alice")

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
    actor_uuid = declare_actor(graphapi_post, policy, "role", "admin")

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
    # "alice" and a specific actor uuid; unbound-policy has no actors. The
    # bootstrap "Policy Administrator" is hard-bound to role "admin".
    role_policy = create_policy(graphapi_post, "role-policy")
    declare_actor(graphapi_post, role_policy, "role", "admin")
    user_policy = create_policy(graphapi_post, "user-policy")
    declare_actor(graphapi_post, user_policy, "username", "alice")
    declare_actor(graphapi_post, user_policy, "uuid", ACTOR_UUID)
    create_policy(graphapi_post, "unbound-policy")

    # The bootstrap "Reader" policy is bound to the "reader" role; the bootstrap
    # "Administrator" policy is still unassigned.
    everything = {
        "role-policy",
        "user-policy",
        "unbound-policy",
        "Policy Administrator",
        "Administrator",
        "Reader",
    }
    has_actor = {"role-policy", "user-policy", "Policy Administrator", "Reader"}
    admins = {"role-policy", "Policy Administrator"}

    # No actor constraint -> all policies (including the actor-less one).
    assert {p["name"] for p in read_policies(graphapi_post)} == everything  # omitted
    assert policy_names_for_filter(graphapi_post, None) == everything  # null
    assert policy_names_for_filter(graphapi_post, {}) == everything  # {}
    assert policy_names_for_filter(graphapi_post, {"actor": None}) == everything

    # Empty actor filter -> policies that have *any* actor (excludes unbound).
    assert policy_names_for_filter(graphapi_post, {"actor": {}}) == has_actor

    # Matching by a single attribute. Both role-policy and the bootstrap policy
    # are bound to "admin".
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["admin"]}}
    ) == admins
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
    ) == admins | {"user-policy"}

    # No actor matches a non-existent role.
    assert policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["nobody"]}}
    ) == set()


@pytest.mark.integration_test
async def test_policyadmin_hard_bound_to_admin_role(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    assert response.errors is None
    actors = response.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("role", "admin")}


@pytest.mark.integration_test
async def test_policyadmin_cannot_be_modified(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Updating the policy itself is rejected.
    update = declare_policy(
        graphapi_post,
        uuid=POLICYADMIN,
        name="Hacked",
        start="2024-01-01T00:00:00+00:00",
    )
    assert update.errors is not None

    # Declaring an actor on it is rejected.
    add = graphapi_post(
        DECLARE_ACTOR,
        variables={
            "input": {"policy": POLICYADMIN, "kind": "username", "value": "mallory"}
        },
    )
    assert add.errors is not None

    # Its hard-bound admin role is unchanged.
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    actors = read.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("role", "admin")}


@pytest.mark.integration_test
async def test_policy_actor_declare_is_idempotent(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    first = declare_actor(graphapi_post, policy, "role", "admin")
    second = declare_actor(graphapi_post, policy, "role", "admin")
    # Declaring the same actor twice returns the same binding, no duplicate.
    assert first == second
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert len(response.data["policies"]["objects"][0]["actors"]) == 1


@pytest.mark.integration_test
async def test_policy_actors_declare_replaces_set(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "username", "value": "alice"},
                ],
            }
        },
    )
    assert response.errors is None
    assert len(response.data["policy_actors_declare"]) == 2

    # Declaring a new set replaces the old one: "alice" is dropped, the uuid
    # actor is added, and "admin" is kept (unchanged).
    again = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "uuid", "value": ACTOR_UUID},
                ],
            }
        },
    )
    assert again.errors is None

    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    actors = read.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("uuid", ACTOR_UUID),
    }

    # Declaring an empty set clears all actors.
    cleared = graphapi_post(
        DECLARE_ACTORS, variables={"input": {"policy": policy, "actors": []}}
    )
    assert cleared.errors is None
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert read.data["policies"]["objects"][0]["actors"] == []


# Rules
# -----

DECLARE_RULE = """
  mutation DeclareRule($input: PolicyRuleDeclareInput!) {
    policy_rule_declare(input: $input) {
      uuid
      type
      field
      condition
    }
  }
"""

DECLARE_RULES = """
  mutation DeclareRules($input: PolicyRulesDeclareInput!) {
    policy_rules_declare(input: $input) {
      uuid
      type
      field
      condition
    }
  }
"""

DELETE_RULE = """
  mutation DeleteRule($uuid: UUID!) {
    policy_rule_delete(input: { uuid: $uuid })
  }
"""

READ_POLICY_RULES = """
  query ReadPolicyRules($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        rules {
          uuid
          type
          field
          condition
        }
      }
    }
  }
"""


def declare_rule(
    graphapi_post: GraphAPIPost,
    policy: str,
    type: str,
    field: str,
    condition: str | None = None,
) -> str:
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": type,
                "field": field,
                "condition": condition,
            }
        },
    )
    assert response.errors is None
    return response.data["policy_rule_declare"]["uuid"]


def read_policy_rules(graphapi_post: GraphAPIPost, uuid: str) -> list[dict]:
    response = graphapi_post(READ_POLICY_RULES, variables={"uuids": [uuid]})
    assert response.errors is None
    return response.data["policies"]["objects"][0]["rules"]


@pytest.mark.integration_test
async def test_policy_rule_declare_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "with-rules")
    declare_rule(graphapi_post, policy, "Query", "policies")
    declare_rule(graphapi_post, policy, "Policy", "*")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"]) for r in rules} == {
        ("Query", "policies"),
        ("Policy", "*"),
    }


@pytest.mark.integration_test
async def test_policy_rule_declare_is_idempotent(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    first = declare_rule(graphapi_post, policy, "Query", "policies")
    second = declare_rule(graphapi_post, policy, "Query", "policies")
    assert first == second
    assert len(read_policy_rules(graphapi_post, policy)) == 1


@pytest.mark.integration_test
async def test_policy_rules_declare_replaces_set(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "policies"},
                    {"type": "Mutation", "field": "policy_declare"},
                ],
            }
        },
    )
    assert response.errors is None
    assert len(response.data["policy_rules_declare"]) == 2

    again = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "policies"},
                    {"type": "Policy", "field": "name"},
                ],
            }
        },
    )
    assert again.errors is None
    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"]) for r in rules} == {
        ("Query", "policies"),
        ("Policy", "name"),
    }

    cleared = graphapi_post(
        DECLARE_RULES, variables={"input": {"policy": policy, "rules": []}}
    )
    assert cleared.errors is None
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policy_rule_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    policy = create_policy(graphapi_post, "p")
    rule_uuid = declare_rule(graphapi_post, policy, "Query", "policies")
    deleted = graphapi_post(DELETE_RULE, variables={"uuid": rule_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_rule_delete"] is True
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policyadmin_rules_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    pairs = {(r["type"], r["field"]) for r in read_policy_rules(graphapi_post, POLICYADMIN)}
    assert ("Query", "policies") in pairs
    assert ("Mutation", "policy_declare") in pairs
    assert ("Mutation", "policy_rules_declare") in pairs


@pytest.mark.integration_test
async def test_policyadmin_rules_cannot_be_modified(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    add = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {"policy": POLICYADMIN, "type": "Query", "field": "employees"}
        },
    )
    assert add.errors is not None
    replace = graphapi_post(
        DECLARE_RULES, variables={"input": {"policy": POLICYADMIN, "rules": []}}
    )
    assert replace.errors is not None


# PBAC permission engine
# ----------------------

READ_EMPLOYEES = """
  query {
    employees {
      objects {
        uuid
      }
    }
  }
"""


@pytest.mark.integration_test
async def test_pbac_admin_can_read_policies(
    graphapi_post: GraphAPIPost, set_settings, empty_db
) -> None:
    # The admin token has the "admin" role, which the bootstrap Policy
    # Administrator is bound to and which grants Query.policies.
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None


@pytest.mark.integration_test
async def test_pbac_denies_without_grant(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    set_auth(role="nobody", user_uuid="11111111-1111-1111-1111-111111111111")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")
    response = graphapi_post(READ_POLICIES)
    assert response.errors is not None


@pytest.mark.integration_test
async def test_pbac_grant_via_policy(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    # As admin (RBAC), grant "bruce" read access to the employees collection.
    policy = create_policy(graphapi_post, "bruce-reader")
    declare_actor(graphapi_post, policy, "username", "bruce")
    declare_rule(graphapi_post, policy, "Query", "employees")

    # Become bruce (no admin role) and switch to PBAC.
    set_auth(preferred_username="bruce")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None

    # bruce was not granted the policies collection.
    denied = graphapi_post(READ_POLICIES)
    assert denied.errors is not None


@pytest.mark.integration_test
async def test_pbac_grant_respects_validity(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    # A policy that has already ended does not grant access.
    response = declare_policy(
        graphapi_post,
        name="expired",
        start="2000-01-01T00:00:00+00:00",
        end="2001-01-01T00:00:00+00:00",
    )
    policy = response.data["policy_declare"]["uuid"]
    declare_actor(graphapi_post, policy, "username", "bruce")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(preferred_username="bruce")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    denied = graphapi_post(READ_EMPLOYEES)
    assert denied.errors is not None


@pytest.mark.integration_test
async def test_policy_actor_all_matches_any_filter(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "everyone-policy")
    # An "all" actor has no value and matches every actor.
    declare_actor(graphapi_post, policy, "all", "")

    # It is returned regardless of the queried actor attributes.
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["whatever"]}}
    )
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"usernames": ["nobody"]}}
    )
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"uuids": [ACTOR_UUID]}}
    )
    # ... and by the existence filter.
    assert "everyone-policy" in policy_names_for_filter(graphapi_post, {"actor": {}})


@pytest.mark.integration_test
async def test_pbac_all_actor_grants_everyone(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    policy = create_policy(graphapi_post, "everyone-reader")
    declare_actor(graphapi_post, policy, "all", "")
    declare_rule(graphapi_post, policy, "Query", "employees")

    # A token with a non-matching role/uuid/username still gets access.
    set_auth(role="nobody", user_uuid="22222222-2222-2222-2222-222222222222")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None


@pytest.mark.integration_test
async def test_administrator_and_reader_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    by_name = {p["name"]: p["uuid"] for p in read_policies(graphapi_post)}
    assert "Administrator" in by_name
    assert "Reader" in by_name

    admin_rules = {
        (r["type"], r["field"])
        for r in read_policy_rules(graphapi_post, by_name["Administrator"])
    }
    assert admin_rules == {("Query", "*"), ("Mutation", "*")}

    reader_rules = {
        (r["type"], r["field"])
        for r in read_policy_rules(graphapi_post, by_name["Reader"])
    }
    assert reader_rules == {("Query", "*")}

    def actors_of(name: str) -> set:
        objects = graphapi_post(
            READ_POLICY_ACTORS, variables={"uuids": [by_name[name]]}
        ).data["policies"]["objects"][0]["actors"]
        return {(a["kind"], a["value"]) for a in objects}

    # Reader is bound to the "reader" role.
    assert actors_of("Reader") == {("role", "reader")}
    # Administrator starts unassigned.
    assert actors_of("Administrator") == set()


@pytest.mark.integration_test
async def test_administrator_policy_is_removable(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Unlike the policyadmin policy, Administrator is a normal, removable policy
    # (and deleting it also removes its rules).
    by_name = {p["name"]: p["uuid"] for p in read_policies(graphapi_post)}
    admin_uuid = by_name["Administrator"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": admin_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    # Deletion succeeds (its rules are removed too, so no FK violation).
    assert admin_uuid not in {p["uuid"] for p in read_policies(graphapi_post)}


@pytest.mark.integration_test
async def test_policy_delete_removes_actors_and_rules(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "to-delete")
    declare_actor(graphapi_post, policy, "role", "x")
    declare_rule(graphapi_post, policy, "Query", "employees")

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": policy})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True
    assert policy not in {p["uuid"] for p in read_policies(graphapi_post)}


# Rule conditions (CEL)
# ---------------------


@pytest.mark.integration_test
async def test_policy_rule_declare_with_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "conditional")
    declare_rule(
        graphapi_post,
        policy,
        "Query",
        "employees",
        condition='"admin" in token.roles',
    )

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", '"admin" in token.roles')
    }


@pytest.mark.integration_test
async def test_policy_rule_empty_condition_is_unconditional(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # An empty-string condition is normalised to null (unconditional).
    policy = create_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="")
    rules = read_policy_rules(graphapi_post, policy)
    assert rules[0]["condition"] is None


@pytest.mark.integration_test
async def test_policy_rule_condition_distinct_per_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The same (type, field) may carry several conditions (each its own rule),
    # while re-declaring an identical (type, field, condition) is idempotent.
    policy = create_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees")  # unconditional
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="false")
    # Idempotent re-declares.
    declare_rule(graphapi_post, policy, "Query", "employees")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", None),
        ("Query", "employees", "true"),
        ("Query", "employees", "false"),
    }


@pytest.mark.integration_test
async def test_policy_rule_declare_rejects_invalid_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": "Query",
                "field": "employees",
                "condition": "this is (not valid CEL",
            }
        },
    )
    assert response.errors is not None
    # Nothing was stored.
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policy_rules_declare_keys_on_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The full-replace mutator treats (type, field, condition) as the identity.
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "employees"},
                    {
                        "type": "Query",
                        "field": "employees",
                        "condition": '"admin" in token.roles',
                    },
                ],
            }
        },
    )
    assert response.errors is None
    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", None),
        ("Query", "employees", '"admin" in token.roles'),
    }


@pytest.mark.integration_test
async def test_pbac_condition_grants_when_true(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    # bruce's policy only grants employees when the condition holds.
    policy = create_policy(graphapi_post, "bruce-reader")
    declare_actor(graphapi_post, policy, "username", "bruce")
    declare_rule(
        graphapi_post,
        policy,
        "Query",
        "employees",
        condition='token.preferred_username == "bruce"',
    )

    set_auth(preferred_username="bruce")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None


@pytest.mark.integration_test
async def test_pbac_condition_denies_when_false(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    # The actor matches the policy, but the condition does not hold.
    policy = create_policy(graphapi_post, "bruce-reader")
    declare_actor(graphapi_post, policy, "username", "bruce")
    declare_rule(
        graphapi_post,
        policy,
        "Query",
        "employees",
        condition='token.preferred_username == "alice"',
    )

    set_auth(preferred_username="bruce")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    denied = graphapi_post(READ_EMPLOYEES)
    assert denied.errors is not None


@pytest.mark.integration_test
async def test_pbac_unconditional_rule_grants_despite_false_condition(
    graphapi_post: GraphAPIPost, set_settings, set_auth, empty_db
) -> None:
    # Two rules for the same field: one with a false condition, one
    # unconditional. The unconditional one grants access regardless.
    policy = create_policy(graphapi_post, "bruce-reader")
    declare_actor(graphapi_post, policy, "username", "bruce")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="false")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(preferred_username="bruce")
    set_settings(POLICY_RBAC="true", OS2MO_AUTH="true")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None
