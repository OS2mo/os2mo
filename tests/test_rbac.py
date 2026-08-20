# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest.mock
from uuid import uuid4

import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.rbac import _get_employee_uuid
from mora.auth.keycloak.rbac import _get_employee_uuid_via_token
from mora.auth.keycloak.rbac import _rbac
from mora.config import Settings
from mora.mapping import OWNER
from tests.conftest import admin_auth
from tests.conftest import fake_auth


class TestRole:
    async def test_raise_exception_for_normal_user(self):
        # The user is neither admin or owner
        with pytest.raises(AuthorizationError):
            await _rbac(await fake_auth())

    async def test_raise_exception_when_role_is_owner(self):
        # Ownership based authorization is only available through GraphQL
        token = await fake_auth()
        token.realm_access.roles = {OWNER}
        with pytest.raises(AuthorizationError):
            await _rbac(token)

    async def test_return_when_role_is_admin(self):
        assert await _rbac(await admin_auth()) is None


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


@unittest.mock.patch("mora.auth.keycloak.rbac.mora.config.get_settings")
@unittest.mock.patch("mora.auth.keycloak.rbac._get_employee_uuid_via_it_system")
async def test__get_employee_uuid_via_it_system_strategy(mock, mock_get_settings):
    it_system_uuid = uuid4()
    uuid = uuid4()

    mock_get_settings.return_value = Settings(
        keycloak_rbac_authoritative_it_system_for_owners=it_system_uuid
    )

    token = Token(
        azp="azp",
        email="test@example.org",
        preferred_username="Test",
        uuid=uuid,
    )

    await _get_employee_uuid(token)

    # We are only testing that the correct strategy is selected
    mock.assert_awaited_once_with(it_system_uuid, uuid)
