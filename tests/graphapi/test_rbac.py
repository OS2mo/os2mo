# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import NameNode
from graphql import VariableNode
from hypothesis import HealthCheck
from hypothesis import assume
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis_graphql import nodes
from hypothesis_graphql import strategies as gql_st
from sqlalchemy import select

from mora import db
from mora.graphapi.events import EventToken
from mora.graphapi.rbac_map import RBAC_MAP
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.mark.integration_test
async def test_rbac_map_covers_schema(
    graphapi_post: GraphAPIPost, empty_db: db.AsyncSession
) -> None:
    """RBAC is reject-by-default, so every field must be classified.

    Each schema field must be either granted by a PBAC policy or have a role
    requirement (`RBAC_MAP`). Conversely, entries which do not correspond to
    any schema field are dead rules, and therefore most likely mistakes.

    A field in both would be silently public (the chain grants access as soon
    as the PBAC policy matches, before `rbac_policy` runs), so it is almost
    certainly a mistake; the two are required to be disjoint.
    """
    public_fields = set(
        (
            await empty_db.execute(
                select(db.PolicyRule.type, db.PolicyRule.field)
                .join(db.Policy, db.PolicyRule.policy_fk == db.Policy.id)
                .where(db.Policy.name == "Public")
            )
        ).all()
    )

    schema_fields = set()
    for version in Version:
        response = graphapi_post(
            """
            query {
              __schema {
                types {
                  name
                  kind
                  fields(includeDeprecated: true) {
                    name
                  }
                }
              }
            }
            """,
            url=f"/graphql/v{version.value}",
        )
        assert response.errors is None
        assert response.data
        for type_ in response.data["__schema"]["types"]:
            if type_["kind"] != "OBJECT" or type_["name"].startswith("__"):
                continue
            schema_fields.update(
                (type_["name"], field["name"]) for field in type_["fields"]
            )

    classified = public_fields | RBAC_MAP.keys()

    missing = schema_fields - classified
    assert missing == set(), f"Unclassified schema fields: {missing}"

    stale = classified - schema_fields
    assert stale == set(), f"Classified entries without a schema field: {stale}"

    overlap = public_fields & RBAC_MAP.keys()
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


@pytest.fixture
def org_unit_with_address(
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """An org-unit with an address, so the queries under test return data."""
    org_unit_uuid = create_org_unit("test")
    facet_uuid = create_facet(
        {"user_key": "org_unit_address_type", "validity": {"from": "2000-01-01"}}
    )
    address_type_uuid = create_class(
        {
            "facet_uuid": str(facet_uuid),
            "user_key": "email",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2000-01-01"},
        }
    )
    create_address(
        {
            "address_type": str(address_type_uuid),
            "org_unit": str(org_unit_uuid),
            "value": "unit@example.org",
            "validity": {"from": "2000-01-01"},
        }
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
@pytest.mark.parametrize(
    "query,roles,errors",
    [
        # Query our org
        ("query { org { uuid } }", set(), {"No policy approved the access"}),
        ("query { org { uuid } }", {"reader"}, set()),
        # Query all org-units
        (
            "query { org_units { objects { uuid } } }",
            set(),
            {"No policy approved the access"},
        ),
        ("query { org_units { objects { uuid } } }", {"reader"}, set()),
        # Query all addresses
        (
            "query { addresses { objects { uuid } } }",
            set(),
            {"No policy approved the access"},
        ),
        ("query { addresses { objects { uuid } } }", {"reader"}, set()),
        # Query all org-units and their addresses
        (
            "query { org_units { objects { objects { addresses { uuid } } } } }",
            set(),
            {"No policy approved the access"},
        ),
        (
            "query { org_units { objects { objects { addresses { uuid } } } } }",
            {"reader"},
            set(),
        ),
    ],
)
async def test_graphql_rbac(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    query: str,
    roles: set[str],
    errors: set[str],
) -> None:
    """Test that we get the expected permission errors.

    Args:
        set_auth: Fixture to set the roles on the OIDC token.
        graphapi_post: Fixture to execute GraphQL queries.
        query: The GraphQL query to execute.
        roles: The roles on the OIDC token.
        errors: The errors we expect.
    """
    set_auth(roles, None)

    response = graphapi_post(query)

    # Assert our errors are as expected
    error_messages = set()
    if response.errors:
        error_messages = {error["message"] for error in response.errors}
    assert errors == error_messages


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@settings(
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.filter_too_much,
    ],
)
@given(
    mutation=gql_st.mutations(
        str(get_schema(LATEST_VERSION)),
        custom_scalars={
            "UUID": st.uuids().map(str).map(nodes.String),
            # The below line generates raw GraphQL AST nodes, representing:
            # 'upload_file(file: $upload_type_used, ...)'
            #                    ^^^^^^^^^^^^^^^^^ This part of a query
            "Upload": st.just(None).map(
                lambda f: VariableNode(name=NameNode(value="upload_type_used"))
            ),
            "DateTime": st.datetimes().map(lambda dt: dt.isoformat()).map(nodes.String),
            "EventToken": st.just(
                EventToken.serialize(EventToken(uuid=uuid4(), generation=uuid4()))
            ).map(nodes.String),
        },
    )
)
async def test_mutators_require_rbac(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    mutation: str,
) -> None:
    # We reject if 'upload_type_used' is found within the generated mutation.
    # NOTE: This assumes that this string is globally unique within the query.
    #
    # Upload files are a special case, as they are passed via http multi-part and not
    # via a normal GraphQL arguments, and thus it is very, very hard to handle without
    # patching inside hypothesis_graphql.
    #
    # If we were to patch hypothesis_graphql we would not only have to generate
    # VariableNodes, but also the corresponding ArgumentNodes and additionally we would
    # need to pass the generated variable/argument node name in as a context_value.
    #
    # Thus it is probably easier to just not test the 'upload_file' endpoint,
    # especially as we are hoping to get rid of it long term.
    assume("upload_type_used" not in mutation)

    # A user without any roles must not be able to call any mutator
    set_auth(None, None)

    response = graphapi_post(mutation)

    assert response.errors
    error_messages = {error["message"] for error in response.errors}
    assert error_messages == {"No policy approved the access"}
