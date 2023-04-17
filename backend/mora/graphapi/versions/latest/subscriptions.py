# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Subscriptions."""
import asyncio
from datetime import datetime
from collections.abc import AsyncGenerator, AsyncIterator
from uuid import UUID

from more_itertools import count_cycle

import strawberry
from strawberry.types import Info

from .schema import Address
from .schema import Response
from ramodels.mo.details import AddressRead


def event_generator(model: type, resolver_model):

    async def handler(
        info: Info,
        uuid: UUID | None = None,
    ) -> AsyncIterator[Response[model]]:

        uuids = [
            "0011406b-419f-4236-91e3-8040e9438370",
            "00423155-3eab-4a4c-b0ad-33d5e8c186a5",
            "00513f7c-5aed-466a-966d-35537025d72d",
            "0056be89-5191-4559-82d9-e1d5beeadaba",
            "0071a6f6-41ab-4f45-a8c0-5de31168f094",
            "00770a13-8894-49a1-b3ef-71e4d15d6d82",
            "00817d38-bc4f-4db3-9b72-e064bd5ecca9",
        ]

        while True:
            for x in uuids:
                yield Response(uuid=UUID(x), model=resolver_model)  # type: ignore
                await asyncio.sleep(1)

        #routing_key = MORoutingKey(service_type, object_type, request_type)
        #async for payload in event_bus.listen(routing_key, uuid, object_uuid):
        #    yield payload

    return handler


@strawberry.type
class Subscription:
    addresses: AsyncIterator[Response[Address]] = strawberry.subscription(
        resolver=event_generator(Address, AddressRead)
    )
   
    @strawberry.subscription
    async def heartbeat(self, info: Info) -> AsyncGenerator[str, None]:
        connection_params: dict = info.context.get("connection_params")
        print(info.context)
        print(connection_params)

        while True:
            await asyncio.sleep(1)
            yield datetime.now().isoformat()
