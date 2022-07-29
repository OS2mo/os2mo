# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
# TODO: IRL this would be imported from v1.query, but since we're going from a non-
#  versioned to a versioned API, the first v1 version doesn't introduce any schema
#  changes - something that would never be the case otherwise.
from strawberry.types import Info

from mora.graphapi.shim import execute_graphql
from ..latest.query import Query
from ..latest.schema import Organisation
from ..v3.version import GraphQLVersion3


@strawberry.type(description="Entrypoint for all read-operations")
class Query(Query):
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
            """,
            graphql_version=GraphQLVersion3
        )
        org = response.data["org"]
        # org["name"] = "lol"
        return Organisation(**org)
