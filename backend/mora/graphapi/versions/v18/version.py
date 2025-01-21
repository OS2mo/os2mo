# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

import strawberry
from pydantic import Field
from pydantic import parse_obj_as

from mora.graphapi.gmodels.mo._shared import UUIDBase

from ..latest.inputs import ClassTerminateInput as LatestClassTerminateInput
from ..latest.inputs import FacetTerminateInput as LatestFacetTerminateInput
from ..latest.inputs import ITSystemTerminateInput as LatestITSystemTerminateInput
from ..latest.models import ClassTerminate as LatestClassTerminate
from ..latest.models import FacetTerminate as LatestFacetTerminate
from ..latest.models import ITSystemTerminate as LatestITSystemTerminate
from ..latest.models import ValidityTerminate
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.permissions import gen_terminate_permission
from ..latest.response import Response
from ..latest.schema import Class
from ..latest.schema import Facet
from ..latest.schema import ITSystem
from ..v19.version import GraphQLVersion as NextGraphQLVersion


class TerminatorMixin:
    def to_latest_dict(self: Any) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "from": self.validity.from_date,
            "to": self.validity.to_date,
        }


class ClassTerminateV18(UUIDBase, TerminatorMixin):
    uuid: UUID = Field(description="UUID for the class we want to terminate.")
    validity: ValidityTerminate = Field(description="When to terminate the class")

    def to_new_create_input(self) -> LatestClassTerminateInput:
        return LatestClassTerminateInput.from_pydantic(
            parse_obj_as(LatestClassTerminate, self.to_latest_dict())
        )


class FacetTerminateV18(UUIDBase, TerminatorMixin):
    uuid: UUID = Field(description="UUID for the facet we want to terminate.")
    validity: ValidityTerminate = Field(description="When to terminate the facet")

    def to_new_create_input(self) -> LatestFacetTerminateInput:
        return LatestFacetTerminateInput.from_pydantic(
            parse_obj_as(LatestFacetTerminate, self.to_latest_dict())
        )


class ITSystemTerminateV18(UUIDBase, TerminatorMixin):
    uuid: UUID = Field(description="UUID for the it-system we want to terminate.")
    validity: ValidityTerminate = Field(description="When to terminate the ITSystem")

    def to_new_create_input(self) -> LatestITSystemTerminateInput:
        return LatestITSystemTerminateInput.from_pydantic(
            parse_obj_as(LatestITSystemTerminate, self.to_latest_dict())
        )


@strawberry.experimental.pydantic.input(
    model=ClassTerminateV18,
    all_fields=True,
)
class ClassTerminateInput:
    """Input model for terminating a class."""


@strawberry.experimental.pydantic.input(
    model=FacetTerminateV18,
    all_fields=True,
)
class FacetTerminateInput:
    """Input model for terminating a facet."""


@strawberry.experimental.pydantic.input(
    model=ITSystemTerminateV18,
    all_fields=True,
)
class ITSystemTerminateInput:
    """Input model for terminating an ITSystem."""


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Terminates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("class"),
        ],
    )
    async def class_terminate(self, input: ClassTerminateInput) -> Response[Class]:
        new_input = input.to_pydantic().to_new_create_input()
        return await NextGraphQLVersion.schema.mutation.class_terminate(
            self=self, input=new_input
        )

    @strawberry.mutation(
        description="Terminates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("facet"),
        ],
    )
    async def facet_terminate(self, input: FacetTerminateInput) -> Response[Facet]:
        new_input = input.to_pydantic().to_new_create_input()
        return await NextGraphQLVersion.schema.mutation.facet_terminate(
            self=self, input=new_input
        )

    @strawberry.mutation(
        description="Terminates an IT-System.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("itsystem"),
        ],
    )
    async def itsystem_terminate(
        self, input: ITSystemTerminateInput
    ) -> Response[ITSystem]:
        new_input = input.to_pydantic().to_new_create_input()
        return await NextGraphQLVersion.schema.mutation.itsystem_terminate(
            self=self, input=new_input
        )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 18 of the GraphQL Schema.

    Version 19 introduced a breaking change to the `facet_terminate`, `class_terminate`
    and `itsystem_terminate` mutators inlining the validity property.
    Version 18 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 18."""

    version = 18
    schema = GraphQLSchema
