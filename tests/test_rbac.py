# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest.mock
from uuid import uuid4

import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.owner import _get_entity_owners
from mora.auth.keycloak.rbac import _get_employee_uuid
from mora.auth.keycloak.rbac import _get_employee_uuid_via_token
from mora.auth.keycloak.rbac import _rbac
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import EntityType
from tests.test_integration_rbac import ANDERS_AND
from tests.test_integration_rbac import mock_auth


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


class TestGetEntityOwners:
    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    async def test_filter_empty_dicts_and_vacant_owners(
        self, mock_get_from_type, mock_get_connector
    ):
        # Arrange
        owner_uuid = uuid4()
        mock_get_from_type.return_value = [
            {},
            {"owner": None},  # Happens for vacant owners
            {"owner": {"uuid": str(owner_uuid)}},
        ]

        # Act
        owners = await _get_entity_owners(uuid4(), EntityType.ORG_UNIT)

        # Assert
        assert owners == {owner_uuid}


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
