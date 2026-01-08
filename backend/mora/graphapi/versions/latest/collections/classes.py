# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Class."""

from textwrap import dedent
from uuid import UUID

import strawberry
from strawberry.types import Info

from mora.graphapi.gmodels.mo.details import ITSystemRead

from ..lazy import LazyClass
from ..lazy import LazyFacet
from ..lazy import LazyITSystem
from ..models import ClassRead
from ..models import FacetRead
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import facet_resolver
from ..resolvers import it_system_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import OpenValidity
from .utils import gen_uuid_field_deprecation
from .utils import to_list
from .utils import to_one
from .utils import to_only
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=ClassRead,
    description=dedent(
        """
        A value in the facet sample space.

        Classes can also be thought of as the value component of the facet/class key-value setup.
        """
    ),
)
class Class:
    parent_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.parent_uuid)
        if root.parent_uuid
        else None,
        description=dedent(
            """
            Parent class.

            Almost always `null` as class hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `children`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    parent: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver, {"uuids": lambda root: uuid2list(root.parent_uuid)}
            )
        ),
        description=dedent(
            """
            Parent class.

            Almost always `null` as class hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `children`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'parent_response' instead. Will be removed in a future version of OS2mo.",
    )

    children_response: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response(ClassRead)(
            seed_resolver(
                class_resolver,
                {"parents": lambda root: [root.uuid]},
            ),
        ),
        description=dedent(
            """
            Class children.

            Almost always an empty list as class hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `parent`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    children: list[LazyClass] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                class_resolver,
                {"parents": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Class children.

            Almost always an empty list as class hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.

            The inverse operation of `parent`.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'children_response' instead. Will be removed in a future version of OS2mo.",
    )

    facet_response: Response[LazyFacet] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=FacetRead, uuid=root.facet_uuid),
        description=dedent(
            """
            Facet this class is defined under.

            Examples of user-keys:
            * `"employee_address_type"`
            * `"primary_type"`
            * `"engagement_job_function"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    facet: LazyFacet = strawberry.field(
        resolver=to_one(
            seed_resolver(facet_resolver, {"uuids": lambda root: [root.facet_uuid]})
        ),
        description=dedent(
            """
            Facet this class is defined under.

            Examples of user-keys:
            * `"employee_address_type"`
            * `"primary_type"`
            * `"engagement_job_function"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
        deprecation_reason="Use 'facet_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            Facet of this class's upmost parent.

            The result of following `parent` until `parent` becomes `null`, then calling `facet`.

            Almost always the same as `facet` as class hierarchies are rare.
            Currently mostly used to describe (trade) union hierachies.
            """
        ),
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            Will either be replaced by client-side recursion, an ancestor field or a recursive schema directive.
            For now client-side recursion is the preferred replacement.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )
    async def top_level_facet(self, root: ClassRead, info: Info) -> LazyFacet:
        if root.parent_uuid is None:
            return await Class.facet(root=root, info=info)  # type: ignore[operator]
        # coverage: pause
        parent_node = await Class.parent(root=root, info=info)  # type: ignore[operator,misc]
        return await Class.top_level_facet(self=self, root=parent_node, info=info)
        # coverage: unpause

    it_system_response: Response[LazyITSystem] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ITSystemRead, uuid=root.it_system_uuid)
        if root.it_system_uuid
        else None,
        description=dedent(
            """
            The IT-System associated with the class.

            This is intended to be used for (IT) roles.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    it_system: LazyITSystem | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                it_system_resolver,
                {"uuids": lambda root: uuid2list(root.it_system_uuid)},
            )
        ),
        description=dedent(
            """
            The IT-System associated with the class.

            This is intended to be used for (IT) roles.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
        deprecation_reason="Use 'it_system_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            Full name of the class, exactly the same as `name`.
            """
        ),
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            Returns exactly the same as `name`, use that instead.
            """
        ),
    )
    async def full_name(self, root: ClassRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `class`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ClassRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: ClassRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to the `name` provided on object creation.
            May also be set to the key used in external systems or a system-name.

            Usually also used as the machine "value" for the class.

            Examples:
            * `"primary"`
            * `"PhoneEmployee"`
            * `"Jurist"`
            * `"X-418"`
            """
        )
    )
    async def user_key(self, root: ClassRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            Human readable name of the class.

            This is the value that should be shown to users in UIs.

            Examples:
            * `"Primary"`
            * `"Phone number"`
            * `"Jurist"`
            * `"Paragraph 11 Hire"`
            """
        )
    )
    async def name(self, root: ClassRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            Scope of the class.

            The scope of the class describes the kind of values that can be contained when using the class.
            It has different implications depending on the associated facet.

            Below is a non-exhaustive list of scope values for a non-exhaustive list of facets:

            Facet `visibility`; scope controls visibility classes:
            * `"PUBLIC"`: The entity can be shared publicly.
            * `"SECRET"`: The entity should not be shared publicly.

            Facet `primary_type`; scope controls how primary the class is:
            * `"0"`: Not primary.
            * `"3000"`: Primary.
            * `"5000"`: Explicitly primary / override.

            A lot of facets; scope controls input-validation:
            * `"TEXT"`: The input can be any text string.
            * `"PHONE"`: The input must match OS2mo's phone number regex.
            * `"PNUMBER"`: The input must match OS2mo's p-number regex.
            * `"EMAIL"`: The input must match OS2mo's email regex.
            * `"DAR"`: The input must be a DAR UUID.
            """
        )
    )
    async def scope(self, root: ClassRead) -> str | None:
        return root.scope

    @strawberry.field(
        description=dedent(
            """
            Published state of the class object.

            Whether the class is published or not, aka. if it should be shown.

            Examples:
            * `"Publiceret"`
            * `"IkkePubliceret"`
            * `"Normal"`

            Note:
            Return change may change to an enum in the future.

            May eventually be superseeded by validities on classes.
            """
        )
    )
    # TODO: Change to returning an enum instead, remove optional
    async def published(self, root: ClassRead) -> str | None:
        return root.published

    @strawberry.field(
        description=dedent(
            """
            Example usage.

            Almost always `null`.
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
    async def example(self, root: ClassRead) -> str | None:
        return root.example

    # TODO: Document this better
    owner: UUID | None = strawberry.auto

    @strawberry.field(
        description="UUID of the related facet.",
        deprecation_reason=gen_uuid_field_deprecation("facet"),
    )
    async def facet_uuid(self, root: ClassRead) -> UUID:
        return root.facet_uuid

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
        description="UUID of the employee related to the address.",
        deprecation_reason=gen_uuid_field_deprecation("parent"),
    )
    async def parent_uuid(self, root: ClassRead) -> UUID | None:
        return root.parent_uuid

    @strawberry.field(
        description="The IT-System associated with the class.",
        deprecation_reason=gen_uuid_field_deprecation("it_system"),
    )
    async def it_system_uuid(self, root: ClassRead) -> UUID | None:
        return root.it_system_uuid

    @strawberry.field(
        description="Description of the class",
    )
    async def description(self, root: ClassRead) -> str | None:
        return root.description

    validity: OpenValidity = strawberry.auto
