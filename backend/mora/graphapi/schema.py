# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from strawberry.schema.config import StrawberryConfig

from ..service import org


@strawberry.type
class Organisation:
    uuid: UUID
    name: str
    user_key: str


@strawberry.type
class Query:
    @strawberry.field
    async def org(self) -> Organisation:
        obj = await org.get_configured_organisation()
        return Organisation(**obj)


schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
