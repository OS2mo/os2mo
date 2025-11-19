# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from typing import Self

from strawberry.types import Info

from mora.auth.keycloak.models import Token


class CustomInfo(Info):
    @property
    def token(self: Self) -> Awaitable[Token]:
        return self.context["get_token"]()
