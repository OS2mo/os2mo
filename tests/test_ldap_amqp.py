# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import uuid4

from mo_ldap_import_export.ldap_amqp import process_dn


async def test_process_dn() -> None:
    """Test that process_dn calls sync_tool as expected."""
    sync_tool = AsyncMock()
    dn = str(uuid4())

    await process_dn(sync_tool, dn, _=None)
    sync_tool.import_single_user.assert_called_once_with(dn)
