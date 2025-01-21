# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from mora.graphapi.gmodels.mo import OrganisationUnitRead

from ..latest.inputs import (
    OrganisationUnitUpdateInput as OrganisationUnitUpdateInputLatest,
)
from ..latest.inputs import strip_none
from ..latest.mutators import uuid2response
from ..latest.org_unit import update_org_unit
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.permissions import gen_update_permission
from ..latest.response import Response
from ..latest.schema import OrganisationUnit
from ..v22.version import GraphQLVersion as NextGraphQLVersion


class OrganisationUnitUpdateInput(OrganisationUnitUpdateInputLatest):
    def to_handler_dict(self) -> dict:
        return strip_none(super().to_handler_dict())


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Updates an organisation unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("org_unit"),
        ],
    )
    async def org_unit_update(
        self, input: OrganisationUnitUpdateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(await update_org_unit(input), OrganisationUnitRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 21 of the GraphQL Schema.

    Version 22 introduced a breaking change to the `org_unit_update` mutator
    making unset entries mean 'retain the original value' instead of mearning
    clear the field.
    Version 21 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 21."""

    version = 21
    schema = GraphQLSchema
