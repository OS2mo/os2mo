# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest

from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.environments.main import get_org_unit_type_uuid
from mo_ldap_import_export.exceptions import UUIDNotFoundException


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_get_org_unit_type_uuid(
    graphql_client: GraphQLClient,
) -> None:
    result = await get_org_unit_type_uuid(graphql_client, "Afdeling")
    assert result is not None
    UUID(result)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_get_org_unit_type_uuid_invalid(
    graphql_client: GraphQLClient,
) -> None:
    with pytest.raises(UUIDNotFoundException) as exc_info:
        await get_org_unit_type_uuid(graphql_client, "__this__does__not__exist")
    assert "class not found, facet_user_key: org_unit_type" in str(exc_info.value)
