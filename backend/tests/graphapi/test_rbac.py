# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from datetime import date
from operator import attrgetter
from typing import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from os2mo_fastapi_utils.auth.models import RealmAccess
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import Token
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.schema import AddressRead
from mora.graphapi.versions.latest.schema import Response
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead

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
