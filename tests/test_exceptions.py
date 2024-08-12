# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage
from gql.transport.exceptions import TransportQueryError

from mo_ldap_import_export.exceptions import http_reject_on_failure


@pytest.mark.parametrize(
    "exception,status_code,detail",
    [
        (RejectMessage("Rejected"), 451, "Rejected"),
        (RequeueMessage("Requeue"), 409, "Requeue"),
        (TransportQueryError("Connection refused"), 409, "Connection refused"),
        (ValueError("BOOM"), 500, "BOOM"),
    ],
)
async def test_http_reject_on_failure(
    exception: Exception, status_code: int, detail: str
) -> None:
    wrappee = AsyncMock()
    wrapped = http_reject_on_failure(wrappee)

    wrappee.side_effect = exception
    with pytest.raises(HTTPException) as exc_info:
        await wrapped()
    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == detail
