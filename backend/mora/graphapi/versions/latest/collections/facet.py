# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Facet."""

from textwrap import dedent
from uuid import UUID

import strawberry

from ..lazy import LazyClass
from ..lazy import LazyFacet
from ..models import ClassRead
from ..models import FacetRead
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import facet_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import OpenValidity
from .utils import gen_uuid_field_deprecation
from .utils import to_list
from .utils import to_only
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=FacetRead,
    description="The key component of the class/facet choice setup",
)
class Facet:
    classes_responses: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response("class")(
            seed_resolver(class_resolver, {"facets": lambda root: [root.uuid]})
        ),
        description="Associated classes",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    classes: list[LazyClass] = strawberry.field(
        resolver=to_list(
            seed_resolver(class_resolver, {"facets": lambda root: [root.uuid]})
        ),
        description="Associated classes",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'classes_response' instead. Will be removed in a future version of OS2mo.",
    )

    parent_response: Response[LazyFacet] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="facet", uuid=root.parent_uuid)
        if root.parent_uuid
        else None,
        description=dedent(
            """
            Parent facet.

            Almost always `null` as facet hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `children`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    parent: LazyFacet | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                facet_resolver, {"uuids": lambda root: uuid2list(root.parent_uuid)}
            )
        ),
        description=dedent(
            """
            Parent facet.

            Almost always `null` as facet hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `children`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
        deprecation_reason="Use 'parent_response' instead. Will be removed in a future version of OS2mo.",
    )

    children_response: Paged[Response[LazyFacet]] = strawberry.field(
        resolver=to_paged_response("facet")(
            seed_resolver(
                facet_resolver,
                {"parents": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Facet children.

            Almost always an empty list as facet hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `parent`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    children: list[LazyFacet] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                facet_resolver,
                {"parents": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Facet children.

            Almost always an empty list as facet hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `parent`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
        deprecation_reason="Use 'children_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `facet`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: FacetRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: FacetRead) -> UUID:
        return root.uuid

    # TODO: Document this
    user_key: str = strawberry.auto

    @strawberry.field(
        description=dedent(
            """
            Published state of the facet object.

            Whether the facet is published or not, aka. if it should be shown.

            Examples:
            * `"Publiceret"`
            * `"IkkePubliceret"`
            * `"Normal"`

            Note:
            Return change may change to an enum in the future.

            May eventually be superseeded by validities on facets.
            """
        )
    )
    # TODO: Change to returning an enum instead, remove optional
    async def published(self, root: FacetRead) -> str | None:
        return root.published

    @strawberry.field(
        description="UUID of the related organisation.",
        deprecation_reason=dedent(
            """
            The root organisation concept will be removed in a future version of OS2mo.
            """
        ),
    )
    async def org_uuid(self, root: ClassRead) -> UUID:
        return root.org_uuid

    @strawberry.field(
        description="UUID of the parent facet.",
        deprecation_reason=gen_uuid_field_deprecation("parent"),
    )
    async def parent_uuid(self, root: FacetRead) -> UUID | None:
        return root.parent_uuid

    @strawberry.field(
        description=dedent(
            """
            Description of the facet object.

            Almost always `""`.
            """
        ),
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            This field is almost never used, and serves no real purpose.
            May be reintroduced in the future if the demand for it increases.
            """
        ),
    )
    async def description(self, root: FacetRead) -> str | None:
        return root.description

    validity: OpenValidity = strawberry.auto
