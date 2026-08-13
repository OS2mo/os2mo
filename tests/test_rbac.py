# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.rbac import _rbac
from mora.mapping import ADMIN
from mora.mapping import OWNER
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
