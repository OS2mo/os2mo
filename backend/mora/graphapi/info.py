# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from typing import Self

from strawberry.types import Info

from mora.auth.keycloak.models import Token


class MOContext:
    def __init__(self: Self, info: Info) -> None:
        self.info = info

    @property
    def token(self: Self) -> Awaitable[Token]:
        return self.info.context["get_token"]()


# https://strawberry.rocks/docs/types/schema-configurations#info_class
class MOInfo(Info):
    @property
    def mo(self: Self) -> MOContext:
        return MOContext(self)
