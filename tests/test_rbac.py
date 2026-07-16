# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest.mock
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.rbac import _get_employee_uuid
from mora.auth.keycloak.rbac import _get_employee_uuid_via_token
from mora.auth.keycloak.rbac import _rbac
from mora.mapping import ADMIN
from mora.mapping import OWNER
from tests.test_integration_rbac import ANDERS_AND
from tests.test_integration_rbac import mock_auth

IT_SYSTEM = UUID("07817b1e-a4a3-45a1-8ae0-13a02861cfa9")


class TestRole:
    async def test_raise_exception_for_normal_user(self):
        # The user is neither admin or owner
        token = mock_auth()()
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    async def test_raise_exception_when_role_is_owner_and_admin_only_true(self):
        token = mock_auth(OWNER, ANDERS_AND)()
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, True)

    async def test_return_when_role_is_admin(self):
        token = mock_auth(ADMIN, ANDERS_AND)()
        r = await _rbac(token, None, False)
        assert r is None


class TestOwner:
    async def test_raise_exception_when_owner_but_no_user_uuid(self):
        token = mock_auth(role=OWNER, user_uuid=None)()  # noqa: FURB120
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)


def test__get_employee_uuid_via_token():
    uuid = uuid4()
    employee_uuid = _get_employee_uuid_via_token(
        Token(
            azp="azp",
            email="test@example.org",
            preferred_username="Test",
            uuid=uuid,
        )
    )
    assert employee_uuid == uuid


async def test__get_employee_uuid_via_token_strategy():
    uuid = uuid4()
    token = Token(
        azp="azp",
        email="test@example.org",
        preferred_username="Test",
        uuid=uuid,
    )
    assert await _get_employee_uuid(token) == uuid


@pytest.mark.envvar(
    {"KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS": str(IT_SYSTEM)}
)
@unittest.mock.patch("mora.auth.keycloak.rbac._get_employee_uuid_via_it_system")
async def test__get_employee_uuid_via_it_system_strategy(
    mock: AsyncMock,
) -> None:
    uuid = uuid4()

    token = Token(
        azp="azp",
        email="test@example.org",
        preferred_username="Test",
        uuid=uuid,
    )

    await _get_employee_uuid(token)

    # We are only testing that the correct strategy is selected
    mock.assert_awaited_once_with(IT_SYSTEM, uuid)
