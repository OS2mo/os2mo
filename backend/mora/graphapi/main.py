# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import strawberry
from strawberry.asgi import GraphQL
from strawberry.schema.config import StrawberryConfig
from strawberry.extensions.tracing import OpenTelemetryExtension

from mora.graphapi.auth import IsAuthenticated
from mora.graphapi.schema import Organisation
from mora.service import org


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
    async def org(self) -> Organisation:
        obj = await org.get_configured_organisation()
        return Organisation(**obj)


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
        ]
    )
    return schema


def setup_graphql(app):
    schema = get_schema()
    graphql_app = GraphQL(schema)

    app.add_route("/graphql", graphql_app)
    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    return app
