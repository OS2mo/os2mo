# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastramqpi.ramqp.utils import RejectMessage
from structlog.testing import capture_logs

from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldap_amqp import process_uuid


async def test_process_uuid() -> None:
    """Test that process_uuid calls sync_tool as expected."""
    ldap_amqpsystem = AsyncMock()
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    uuid = uuid4()
    dn = str(uuid4())

    dataloader.get_ldap_dn.return_value = dn

    await process_uuid(ldap_amqpsystem, sync_tool, dataloader, uuid)

    dataloader.get_ldap_dn.assert_called_once_with(uuid)
    sync_tool.import_single_user.assert_called_once_with(dn)


async def test_process_uuid_missing_uuid() -> None:
    """Test that process_uuid fails as expected."""
    ldap_amqpsystem = AsyncMock()
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    dataloader.get_ldap_dn.side_effect = NoObjectsReturnedException("BOOM")

    uuid = uuid4()

    with pytest.raises(RejectMessage) as exc_info:
        await process_uuid(ldap_amqpsystem, sync_tool, dataloader, uuid)
    assert "LDAP UUID could not be found" in str(exc_info.value)

    dataloader.get_ldap_dn.assert_called_once_with(uuid)


async def test_process_uuid_bad_sync() -> None:
    """Test that process_uuid fails as expected."""
    ldap_amqpsystem = AsyncMock()
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    uuid = uuid4()
    dn = str(uuid4())

    dataloader.get_ldap_dn.return_value = dn
    sync_tool.import_single_user.side_effect = ValueError("BOOM")

    with capture_logs() as cap_logs:
        await process_uuid(ldap_amqpsystem, sync_tool, dataloader, uuid)
        assert "Unable to synchronize DN to MO" in [x["event"] for x in cap_logs]

    dataloader.get_ldap_dn.assert_called_once_with(uuid)
    sync_tool.import_single_user.assert_called_once_with(dn)
    ldap_amqpsystem.publish_message.assert_called_once_with("uuid", uuid)
