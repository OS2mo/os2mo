# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from pydantic import parse_obj_as
from strawberry.types import Info

from ..latest.health import health_map
from ..latest.models import HealthRead
from ..latest.permissions import gen_read_permission
from ..latest.query import Query as LatestQuery
from ..latest.schema import Health
from ..v3.version import GraphQLVersion3
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]


@strawberry.type(description="Entrypoint for all read-operations")
class Query(LatestQuery):
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
        healthchecks = set(health_map.keys())
        if identifiers is not None:
            healthchecks = healthchecks.intersection(set(identifiers))
        response = await execute_graphql(
            """
            query HealthQuery ($identifiers: [String!]){
                healths(identifiers: $identifiers) {
                    objects {
                        status
                        identifier
                    }
                }
            }
            """,
            graphql_version=GraphQLVersion3,
            context_value=info.context,
            variable_values={"identifiers": identifiers},
        )

        healths = response.data["healths"]["objects"]
        parsed_healths = parse_obj_as(list[HealthRead], healths)
        return list(map(Health.from_pydantic, parsed_healths))
