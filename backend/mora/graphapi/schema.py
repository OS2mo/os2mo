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


from typing import AsyncGenerator
from mora.triggers.internal.amqp_trigger import construct_topic
from mora.triggers.internal.amqp_trigger import listen_to_topic


@strawberry.type
class EventOutput:
    message_uuid: UUID
    uuid: UUID
    object_uuid: UUID
    time: str


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def event_listener(self, service: str, object_type: str, action: str) -> AsyncGenerator[EventOutput, None]:
        topic = construct_topic(service, object_type, action)
        async for payload in listen_to_topic(topic):
            event_output = EventOutput(**payload)
            yield event_output


schema = strawberry.Schema(query=Query, subscription=Subscription, config=StrawberryConfig(auto_camel_case=False))
