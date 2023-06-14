# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from strawberry.types import Info

from ..latest.permissions import gen_read_permission
from ..latest.schema import Health
from ..v3.version import GraphQLVersion as NextGraphQLVersion
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]


@strawberry.type(description="Entrypoint for all read-operations")
class Query(NextGraphQLVersion.schema.query):  # type: ignore[name-defined]
    @strawberry.field(
        description="Get a list of all health checks, optionally by identifier(s)",
        permission_classes=[gen_read_permission("health")],
    )
    async def healths(
        self, info: Info, identifiers: list[str] | None = None
    ) -> list[Health]:
        """Implements backwards-compatibility of healths.

        Returns a list of Health(s), instead of PagedHealth(s).
        """
        response = await execute_graphql(
            """
            query HealthQuery ($identifiers: [String!]){
                healths(identifiers: $identifiers) {
                    objects {
                        identifier
                    }
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"identifiers": identifiers},
        )

        healths = response.data["healths"]["objects"]
        return [
            Health(identifier=health["identifier"])  # type: ignore[call-arg]
            for health in healths
        ]


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 2 of the GraphQL Schema.

    Version 3 introduced a breaking change to the `healths` endpoint by introducing
    pagination to it.
    Version 2 ensures that the old non-paginated version is still available.
    """

    query = Query


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 2."""

    version = 2
    schema = GraphQLSchema
