# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from ..latest.inputs import OrganisationUnitTerminateInput
from ..latest.mutators import uuid2response
from ..latest.org_unit import terminate_org_unit
from ..latest.permissions import gen_terminate_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.schema import OrganisationUnit
from ..latest.schema import Response
from ..v9.version import GraphQLVersion as NextGraphQLVersion
from ramodels.mo.organisation_unit import OrganisationUnitRead


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Terminates an organization unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("org_unit"),
        ],
    )
    async def org_unit_terminate(
        self, unit: OrganisationUnitTerminateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await terminate_org_unit(unit.to_pydantic()), OrganisationUnitRead
        )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 8 of the GraphQL Schema.

    Version 9 introduced a breaking change to the org_unit_terminate mutator, which
    changes the name of its input from `unit` to `input` to align with other mutators.
    Version 8 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 8."""

    version = 8
    schema = GraphQLSchema
