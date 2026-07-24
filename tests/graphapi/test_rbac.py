# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from graphql import GraphQLObjectType
from sqlalchemy import select

from mora import db
from mora.graphapi.rbac_map import RBAC_MAP
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version
from tests.conftest import AnotherTransaction
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.mark.integration_test
async def test_rbac_map_covers_schema(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    """Authorization is reject-by-default, so every field must be classified.

    Each schema field must be either granted by the bootstrapped Public policy
    or have a role requirement (`RBAC_MAP`). Conversely, entries which do not
    correspond to any schema field are dead rules, and therefore most likely
    mistakes.

    A field in both would be silently public (the chain grants access as soon
    as the Public policy matches, before `rbac_policy` runs), so it is almost
    certainly a mistake; the two are required to be disjoint.
    """
    async with another_transaction() as (_, session):
        public = set(
            (
                await session.execute(
                    select(db.PolicyRule.type, db.PolicyRule.field)
                    .join(db.Policy, db.PolicyRule.policy_fk == db.Policy.id)
                    .where(db.Policy.name == "Public")
                )
            ).all()
        )

    schema_fields = set()
    for version in Version:
        schema = get_schema(version)._schema
        for name, type_ in schema.type_map.items():
            if name.startswith("__"):
                continue
            if isinstance(type_, GraphQLObjectType):
                schema_fields.update((name, field) for field in type_.fields)

    classified = public | RBAC_MAP.keys()

    missing = schema_fields - classified
    assert missing == set(), f"Unclassified schema fields: {missing}"

    stale = classified - schema_fields
    assert stale == set(), f"Classified entries without a schema field: {stale}"

    overlap = public & RBAC_MAP.keys()
    assert overlap == set(), f"Fields both public and role-gated: {overlap}"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_introspection_is_public(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    """Introspection must be available to authenticated users without any roles."""
    set_auth(None, None)

    query = """
    query {
      __typename
      __schema {
        query_type: queryType {
          name
        }
      }
      __type(name: "Address") {
        name
        kind
      }
    }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "__typename": "Query",
        "__schema": {"query_type": {"name": "Query"}},
        "__type": {"name": "Address", "kind": "OBJECT"},
    }
