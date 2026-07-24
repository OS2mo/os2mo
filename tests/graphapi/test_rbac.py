# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from operator import attrgetter
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import GraphQLObjectType
from graphql import NameNode
from graphql import VariableNode
from hypothesis import HealthCheck
from hypothesis import assume
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis_graphql import nodes
from hypothesis_graphql import strategies as gql_st
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.graphapi.events import EventToken
from mora.graphapi.gmodels.mo import OrganisationRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.models import AddressRead
from mora.graphapi.rbac_map import PUBLIC_FIELDS
from mora.graphapi.rbac_map import RBAC_MAP
from mora.graphapi.schema import get_schema
from mora.graphapi.shim import execute_graphql
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

ORG_QUERY = "query { org { uuid } }"
ORG_UNIT_QUERY = "query { org_units { objects { uuid } } }"
ADDRESS_QUERY = "query { addresses { objects { uuid } } }"
ORG_UNIT_ADDRESS_QUERY = (
    "query { org_units { objects { objects { addresses { uuid } } } } }"
)


async def load_org(keys: list[int]) -> list[OrganisationRead]:
    return [OrganisationRead.parse_obj({"name": "Test org"})] * len(keys)


async def load_all_org_units(**kwargs) -> dict[UUID, list[OrganisationUnitRead]]:
    return {}


async def load_org_units(keys: list[UUID]) -> list[list[OrganisationUnitRead]]:
    return [
        [
            OrganisationUnitRead.parse_obj(
                {
                    "name": "Test org",
                    "validity": {"from": date.today().isoformat(), "to": None},
                }
            )
        ]
    ] * len(keys)


async def load_all_addresses(**kwargs) -> dict[UUID, list[AddressRead]]:
    return {}


async def load_addresses(keys: list[UUID]) -> list[list[AddressRead]]:
    return [[] * len(keys)]


def test_rbac_map_covers_schema() -> None:
    """RBAC is reject-by-default, so every field must be classified.

    Each schema field must be either public (`PUBLIC_FIELDS`) or have a role
    requirement (`RBAC_MAP`). Conversely, entries which do not correspond to
    any schema field are dead rules, and therefore most likely mistakes.

    A field in both would be silently public (the chain grants access as soon
    as `no_role_required_policy` matches, before `rbac_policy` runs), so it is
    almost certainly a mistake; the two are required to be disjoint.
    """
    schema_fields = set()
    for version in Version:
        schema = get_schema(version)._schema
        for name, type_ in schema.type_map.items():
            if name.startswith("__"):
                continue
            if isinstance(type_, GraphQLObjectType):
                schema_fields.update((name, field) for field in type_.fields)

    classified = PUBLIC_FIELDS | RBAC_MAP.keys()

    missing = schema_fields - classified
    assert missing == set(), f"Unclassified schema fields: {missing}"

    stale = classified - schema_fields
    assert stale == set(), f"Classified entries without a schema field: {stale}"

    overlap = PUBLIC_FIELDS & RBAC_MAP.keys()
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


@pytest.mark.parametrize(
    "query,roles,errors",
    [
        # Query our org
        (ORG_QUERY, set(), {"No policy approved the access"}),
        (ORG_QUERY, {"read_org"}, set()),
        # Query all org-units
        (ORG_UNIT_QUERY, set(), {"No policy approved the access"}),
        (ORG_UNIT_QUERY, {"read_org"}, {"No policy approved the access"}),
        (ORG_UNIT_QUERY, {"read_org_unit"}, set()),
        # Query all addresses
        (ADDRESS_QUERY, set(), {"No policy approved the access"}),
        (ADDRESS_QUERY, {"read_org"}, {"No policy approved the access"}),
        (ADDRESS_QUERY, {"read_address"}, set()),
        # Query all org-units and their addresses
        (
            ORG_UNIT_ADDRESS_QUERY,
            set(),
            {"No policy approved the access"},
        ),
        (
            ORG_UNIT_ADDRESS_QUERY,
            {"read_org"},
            {"No policy approved the access"},
        ),
        # Address permission is first checked here, as we actually have org-unit data
        (
            ORG_UNIT_ADDRESS_QUERY,
            {"read_org_unit"},
            {"No policy approved the access"},
        ),
        (ORG_UNIT_ADDRESS_QUERY, {"read_org_unit", "read_address"}, set()),
    ],
)
async def test_graphql_rbac(query: str, roles: set[str], errors: set[str]) -> None:
    """Test that we get the expected permission errors.

    Args:
        query: The GraphQL query to execute.
        roles: The roles on the OIDC token.
        errors: The errors we expect.
    """
    # Setup the GraphQL context with the required dataloaders and OIDC token

    async def get_token():
        return Token(
            azp="mo",
            uuid="00000000-0000-0000-0000-000000000000",
            realm_access=RealmAccess(roles=roles),
        )

    session = AsyncMock()
    session.scalars.return_value.all = lambda: [uuid4()]

    # Configure context to allow both attribute and dictionary access
    context = AsyncMock()
    context.__getitem__.side_effect = lambda key: getattr(context, key)

    context.session = session
    context.get_token = get_token

    # Configure dataloaders container
    context.dataloaders = AsyncMock()
    context.dataloaders.org_loader = DataLoader(load_fn=load_org)
    context.dataloaders.address_loader = DataLoader(load_fn=load_addresses)
    context.dataloaders.address_getter = AsyncMock(side_effect=load_all_addresses)
    context.dataloaders.org_unit_loader = DataLoader(load_fn=load_org_units)
    context.dataloaders.org_unit_getter = AsyncMock(side_effect=load_all_org_units)
    context.dataloaders.org_unit_address_loader = DataLoader(load_fn=load_addresses)

    response = await execute_graphql(query=query, context_value=context)

    # Assert our errors are as expected
    error_messages = set()
    if response.errors:
        error_messages = {e.message for e in response.errors}
    assert errors == error_messages


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
async def test_mutators_require_rbac(mutation) -> None:
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

    # Setup the GraphQL context with the required dataloaders and OIDC token

    async def get_token():
        return Token(
            azp="mo",
            uuid="00000000-0000-0000-0000-000000000000",
            realm_access=RealmAccess(roles=[]),
        )

    context = AsyncMock()
    context.__getitem__.side_effect = lambda key: getattr(context, key)
    context.get_token = get_token

    response = await execute_graphql(query=mutation, context_value=context)
    assert len(response.errors) >= 1
    error_messages = set(map(attrgetter("message"), response.errors))
    for error_message in error_messages:
        assert error_message == "No policy approved the access"
