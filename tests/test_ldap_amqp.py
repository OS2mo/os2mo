# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastramqpi.ramqp.utils import RejectMessage

from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldap_amqp import process_dn


async def test_process_dn() -> None:
    """Test that process_dn calls sync_tool as expected."""
    sync_tool = AsyncMock()
    dn = str(uuid4())

    await process_dn(sync_tool, dn, _=None)
    sync_tool.import_single_user.assert_called_once_with(dn)


async def test_process_missing_dn() -> None:
    """Test that process_dn calls sync_tool as expected."""
    sync_tool = AsyncMock()
    sync_tool.import_single_user.side_effect = NoObjectsReturnedException("BOOM")

    dn = str(uuid4())

    with pytest.raises(RejectMessage) as exc_info:
        await process_dn(sync_tool, dn, _=None)
    assert f"DN could not be found: {dn}" in str(exc_info.value)

    sync_tool.import_single_user.assert_called_once_with(dn)
