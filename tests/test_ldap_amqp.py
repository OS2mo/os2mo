# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage

from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldap_amqp import process_dn
from mo_ldap_import_export.ldap_amqp import process_uuid


async def test_process_dn() -> None:
    """Test that process_dn published messages as expected."""
    ldap_amqpsystem = AsyncMock()
    dataloader = AsyncMock()

    uuid = uuid4()
    dn = str(uuid4())

    dataloader.get_ldap_unique_ldap_uuid.return_value = uuid

    await process_dn(ldap_amqpsystem, dataloader, dn)

    dataloader.get_ldap_unique_ldap_uuid.assert_called_once_with(dn)
    ldap_amqpsystem.publish_message.assert_called_once_with("uuid", uuid)


async def test_process_dn_missing_dn() -> None:
    """Test that process_dn fails as expected."""
    ldap_amqpsystem = AsyncMock()
    dataloader = AsyncMock()

    dataloader.get_ldap_unique_ldap_uuid.side_effect = NoObjectsReturnedException(
        "BOOM"
    )

    dn = str(uuid4())

    with pytest.raises(RejectMessage) as exc_info:
        await process_dn(ldap_amqpsystem, dataloader, dn)
    assert "DN could not be found" in str(exc_info.value)

    dataloader.get_ldap_unique_ldap_uuid.assert_called_once_with(dn)


async def test_process_uuid() -> None:
    """Test that process_uuid calls sync_tool as expected."""
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    uuid = uuid4()
    dn = str(uuid4())

    dataloader.get_ldap_dn.return_value = dn

    await process_uuid(sync_tool, dataloader, uuid)

    dataloader.get_ldap_dn.assert_called_once_with(uuid)
    sync_tool.import_single_user.assert_called_once_with(dn)


async def test_process_uuid_missing_uuid() -> None:
    """Test that process_uuid fails as expected."""
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    dataloader.get_ldap_dn.side_effect = NoObjectsReturnedException("BOOM")

    uuid = uuid4()

    with pytest.raises(RejectMessage) as exc_info:
        await process_uuid(sync_tool, dataloader, uuid)
    assert "LDAP UUID could not be found" in str(exc_info.value)

    dataloader.get_ldap_dn.assert_called_once_with(uuid)


async def test_process_uuid_bad_sync() -> None:
    """Test that process_uuid fails as expected."""
    sync_tool = AsyncMock()
    dataloader = AsyncMock()

    uuid = uuid4()
    dn = str(uuid4())

    dataloader.get_ldap_dn.return_value = dn
    sync_tool.import_single_user.side_effect = ValueError("BOOM")

    with pytest.raises(RequeueMessage) as exc_info:
        await process_uuid(sync_tool, dataloader, uuid)
    assert "Unable to synchronize DN to MO" in str(exc_info.value)

    dataloader.get_ldap_dn.assert_called_once_with(uuid)
    sync_tool.import_single_user.assert_called_once_with(dn)
