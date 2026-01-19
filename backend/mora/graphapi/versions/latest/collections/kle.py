# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - KLE."""

from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.fields import Metadata
from mora.graphapi.gmodels.mo.details import KLERead

from ....version import Version as GraphQLVersion
from ..lazy import LazyClass
from ..lazy import LazyOrganisationUnit
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..validity import Validity
from .utils import force_none_return_wrapper
from .utils import gen_uuid_field_deprecation
from .utils import raise_force_none_return_if_uuid_none
from .utils import to_list
from .utils import to_one
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=KLERead,
    description=dedent(
        """
        KLE responsibility mapping.

        KLE stands for "Kommunernes Landsforenings Emnesystematik" which is a municipality taxonomy for mapping out municipality tasks.

        In OS2mo KLE responsibilities can be mapped to organisation units to signify that a given organisational unit operates within certain municipality tasks.
        Adding KLE responsibilities to organisational units can help out with regards to GDPR by identifying which organisational units operate with sensitive tasks.

        The KLE numbers themselves are dot seperated structured numbers alike this:
        * "00.75.00": General data exchanges
        * "21.02.05": Library study cafes
        * "32.15.08": Alimony

        The first number specifies the main-group, such as:
        * "00": Municipality operations (Kommunens styrelse)
        * "21": Libraries
        * "31": Monetary benefits

        The second number specifies the group, such as (for libraries):
        * "02": On-site usage
        * "05": AV Materials
        * "20": Online services

        The third and final number specifies the topic, such as (for library on-site usage):
        * "00": General usage
        * "05": Study cafes
        * "10": Study centers

        Some KLE ranges are pre-reserved by The National Association of Municipalities (Kommunernes Landsforenings), however outside of these pre-reserved ranges municipalies are allowed to add their own local numbers.
        Specifically no main-groups can be added, only groups and topics, both above 79.

        For more details see: https://www.kle-online.dk
        """
    ),
)
class KLE:
    kle_number__v22: LazyClass = strawberry.field(
        name="kle_number",
        resolver=to_one(
            seed_resolver(
                class_resolver, {"uuids": lambda root: [root.kle_number_uuid]}
            )
        ),
        description=dedent(
            """
            The KLE number specifies the responsibility.

            For more details read the `KLE` description.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        metadata=Metadata(version=lambda v: v <= GraphQLVersion.VERSION_22),
    )

    kle_number_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.kle_number_uuid),
        description=dedent(
            """
            The KLE number specifies the responsibility.

            For more details read the `KLE` description.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    kle_number__v23: list[LazyClass] = strawberry.field(
        name="kle_number",
        resolver=to_list(
            seed_resolver(
                class_resolver, {"uuids": lambda root: [root.kle_number_uuid]}
            )
        ),
        description=dedent(
            """
            The KLE number specifies the responsibility.

            For more details read the `KLE` description.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_23),
        deprecation_reason="Use 'kle_number_response' instead. Will be removed in a future version of OS2mo.",
    )

    kle_aspects_response: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response("class")(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: root.kle_aspect_uuids or []},
            )
        ),
        description=dedent(
            """
            KLE Aspects.

            The KLE aspect describes the kind of relationship the organisation unit has with the responsibility given by the KLE number.

            Examples of user-keys:
            * "Insight"
            * "Executive"
            * "Responsible"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    kle_aspects: list[LazyClass] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: root.kle_aspect_uuids or []},
            )
        ),
        description=dedent(
            """
            KLE Aspects.

            The KLE aspect describes the kind of relationship the organisation unit has with the responsibility given by the KLE number.

            Examples of user-keys:
            * "Insight"
            * "Executive"
            * "Responsible"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'kle_aspects_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="org_unit", uuid=root.org_unit_uuid)
        if root.org_unit_uuid
        else None,
        description=dedent(
            """
            The organisation unit the responsibility is mapped to.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    organisation_unit_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.org_unit_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            The organisation unit the responsibility is mapped to.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `kle`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: KLERead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: KLERead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to be set to the kle number itself.

            Examples:
            * "00.75.00"
            * "21.02.05"
            * "32.15.08"
            """
        )
    )
    async def user_key(self, root: KLERead) -> str:
        return root.user_key

    @strawberry.field(
        description="UUID of the KLE number.",
        deprecation_reason=gen_uuid_field_deprecation("kle_number"),
    )
    async def kle_number_uuid(self, root: KLERead) -> UUID:
        return root.kle_number_uuid

    @strawberry.field(
        description="List of UUIDs of the KLE aspect.",
        deprecation_reason=gen_uuid_field_deprecation("kle_aspects"),
    )
    async def kle_aspect_uuids(self, root: KLERead) -> list[UUID]:
        return root.kle_aspect_uuids

    @strawberry.field(
        description="UUID of the organisation unit related to the KLE.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: KLERead) -> UUID:
        return root.org_unit_uuid

    validity: Validity = strawberry.auto
