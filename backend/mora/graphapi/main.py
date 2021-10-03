# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from uuid import UUID
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import strawberry
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL
from strawberry.schema.config import StrawberryConfig
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.types import Info

from mora.graphapi.auth import IsAuthenticated
from mora.graphapi.schema import Employee
from mora.graphapi.schema import Organisation
from mora.graphapi.dataloaders import get_employees
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.middleware import StarletteContextExtension


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Root Organisation
    # -----------------
    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Employees
    # ---------
    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Get a list of all employees"
    )
    async def employees(self, info: Info) -> List[Employee]:
        return await get_employees()

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Get a list of employees by uuids",
    )
    async def employees_by_uuids(self, info: Info, uuids: List[UUID]) -> List[Employee]:
        tasks = map(info.context["employee_loader"].load, map(str, uuids))
        return await gather(*tasks)

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Get a single employee by uuid",
    )
    async def employee_by_uuid(self, info: Info, uuid: UUID) -> Optional[Employee]:
        return await info.context["employee_loader"].load(str(uuid))


class MyGraphQL(GraphQL):
    # Subclass as done here:
    # * https://strawberry.rocks/docs/guides/dataloaders#usage-with-context

    async def get_context(
        self, request: Union[Request, WebSocket], response: Any
    ) -> Any:
        # Add our dataloaders to the context, such that they are available everywhere
        return {"request": request, "response": response, **get_loaders()}


def get_schema():
    schema = strawberry.Schema(
        query=Query,
        # Automatic camelCasing disabled because under_score style is simply better
        #
        # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
        # Excerpt:
        #   Although, no difference was found between identifier styles with respect
        #   to accuracy, results indicate a significant improvement in time and lower
        #   visual effort with the underscore style.
        #
        # Additionally it is perserves the naming of the underlying Python functions.
        config=StrawberryConfig(auto_camel_case=False),
        extensions=[
            OpenTelemetryExtension,
            StarletteContextExtension,
        ],
    )
    return schema


def setup_graphql(app):
    schema = get_schema()
    graphql_app = MyGraphQL(schema)

    app.add_route("/graphql", graphql_app)
    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    return app
