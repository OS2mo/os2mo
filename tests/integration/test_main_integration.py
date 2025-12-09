# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastramqpi.context import Context

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import ldap_healthcheck
from mo_ldap_import_export.main import open_ldap_connection


@pytest.mark.usefixtures("integration_test_environment_variables")
@pytest.mark.integration_test
async def test_open_ldap_connection() -> None:
    """Test the open_ldap_connection."""
    settings = Settings()
    ldap_connection = configure_ldap_connection(settings)

    async with open_ldap_connection(ldap_connection):
        assert ldap_connection is not None
        assert ldap_connection.bound

        # Create a mock context for the healthcheck, as it expects a FastRAMQPI context
        mock_context = Context(user_context={"ldap_connection": ldap_connection})
        assert await ldap_healthcheck(mock_context)
