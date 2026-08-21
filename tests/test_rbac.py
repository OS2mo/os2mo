# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.rbac import _rbac
from mora.mapping import ADMIN
from mora.mapping import OWNER


def make_token(roles: set[str]) -> Token:
    return Token(
        azp="mo-frontend",
        realm_access={"roles": roles},
        uuid="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
    )


class TestRole:
    async def test_raise_exception_for_normal_user(self):
        # The user is neither admin or owner
        with pytest.raises(AuthorizationError):
            await _rbac(make_token({"service_api"}))

    async def test_raise_exception_when_role_is_owner(self):
        # Ownership based authorization is only available through GraphQL
        with pytest.raises(AuthorizationError):
            await _rbac(make_token({OWNER}))

    async def test_return_when_role_is_admin(self):
        assert await _rbac(make_token({ADMIN})) is None
