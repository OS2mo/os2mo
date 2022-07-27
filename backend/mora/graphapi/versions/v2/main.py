from datetime import date
from typing import Any

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

from ..latest.main import get_context
from ..latest.main import Mutation
from ..latest.main import Query as LatestQuery
from ..latest.schema import Organisation
from ..latest.types import CPRType
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.shim import execute_graphql
from mora.graphapi.util import GraphQLVersion
from mora.util import CPR


def get_next_version_query():
    return LatestQuery


@strawberry.type(description="Entrypoint for all read-operations")
class Query(LatestQuery):
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
    )
    async def org(self, info: Info) -> Organisation:
        # TODO: Query the next version instead of latest
        response = await execute_graphql(
            """
            query MyQuery {
              org {
                uuid
                name
              }
            }
            """
        )
        org = response.data["org"]
        # org["name"] = "lol"
        return Organisation(**org)


def get_schema() -> strawberry.Schema:
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        # Automatic camelCasing disabled because under_score style is simply better
        #
        # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
        # Excerpt:
        #   Although, no difference was found between identifier styles with respect
        #   to accuracy, results indicate a significant improvement in time and lower
        #   visual effort with the underscore style.
        #
        # Additionally it preserves the naming of the underlying Python functions.
        config=StrawberryConfig(auto_camel_case=False),
        # https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
        scalar_overrides={
            CPR: CPRType,  # type: ignore
        },
        extensions=[
            StarletteContextExtension,
        ],
    )
    return schema


def get_version(enable_graphiql: bool, **kwargs: Any) -> GraphQLVersion:
    router = GraphQLRouter(
        get_schema(), context_getter=get_context, graphiql=enable_graphiql
    )

    version = GraphQLVersion(
        version=2,
        router=router,
        deprecation_date=date(2023, 1, 1),
    )

    return version
