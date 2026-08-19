# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy CRUD API: the `policies` query and the policy mutators."""

import json
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from mora.db.policies import DELETE_PROTECTED_POLICIES
from mora.db.policies import POLICYADMIN_UUID
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

POLICYADMIN = str(POLICYADMIN_UUID)

CREATE_POLICY = """
  mutation CreatePolicy($input: PolicyCreateInput!) {
    policy_create(input: $input) {
      uuid
      name
      description
      active
    }
  }
"""

UPDATE_POLICY = """
  mutation UpdatePolicy($input: PolicyUpdateInput!) {
    policy_update(input: $input) {
      uuid
      name
      description
      active
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
        active
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

DECLARE_RULE = """
  mutation DeclareRule($input: PolicyRuleDeclareInput!) {
    policy_rule_declare(input: $input) {
      uuid
      type
      field
      condition
      filter
    }
  }
"""

# The rule selection a caller holding only declare_policy may make: a rule's CEL
# expressions take read_policy
DECLARE_RULE_SHAPE_ONLY = """
  mutation DeclareRule($input: PolicyRuleDeclareInput!) {
    policy_rule_declare(input: $input) {
      uuid
      type
      field
    }
  }
"""

READ_EMPLOYEES = "query { employees { objects { uuid } } }"

NOT_FOUND_UUID = "d0d19f81-36e0-46bd-9be5-49d31b1e15a7"

# The conditions the bootstrap policyadmin rules gate on
READ_CONDITION = '"read_policy" in token.roles'
DECLARE_CONDITION = '"declare_policy" in token.roles'


def create_policy(graphapi_post: GraphAPIPost, **input: Any) -> GQLResponse:
    return graphapi_post(CREATE_POLICY, variables={"input": input})


def update_policy(graphapi_post: GraphAPIPost, **input: Any) -> GQLResponse:
    return graphapi_post(UPDATE_POLICY, variables={"input": input})


def read_policies(graphapi_post: GraphAPIPost) -> list[dict]:
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None
    return response.data["policies"]["objects"]


def new_policy(graphapi_post: GraphAPIPost, name: str) -> str:
    """Create a policy through the API, returning its uuid."""
    response = create_policy(graphapi_post, name=name)
    assert response.errors is None
    return response.data["policy_create"]["uuid"]


def declare_actor(
    graphapi_post: GraphAPIPost, policy: str, kind: str, value: str
) -> str:
    response = graphapi_post(
        DECLARE_ACTOR,
        variables={"input": {"policy": policy, "kind": kind, "value": value}},
    )
    assert response.errors is None
    return response.data["policy_actor_declare"]["uuid"]


def policy_names_for_filter(
    graphapi_post: GraphAPIPost, filter_value: dict | None
) -> set[str]:
    response = graphapi_post(FILTER_BY_ACTOR, variables={"filter": filter_value})
    assert response.errors is None
    return {obj["name"] for obj in response.data["policies"]["objects"]}


# Policies
# --------


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_is_bootstrapped(graphapi_post: GraphAPIPost) -> None:
    # The migration inserts the policyadmin policy, so it is always present.
    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert POLICYADMIN in policies
    assert policies[POLICYADMIN]["name"] == "Policy Administrator"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_cannot_be_deleted(graphapi_post: GraphAPIPost) -> None:
    response = graphapi_post(DELETE_POLICY, variables={"uuid": POLICYADMIN})
    assert response.errors is not None

    # It is still there.
    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_create_and_read(graphapi_post: GraphAPIPost) -> None:
    response = create_policy(
        graphapi_post,
        name="GDPR",
        description="Data protection policy",
    )
    assert response.errors is None
    created = response.data["policy_create"]
    assert created["name"] == "GDPR"
    assert created["description"] == "Data protection policy"
    # Policies default to active on create.
    assert created["active"] is True

    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert created["uuid"] in policies
    assert policies[created["uuid"]]["name"] == "GDPR"
    # The bootstrap policy coexists with the created one.
    assert POLICYADMIN in policies


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_update_changes_fields(graphapi_post: GraphAPIPost) -> None:
    baseline = len(read_policies(graphapi_post))
    uuid = new_policy(graphapi_post, "Initial")

    updated = update_policy(
        graphapi_post,
        uuid=uuid,
        name="Renamed",
        description="now with a description",
        active=False,
    )
    assert updated.errors is None
    obj = updated.data["policy_update"]
    assert obj["uuid"] == uuid
    assert obj["name"] == "Renamed"
    assert obj["description"] == "now with a description"
    assert obj["active"] is False

    # Updating does not create: just the one new policy.
    assert len(read_policies(graphapi_post)) == baseline + 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_update_is_partial(graphapi_post: GraphAPIPost) -> None:
    # An omitted field is left alone, so toggling `active` needs nothing else.
    uuid = new_policy(graphapi_post, "Keep")
    described = update_policy(graphapi_post, uuid=uuid, description="a description")
    assert described.errors is None

    response = update_policy(graphapi_post, uuid=uuid, active=False)
    assert response.errors is None
    obj = response.data["policy_update"]
    assert obj["active"] is False
    # Untouched by the activation change.
    assert obj["name"] == "Keep"
    assert obj["description"] == "a description"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_update_unknown_uuid_errors(graphapi_post: GraphAPIPost) -> None:
    # Updating a policy that does not exist is an error rather than a create, so
    # a mistyped uuid cannot silently introduce a new policy.
    response = update_policy(graphapi_post, uuid=NOT_FOUND_UUID, name="typo")
    assert response.errors is not None

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert NOT_FOUND_UUID not in uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_delete(graphapi_post: GraphAPIPost) -> None:
    created = create_policy(graphapi_post, name="ToDelete")
    uuid = created.data["policy_create"]["uuid"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert uuid not in uuids
    # Deleting a normal policy leaves the bootstrap policy untouched.
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_filter_by_uuid(graphapi_post: GraphAPIPost) -> None:
    created = create_policy(graphapi_post, name="Filtered")
    uuid = created.data["policy_create"]["uuid"]

    response = graphapi_post(FILTER_POLICIES, variables={"uuids": [uuid]})
    assert response.errors is None
    objects = response.data["policies"]["objects"]
    assert len(objects) == 1
    assert objects[0]["uuid"] == uuid
    assert objects[0]["name"] == "Filtered"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_pagination(graphapi_post: GraphAPIPost) -> None:
    # Create a handful of policies to page through (plus the bootstrap ones).
    baseline = len(read_policies(graphapi_post))
    created: set[str] = set()
    for i in range(5):
        response = create_policy(graphapi_post, name=f"policy-{i}")
        assert response.errors is None
        created.add(response.data["policy_create"]["uuid"])

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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_builtin_policies_cannot_be_deleted(graphapi_post: GraphAPIPost) -> None:
    # Every migration-seeded policy is delete-protected.
    policies = read_policies(graphapi_post)
    assert {UUID(p["uuid"]) for p in policies} == set(DELETE_PROTECTED_POLICIES)

    for policy in policies:
        deleted = graphapi_post(DELETE_POLICY, variables={"uuid": policy["uuid"]})
        assert deleted.errors is not None

    # They are all still there.
    assert {p["uuid"] for p in read_policies(graphapi_post)} == {
        p["uuid"] for p in policies
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_builtin_policy_can_be_deactivated(graphapi_post: GraphAPIPost) -> None:
    # A built-in policy cannot be deleted, but it can be switched off -- and
    # back on.
    owner = one(p for p in read_policies(graphapi_post) if p["name"] == "Owner")
    assert owner["active"] is True

    for active in (False, True):
        # A partial update, so no need to echo name/description back.
        response = update_policy(graphapi_post, uuid=owner["uuid"], active=active)
        assert response.errors is None
        assert response.data["policy_update"]["active"] is active


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_builtin_policy_cannot_be_modified(graphapi_post: GraphAPIPost) -> None:
    owner = one(p for p in read_policies(graphapi_post) if p["name"] == "Owner")

    # Renaming (or redescribing) a built-in policy is rejected.
    renamed = update_policy(graphapi_post, uuid=owner["uuid"], name="Pwner")
    assert renamed.errors is not None

    # So is changing its actors...
    add_actor = graphapi_post(
        DECLARE_ACTOR,
        variables={
            "input": {"policy": owner["uuid"], "kind": "role", "value": "mallory"}
        },
    )
    assert add_actor.errors is not None

    # ... or its rules.
    add_rule = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {"policy": owner["uuid"], "type": "Query", "field": "employees"}
        },
    )
    assert add_rule.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_delete_removes_actors_and_rules(
    graphapi_post: GraphAPIPost,
) -> None:
    policy = new_policy(graphapi_post, "to-delete")
    declare_actor(graphapi_post, policy, "role", "x")
    declare_rule(graphapi_post, policy, "Query", "employees")

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": policy})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True
    assert policy not in {p["uuid"] for p in read_policies(graphapi_post)}


# Actors
# ------


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actor_declare_and_read(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "with-actors")
    declare_actor(graphapi_post, policy, "role", "admin")
    declare_actor(graphapi_post, policy, "role", "reader")

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    actors = response.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("role", "reader"),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actor_delete(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "with-actor")
    actor_uuid = declare_actor(graphapi_post, policy, "role", "admin")

    deleted = graphapi_post(DELETE_ACTOR, variables={"uuid": actor_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_actor_delete"] is True

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    assert response.data["policies"]["objects"][0]["actors"] == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actor_filter_cases(graphapi_post: GraphAPIPost) -> None:
    # The bootstrap "RBAC", "Public", "Introspection" and "Policy
    # Administrator" policies each have an "all" actor that matches every
    # role-based actor filter (covered by
    # test_policy_actor_all_matches_any_filter). Exclude them from the observed
    # sets so these cases isolate role-based matching. They are not deleted: the
    # "Public" policy grants the Policy fields this test reads.
    catch_all = {"RBAC", "Public", "Introspection", "Policy Administrator"}

    def names_for(filter: dict | None) -> set[str]:
        return policy_names_for_filter(graphapi_post, filter) - catch_all

    # role-policy is bound to role "admin"; reader-policy to role "reader";
    # unbound-policy has no actors.
    role_policy = new_policy(graphapi_post, "role-policy")
    declare_actor(graphapi_post, role_policy, "role", "admin")
    reader_policy = new_policy(graphapi_post, "reader-policy")
    declare_actor(graphapi_post, reader_policy, "role", "reader")
    new_policy(graphapi_post, "unbound-policy")

    # The bootstrap "Owner" policy is bound to the "owner" role.
    everything = {
        "role-policy",
        "reader-policy",
        "unbound-policy",
        "Owner",
    }
    has_actor = {
        "role-policy",
        "reader-policy",
        "Owner",
    }
    admins = {"role-policy"}

    # No actor constraint -> all policies (including the actor-less one).
    assert {
        p["name"] for p in read_policies(graphapi_post)
    } - catch_all == everything  # omitted
    assert names_for(None) == everything  # null
    assert names_for({}) == everything  # {}
    assert names_for({"actor": None}) == everything

    # Empty actor filter -> policies that have *any* actor (excludes unbound).
    assert names_for({"actor": {}}) == has_actor

    # Matching by role.
    assert names_for({"actor": {"roles": ["admin"]}}) == admins
    assert names_for({"actor": {"roles": ["reader"]}}) == {"reader-policy"}

    # An empty list matches nothing.
    assert names_for({"actor": {"roles": []}}) == set()

    # Multiple roles are OR'ed together.
    assert names_for({"actor": {"roles": ["admin", "reader"]}}) == admins | {
        "reader-policy"
    }

    # No actor matches a non-existent role.
    assert names_for({"actor": {"roles": ["nobody"]}}) == set()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actor_all_matches_any_filter(
    graphapi_post: GraphAPIPost,
) -> None:
    policy = new_policy(graphapi_post, "everyone-policy")
    # An "all" actor has no value and matches every actor.
    declare_actor(graphapi_post, policy, "all", "")

    # It is returned regardless of the queried role...
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["whatever"]}}
    )
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["nobody"]}}
    )
    # ... and by the existence filter.
    assert "everyone-policy" in policy_names_for_filter(graphapi_post, {"actor": {}})


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_applies_to_every_actor(
    graphapi_post: GraphAPIPost,
) -> None:
    """The policy is bound to no role: each rule gates on its own permission."""
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    assert response.errors is None
    actors = one(response.data["policies"]["objects"])["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("all", "")}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_cannot_be_modified(graphapi_post: GraphAPIPost) -> None:
    # Updating the policy itself is rejected.
    update = update_policy(graphapi_post, uuid=POLICYADMIN, name="Hacked")
    assert update.errors is not None

    # Declaring an actor on it is rejected.
    add = graphapi_post(
        DECLARE_ACTOR,
        variables={
            "input": {"policy": POLICYADMIN, "kind": "role", "value": "mallory"}
        },
    )
    assert add.errors is not None

    # Its sole "all" actor is unchanged.
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    actors = one(read.data["policies"]["objects"])["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("all", "")}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actor_declare_is_idempotent(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "p")
    first = declare_actor(graphapi_post, policy, "role", "admin")
    second = declare_actor(graphapi_post, policy, "role", "admin")
    # Declaring the same actor twice returns the same binding, no duplicate.
    assert first == second
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert len(response.data["policies"]["objects"][0]["actors"]) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_actors_declare_replaces_set(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "role", "value": "editor"},
                ],
            }
        },
    )
    assert response.errors is None
    assert len(response.data["policy_actors_declare"]) == 2

    # Declaring a new set replaces the old one: "editor" is dropped, "reader" is
    # added, and "admin" is kept (unchanged).
    again = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "role", "value": "reader"},
                ],
            }
        },
    )
    assert again.errors is None

    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    actors = read.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("role", "reader"),
    }

    # Declaring an empty set clears all actors.
    cleared = graphapi_post(
        DECLARE_ACTORS, variables={"input": {"policy": policy, "actors": []}}
    )
    assert cleared.errors is None
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert read.data["policies"]["objects"][0]["actors"] == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_actors_and_rules_are_protected(
    graphapi_post: GraphAPIPost,
) -> None:
    # The bulk actor declare is rejected for the policyadmin policy.
    bulk = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": POLICYADMIN,
                "actors": [{"kind": "role", "value": "mallory"}],
            }
        },
    )
    assert bulk.errors is not None

    # Deleting one of its (hard-bound) actors is rejected.
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    actors = read.data["policies"]["objects"][0]["actors"]
    del_actor = graphapi_post(DELETE_ACTOR, variables={"uuid": actors[0]["uuid"]})
    assert del_actor.errors is not None

    # Deleting one of its rules is rejected.
    rule_uuid = read_policy_rules(graphapi_post, POLICYADMIN)[0]["uuid"]
    del_rule = graphapi_post(DELETE_RULE, variables={"uuid": rule_uuid})
    assert del_rule.errors is not None


# Rules
# -----

DECLARE_RULE = """
  mutation DeclareRule($input: PolicyRuleDeclareInput!) {
    policy_rule_declare(input: $input) {
      uuid
      type
      field
      condition
      filter
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
      filter
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
          filter
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
    filter: str | None = None,
) -> str:
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": type,
                "field": field,
                "condition": condition,
                "filter": filter,
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
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_declare_and_read(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "with-rules")
    declare_rule(graphapi_post, policy, "Query", "policies")
    declare_rule(graphapi_post, policy, "Policy", "*")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"]) for r in rules} == {
        ("Query", "policies"),
        ("Policy", "*"),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_declare_is_idempotent(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "p")
    first = declare_rule(graphapi_post, policy, "Query", "policies")
    second = declare_rule(graphapi_post, policy, "Query", "policies")
    assert first == second
    assert len(read_policy_rules(graphapi_post, policy)) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rules_declare_replaces_set(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "policies"},
                    {"type": "Mutation", "field": "policy_create"},
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
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_delete(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "p")
    rule_uuid = declare_rule(graphapi_post, policy, "Query", "policies")
    deleted = graphapi_post(DELETE_RULE, variables={"uuid": rule_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_rule_delete"] is True
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_rules_bootstrapped(graphapi_post: GraphAPIPost) -> None:
    rules = {
        (r["type"], r["field"]): r["condition"]
        for r in read_policy_rules(graphapi_post, POLICYADMIN)
    }
    # Reading takes its own permission; every write takes declare_policy
    assert rules[("Query", "policies")] == READ_CONDITION
    assert rules[("Mutation", "policy_create")] == DECLARE_CONDITION
    assert rules[("Mutation", "policy_rules_declare")] == DECLARE_CONDITION


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policyadmin_rules_cannot_be_modified(
    graphapi_post: GraphAPIPost,
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


# Rule conditions (CEL)
# ---------------------


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_declare_with_condition(graphapi_post: GraphAPIPost) -> None:
    policy = new_policy(graphapi_post, "conditional")
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
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_empty_condition_is_unconditional(
    graphapi_post: GraphAPIPost,
) -> None:
    # An empty-string condition reads back as one (unconditional).
    policy = new_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="")
    rules = read_policy_rules(graphapi_post, policy)
    assert rules[0]["condition"] == ""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_condition_distinct_per_condition(
    graphapi_post: GraphAPIPost,
) -> None:
    # The same (type, field) may carry several conditions (each its own rule),
    # while re-declaring an identical (type, field, condition) is idempotent.
    policy = new_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees")  # unconditional
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="false")
    # Idempotent re-declares.
    declare_rule(graphapi_post, policy, "Query", "employees")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", ""),
        ("Query", "employees", "true"),
        ("Query", "employees", "false"),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_declare_rejects_invalid_condition(
    graphapi_post: GraphAPIPost,
) -> None:
    policy = new_policy(graphapi_post, "p")
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
@pytest.mark.usefixtures("empty_db")
async def test_policy_rules_declare_keys_on_condition(
    graphapi_post: GraphAPIPost,
) -> None:
    # The full-replace mutator treats (type, field, condition) as the identity.
    policy = new_policy(graphapi_post, "p")
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
        ("Query", "employees", ""),
        ("Query", "employees", '"admin" in token.roles'),
    }


# Rule entity filters (CEL)
# -------------------------

UPDATE_ITUSER = """
  mutation UpdateITUser($input: ITUserUpdateInput!) {
    ituser_update(input: $input) {
      uuid
    }
  }
"""

TERMINATE_ITUSER = """
  mutation TerminateITUser($input: ITUserTerminateInput!) {
    ituser_terminate(input: $input) {
      uuid
    }
  }
"""

DELETE_ITUSER = """
  mutation DeleteITUser($uuid: UUID!) {
    ituser_delete(uuid: $uuid) {
      uuid
    }
  }
"""


def ituser_check_spec(uuid_cel: str, employee_filter_cel: str) -> str:
    """A check-spec pinning the mutated IT-user, constrained by its person.

    `uuid_cel` is the CEL path to the mutated IT-user's uuid, which differs per
    mutator: the input-object mutators carry it as `args.input.uuid`, while
    `ituser_delete` takes a bare `args.uuid`.
    """
    return (
        f'[{{"collection": "ituser", "filter": {{"uuids": [{uuid_cel}], '
        f'"employee": {employee_filter_cel}}}}}]'
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_filter_declare_and_read(
    graphapi_post: GraphAPIPost,
) -> None:
    policy = new_policy(graphapi_post, "filtered-rule")
    value = json.dumps(
        [{"collection": "ituser", "filter": {"employee": {"query": "Bob"}}}]
    )
    declare_rule(graphapi_post, policy, "Mutation", "ituser_update", filter=value)

    rules = read_policy_rules(graphapi_post, policy)
    assert len(rules) == 1
    assert rules[0]["field"] == "ituser_update"
    assert rules[0]["filter"] == value


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_filter_allowed_on_any_field(
    graphapi_post: GraphAPIPost,
) -> None:
    # Any rule may carry a filter (compile-check only); the collection each
    # check-spec targets is chosen in the filter, not derived from the field. A
    # filter on a previously-"unsupported" field is therefore accepted.
    policy = new_policy(graphapi_post, "any-field-filter")
    for field in ("address_update", "employee_create", "org_unit_terminate"):
        declare_rule(
            graphapi_post,
            policy,
            "Mutation",
            field,
            filter=json.dumps([{"collection": "org_unit", "filter": {}}]),
        )
    assert {r["field"] for r in read_policy_rules(graphapi_post, policy)} == {
        "address_update",
        "employee_create",
        "org_unit_terminate",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policy_rule_filter_rejects_malformed(
    graphapi_post: GraphAPIPost,
) -> None:
    # A filter that is not a compilable CEL expression is rejected at declare
    # time (`not json` references the undeclared variable `json`).
    policy = new_policy(graphapi_post, "malformed-filtered-rule")
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": "Mutation",
                "field": "ituser_update",
                "filter": "not json",
            }
        },
    )
    assert response.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_rule_filter_cel_scopes_to_caller(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    # The filter is a CEL expression referencing `token`: anyone may update the
    # IT-users linked to *their own* person, and no one else's.
    itsystem = create_itsystem(
        {
            "user_key": "test-itsystem",
            "name": "Test IT system",
            "validity": {"from": "2020-01-01"},
        }
    )
    alice_ituser = create_ituser(
        {
            "user_key": "alice-account",
            "itsystem": str(itsystem),
            "person": str(alice),
            "validity": {"from": "2020-01-01"},
        }
    )
    bob_ituser = create_ituser(
        {
            "user_key": "bob-account",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )

    policy = new_policy(graphapi_post, "own-itusers")
    declare_actor(graphapi_post, policy, "all", "")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_update",
        filter=ituser_check_spec("args.input.uuid", '{"uuids": [token.uuid]}'),
    )
    set_auth(user_uuid=alice)

    def update(ituser: UUID) -> GQLResponse:
        return graphapi_post(
            UPDATE_ITUSER,
            variables={
                "input": {
                    "uuid": str(ituser),
                    "user_key": "changed",
                    "validity": {"from": "2020-01-01"},
                }
            },
        )

    # Alice may update her own IT-user (linked to her == token.uuid)...
    assert update(alice_ituser).errors is None
    # ...but not Bob's.
    assert update(bob_ituser).errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_rule_filter_limits_ituser_terminate_by_person(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    # `ituser_terminate` carries the target uuid as `args.input.uuid`.
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    itsystem = create_itsystem(
        {
            "user_key": "test-itsystem",
            "name": "Test IT system",
            "validity": {"from": "2020-01-01"},
        }
    )
    bob_ituser = create_ituser(
        {
            "user_key": "bob-account",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )
    carol_ituser = create_ituser(
        {
            "user_key": "carol-account",
            "itsystem": str(itsystem),
            "person": str(carol),
            "validity": {"from": "2020-01-01"},
        }
    )

    policy = new_policy(graphapi_post, "editor-terminates-bobs-itusers")
    declare_actor(graphapi_post, policy, "role", "editor")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_terminate",
        filter=ituser_check_spec("args.input.uuid", '{"query": "Bob"}'),
    )

    set_auth(role="editor")

    def terminate(ituser: UUID) -> GQLResponse:
        return graphapi_post(
            TERMINATE_ITUSER,
            variables={"input": {"uuid": str(ituser), "to": "2021-01-01"}},
        )

    assert terminate(bob_ituser).errors is None
    assert terminate(carol_ituser).errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_rule_filter_limits_ituser_delete_by_person(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    # `ituser_delete` takes the target uuid as a bare `uuid` argument, not an
    # `input`; the filter reads it off `args` just the same.
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    itsystem = create_itsystem(
        {
            "user_key": "test-itsystem",
            "name": "Test IT system",
            "validity": {"from": "2020-01-01"},
        }
    )
    bob_ituser = create_ituser(
        {
            "user_key": "bob-account",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )
    carol_ituser = create_ituser(
        {
            "user_key": "carol-account",
            "itsystem": str(itsystem),
            "person": str(carol),
            "validity": {"from": "2020-01-01"},
        }
    )

    policy = new_policy(graphapi_post, "editor-deletes-bobs-itusers")
    declare_actor(graphapi_post, policy, "role", "editor")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_delete",
        filter=ituser_check_spec("args.uuid", '{"query": "Bob"}'),
    )

    set_auth(role="editor")

    # Carol's does not match -> denied.
    assert graphapi_post(DELETE_ITUSER, variables={"uuid": str(carol_ituser)}).errors
    # Bob's IT-user matches the rule filter -> the editor may delete it.
    assert (
        graphapi_post(DELETE_ITUSER, variables={"uuid": str(bob_ituser)}).errors is None
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_rule_filter_unpinned_grants_when_any_matches(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    bob: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    # A check-spec that does not pin the mutated object grants when *any* object
    # matches its filter. Here an IT-user exists, so the update is granted.
    itsystem = create_itsystem(
        {
            "user_key": "test-itsystem",
            "name": "Test IT system",
            "validity": {"from": "2020-01-01"},
        }
    )
    bob_ituser = create_ituser(
        {
            "user_key": "bob-account",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )

    policy = new_policy(graphapi_post, "exists")
    declare_actor(graphapi_post, policy, "all", "")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_update",
        filter='[{"collection": "ituser", "filter": {}}]',
    )
    set_auth(user_uuid=bob)

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": str(bob_ituser),
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None


# PBAC gating of the policy API itself
# ------------------------------------


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_admin_can_read_policies(graphapi_post: GraphAPIPost) -> None:
    # The admin token carries every permission, read_policy among them, which is
    # what the bootstrap Policy Administrator gates Query.policies on
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_denies_without_grant(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    set_auth(role="nobody", user_uuid="11111111-1111-1111-1111-111111111111")
    response = graphapi_post(READ_POLICIES)
    assert response.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_read_policy_grants_reading_only(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """`read_policy` sees the collection, but cannot write to it."""
    set_auth(role="read_policy")

    assert graphapi_post(READ_POLICIES).errors is None
    assert create_policy(graphapi_post, name="GDPR").errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_declare_policy_grants_writing_only(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """`declare_policy` writes the collection, but cannot read it back.

    A mutator returns what it wrote and the policy types' own fields are public,
    so the write is still observable without `read_policy`.
    """
    set_auth(role="declare_policy")

    created = create_policy(graphapi_post, name="GDPR")
    assert created.errors is None
    policy = created.data["policy_create"]["uuid"]
    # A policy's actors and rules take the same permission as the policy itself,
    # though reading back a rule's expressions does not
    declare_actor(graphapi_post, policy, "role", "reader")
    declared = graphapi_post(
        DECLARE_RULE_SHAPE_ONLY,
        variables={"input": {"policy": policy, "type": "Query", "field": "employees"}},
    )
    assert declared.errors is None

    # ...while the expressions come back as field errors
    declared = graphapi_post(
        DECLARE_RULE,
        variables={"input": {"policy": policy, "type": "Query", "field": "employees"}},
    )
    assert declared.errors is not None

    assert graphapi_post(READ_POLICIES).errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_both_permissions_administer_policies(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """Holding both permissions is what makes an actor a policy administrator."""
    set_auth(role=["read_policy", "declare_policy"])

    policy = new_policy(graphapi_post, "GDPR")
    assert policy in {p["uuid"] for p in read_policies(graphapi_post)}

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": policy})
    assert deleted.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_grant_via_policy(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    # As admin (RBAC), grant the "employee-reader" role read access to the
    # employees collection.
    policy = new_policy(graphapi_post, "employee-reader")
    declare_actor(graphapi_post, policy, "role", "employee-reader")
    declare_rule(graphapi_post, policy, "Query", "employees")

    # Become a token carrying only that role and switch to PBAC.
    set_auth(role="employee-reader")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None

    # The role was not granted the policies collection.
    denied = graphapi_post(READ_POLICIES)
    assert denied.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_grant_respects_activation(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    # A deactivated policy does not grant access.
    response = create_policy(graphapi_post, name="inactive", active=False)
    policy = response.data["policy_create"]["uuid"]
    declare_actor(graphapi_post, policy, "role", "employee-reader")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(role="employee-reader")

    denied = graphapi_post(READ_EMPLOYEES)
    assert denied.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_pbac_denies_when_no_rule_matches(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    # With the catch-all RBAC policy deactivated and only a policy that grants an
    # unrelated field, a query for which no candidate rule exists is denied.
    rbac = one(p for p in read_policies(graphapi_post) if p["name"] == "RBAC")
    deactivated = update_policy(graphapi_post, uuid=rbac["uuid"], active=False)
    assert deactivated.errors is None

    policy = new_policy(graphapi_post, "employees-only")
    declare_actor(graphapi_post, policy, "role", "narrow")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(role="narrow")

    # `employees` is granted, but `policies` has no matching rule -> denied.
    assert graphapi_post(READ_EMPLOYEES).errors is None
    assert graphapi_post(READ_POLICIES).errors is not None
