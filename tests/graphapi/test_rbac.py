# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from graphql import GraphQLObjectType
from sqlalchemy import select

from mora import db
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version
from tests.conftest import AnotherTransaction
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.mark.integration_test
async def test_policy_rules_cover_schema(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    """Authorization is reject-by-default and DB-driven, so the bootstrapped
    policy rules must cover the full schema.

    This replaces the old static ``RBAC_MAP`` coverage check: every schema field
    must be granted by at least one bootstrapped policy rule (a ``(type, field)``
    pattern where either component may be the wildcard ``"*"``), or it would be
    permanently denied. Introspection (``__``-prefixed) types are governed by the
    Introspection policy and validated separately by
    ``test_introspection_is_public``.
    """
    async with another_transaction() as (_, session):
        patterns = set(
            (
                await session.execute(select(db.PolicyRule.type, db.PolicyRule.field))
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

    def is_covered(type_name: str, field_name: str) -> bool:
        return any(
            rule_type in (type_name, "*") and rule_field in (field_name, "*")
            for rule_type, rule_field in patterns
        )

    missing = {field for field in schema_fields if not is_covered(*field)}
    assert missing == set(), (
        f"Schema fields not granted by any bootstrapped policy rule: {sorted(missing)}"
    )


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
