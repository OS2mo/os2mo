# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from operator import attrgetter
from typing import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import NameNode
from graphql import VariableNode
from hypothesis import assume
from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis_graphql import nodes
from hypothesis_graphql import strategies as gql_st
from os2mo_fastapi_utils.auth.models import RealmAccess
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import Token
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.schema import AddressRead
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead

SCHEMA = str(LatestGraphQLSchema.get())


ORG_QUERY = "query { org { uuid } }"
ORG_UNIT_QUERY = "query { org_units { uuid } }"
ADDRESS_QUERY = "query { addresses { uuid } }"
ORG_UNIT_ADDRESS_QUERY = "query { org_units { objects { addresses { uuid } } } }"


async def load_org(keys: list[int]) -> list[OrganisationRead]:
    return [OrganisationRead.parse_obj({"name": "Test org"})] * len(keys)


async def load_all_org_units(**kwargs) -> list[Response[OrganisationUnitRead]]:
    uuid = uuid4()
    return [
        Response(
            uuid=uuid,
            objects=[
                OrganisationUnitRead.parse_obj(
                    {
                        "name": "Test org",
                        "validity": {"from": date.today().isoformat(), "to": None},
                    }
                )
            ],
        )
    ]


async def load_all_addresses(**kwargs) -> list[Response[AddressRead]]:
    return []


async def load_addresses(keys: list[UUID]) -> list[list[AddressRead]]:
    return [[] * len(keys)]


@pytest.mark.parametrize(
    "query,roles,errors",
    [
        # Query our org
        (ORG_QUERY, set(), {"User does not have read-access to org"}),
        (ORG_QUERY, {"read_org"}, set()),
        # Query all org-units
        (ORG_UNIT_QUERY, set(), {"User does not have read-access to org_units"}),
        (ORG_UNIT_QUERY, {"read_org"}, {"User does not have read-access to org_units"}),
        (ORG_UNIT_QUERY, {"read_org_units"}, set()),
        # Query all addresses
        (ADDRESS_QUERY, set(), {"User does not have read-access to addresses"}),
        (ADDRESS_QUERY, {"read_org"}, {"User does not have read-access to addresses"}),
        (ADDRESS_QUERY, {"read_addresses"}, set()),
        # Query all org-units and their addresses
        (
            ORG_UNIT_ADDRESS_QUERY,
            set(),
            {"User does not have read-access to org_units"},
        ),
        (
            ORG_UNIT_ADDRESS_QUERY,
            {"read_org"},
            {"User does not have read-access to org_units"},
        ),
        # Address permission is first checked here, as we actually have org-unit data
        (
            ORG_UNIT_ADDRESS_QUERY,
            {"read_org_units"},
            {"User does not have read-access to addresses"},
        ),
        (ORG_UNIT_ADDRESS_QUERY, {"read_org_units", "read_addresses"}, set()),
    ],
)
async def test_graphql_rbac(
    query: str, roles: set[str], errors: set[str], set_settings: Callable[..., None]
) -> None:
    """Test that we get the expected permission errors.

    Args:
        query: The GraphQL query to execute.
        roles: The roles on the OIDC token.
        errors: The errors we expect.
        set_settings: Fixture to configure settings overrides.
    """
    # Configure settings as required to enable GraphQL RBAC
    set_settings(
        **{
            "os2mo_auth": "True",
            "keycloak_rbac_enabled": "True",
            "graphql_rbac": "True",
            "confdb_show_owner": "True",
        }
    )
    # Setup the GraphQL context with the required dataloaders and OIDC token
    token = Token(
        azp="mo",
        uuid="00000000-0000-0000-0000-000000000000",
        realm_access=RealmAccess(roles=roles),
    )
    context = {
        "org_loader": DataLoader(load_fn=load_org),
        "address_getter": load_all_addresses,
        "org_unit_getter": load_all_org_units,
        "org_unit_address_loader": DataLoader(load_fn=load_addresses),
        "token": token,
    }

    response = await execute_graphql(query=query, context_value=context)

    # Assert our errors are as expected
    error_messages = set()
    if response.errors:
        error_messages = set(map(attrgetter("message"), response.errors))
    assert errors == error_messages


@settings(
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
    ],
)
@given(
    mutation=gql_st.mutations(
        SCHEMA,
        custom_scalars={
            "UUID": st.uuids().map(str).map(nodes.String),
            # The below line generates raw GraphQL AST nodes, representing:
            # 'upload_file(file: $upload_type_used, ...)'
            #                    ^^^^^^^^^^^^^^^^^ This part of a query
            "Upload": st.just(None).map(
                lambda f: VariableNode(name=NameNode(value="upload_type_used"))
            ),
        },
    )
)
async def test_mutators_require_rbac(
    mutation, set_settings: Callable[..., None]
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

    # Configure settings as required to enable GraphQL RBAC
    set_settings(
        **{
            "os2mo_auth": "True",
            "keycloak_rbac_enabled": "True",
            "graphql_rbac": "True",
            "confdb_show_owner": "True",
        }
    )
    # Setup the GraphQL context with the required dataloaders and OIDC token
    token = Token(
        azp="mo",
        uuid="00000000-0000-0000-0000-000000000000",
        realm_access=RealmAccess(roles=[]),
    )
    context = {
        "token": token,
    }
    response = await execute_graphql(query=mutation, context_value=context)
    assert len(response.errors) >= 1
    error_messages = set(map(attrgetter("message"), response.errors))
    assert "User does not have required role: admin" in error_messages
