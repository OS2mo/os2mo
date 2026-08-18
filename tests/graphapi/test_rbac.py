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
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.policies.helpers import assert_access

ORG_UNIT_ADDRESS_QUERY = (
    "query { org_units { objects { objects { addresses { uuid } } } } }"
)


@pytest.mark.integration_test
async def test_policy_rules_cover_schema(
    graphapi_post: GraphAPIPost, empty_db: db.AsyncSession
) -> None:
    """PBAC is reject-by-default, so every field must be classified.

    Each schema field must be granted by at least one policy rule, a
    `(type, field)` pattern where either component may be the wildcard `"*"`,
    or it would be permanently denied. Introspection (`__`-prefixed) types are
    covered by `test_introspection_is_public` instead.
    """
    patterns = set(
        (await empty_db.execute(select(db.PolicyRule.type, db.PolicyRule.field))).all()
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
    "roles,granted",
    [
        (set(), False),
        ({"read_org"}, False),
        # The address permission is first checked here, as we actually have
        # org-unit data for the nested resolver to reach
        ({"read_org_unit"}, False),
        ({"read_org_unit", "read_address"}, True),
    ],
)
async def test_nested_field_requires_its_own_permission(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    roles: set[str],
    granted: bool,
) -> None:
    """A nested field is checked on its own, not covered by its parent's grant.

    Reaching an org-unit's addresses takes both permissions, and the check on
    the nested field only happens once there is data to resolve it against.
    Grants on a single field are covered by `tests/policies/test_rbac.py`.
    """
    set_auth(roles, None)
    assert_access(graphapi_post(ORG_UNIT_ADDRESS_QUERY), granted)


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
