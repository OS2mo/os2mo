# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests that the policy API's exposed surface stays fully accounted for.

The policy types describe the authorization model itself, so a field or a route
that reaches one without being classified is a leak waiting to happen. These
tests derive the surface from the schema rather than from a snapshot, so adding
a field or an entry point fails here until it is deliberately placed on one side
of the gate.
"""

import pytest
from sqlalchemy import select

from alembic_helpers.policy_api_fields import POLICY_API_FIELDS
from mora import db
from tests.conftest import GraphAPIPost

# The output types making up the policy API
POLICY_TYPES = frozenset({"Policy", "PolicyActor", "PolicyRule", "PolicyPaged"})

# Every field in the schema whose type reaches a policy object. A route not
# listed here is either new (classify it) or an unintended way in
POLICY_ROUTES = frozenset(
    {
        # The collection, gated on read_policy
        ("Query", "policies"),
        # The self-scoped view, gated likewise: it reaches only the caller's
        # own policies (see test_query.test_me_policies_is_seeded_from_the_caller)
        ("Myself", "policies"),
        # Within the aggregate, reachable only from a policy already held
        ("Policy", "actors"),
        ("Policy", "rules"),
        ("PolicyPaged", "objects"),
        # Mutator returns, gated on declare_policy
        ("Mutation", "policy_create"),
        ("Mutation", "policy_update"),
        ("Mutation", "policy_actor_declare"),
        ("Mutation", "policy_actors_declare"),
        ("Mutation", "policy_rule_declare"),
        ("Mutation", "policy_rules_declare"),
    }
)

INTROSPECT = """
  query Introspect {
    __schema {
      types {
        name
        kind
        fields {
          name
          type {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                }
              }
            }
          }
        }
      }
    }
  }
"""


def named_type(type_ref: dict) -> str | None:
    """The type a (possibly non-null, possibly list) type reference wraps."""
    while type_ref.get("name") is None and type_ref.get("ofType") is not None:
        type_ref = type_ref["ofType"]
    return type_ref.get("name")


@pytest.fixture
def schema_fields(graphapi_post: GraphAPIPost) -> dict[tuple[str, str], str | None]:
    """Every output `(type, field)` in the schema, mapped to what it returns."""
    response = graphapi_post(INTROSPECT)
    assert response.errors is None
    return {
        (type["name"], field["name"]): named_type(field["type"])
        for type in response.data["__schema"]["types"]
        for field in type["fields"] or []
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_every_policy_field_is_classified(
    schema_fields: dict[tuple[str, str], str | None],
    raw_session: db.AsyncSession,
) -> None:
    """Each policy-type field is either public or gated on read_policy.

    A field left out of both is denied to everyone by default, which is safe but
    silently breaks the API, and one put in both is a contradiction. Either way
    a new field has to be classified rather than defaulted.
    """
    gated = set(
        (
            await raw_session.execute(
                select(db.PolicyRule.type, db.PolicyRule.field)
                .join(db.Policy)
                .where(db.Policy.name == "Policy Administrator")
                .where(db.PolicyRule.condition == '"read_policy" in token.roles')
            )
        ).all()
    )
    public = set(POLICY_API_FIELDS)
    exposed = {(type, field) for type, field in schema_fields if type in POLICY_TYPES}

    assert not exposed - public - gated, "policy-type fields left unclassified"
    assert not public & gated, "policy-type fields both public and gated"
    # The only grants that are not fields of a policy type are the two ways in
    assert (public | gated) - exposed == {("Myself", "policies"), ("Query", "policies")}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_no_unclassified_route_to_a_policy(
    schema_fields: dict[tuple[str, str], str | None],
) -> None:
    """Only known fields return a policy object.

    Field permissions gate what you may read off an object you hold, so a new
    field returning a `Policy` is a new way to obtain one. Whether it needs a
    grant is a judgement call; making it silently is the error.
    """
    routes = {
        (type, field)
        for (type, field), returns in schema_fields.items()
        if returns in POLICY_TYPES
    }
    assert routes == POLICY_ROUTES
