# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Related Unit."""

from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo.details import RelatedUnitRead

from ..lazy import LazyOrganisationUnit
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..validity import Validity
from .utils import gen_uuid_field_deprecation
from .utils import to_list
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=RelatedUnitRead,
    description="An organisation unit relation mapping",
)
class RelatedUnit:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: RelatedUnitRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
        User-key of the entity.

        Usually constructed from the user-keys of our organisation units at creation time.

        Examples:
        * \"Administrative <-> Payroll\"
        * \"IT-Support <-> IT-Support`
        * \"Majora School <-> Alias School\"
        """
        )
    )
    async def user_key(self, root: RelatedUnitRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `related_units`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: RelatedUnitRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    org_units_response: Paged[Response[LazyOrganisationUnit]] = strawberry.field(
        resolver=to_paged_response("org_unit")(
            seed_resolver(
                organisation_unit_resolver,
                {"uuids": lambda root: root.org_unit_uuids or []},
            )
        ),
        description=dedent(
            """
            Related organisation units.

            Examples of user-keys:
            * `["Administrative", "Payroll"]`
            * `["IT-Support", "IT-Support]`
            * `["Majora School", "Alias School"]`

            Note:
            The result list should always be of length 2, corresponding to the elements of the bijection.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_units: list[LazyOrganisationUnit] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                organisation_unit_resolver,
                {"uuids": lambda root: root.org_unit_uuids or []},
            )
        ),
        description=dedent(
            """
            Related organisation units.

            Examples of user-keys:
            * `["Administrative", "Payroll"]`
            * `["IT-Support", "IT-Support]`
            * `["Majora School", "Alias School"]

            Note:
            The result list should always be of length 2, corresponding to the elements of the bijection.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_units_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description="UUIDs of the related organisation units.",
        deprecation_reason=gen_uuid_field_deprecation("org_units"),
    )
    async def org_unit_uuids(self, root: RelatedUnitRead) -> list[UUID]:
        return root.org_unit_uuids

    validity: Validity = strawberry.auto
