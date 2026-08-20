# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.rbac import _rbac
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
