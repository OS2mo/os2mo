# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from typing import Self

from strawberry.types import Info

from mora.auth.keycloak.models import Token
from mora.graphapi.gmodels.mo.organisation import OrganisationRead


class LoaderInfo:
    def __init__(self: Self, info: Info) -> None:
        self.info = info

    @property
    def org(self: Self) -> Awaitable[OrganisationRead]:
        return self.info.context["org_loader"].load(0)


class MOInfo:
    def __init__(self: Self, info: Info) -> None:
        self.info = info

    @property
    def loaders(self) -> LoaderInfo:
        return LoaderInfo(self)

    @property
    def token(self: Self) -> Awaitable[Token]:
        return self.info.context["get_token"]()


# https://strawberry.rocks/docs/types/schema-configurations#info_class
class CustomInfo(Info):
    @property
    def mo(self: Self) -> MOInfo:
        return MOInfo(self)
