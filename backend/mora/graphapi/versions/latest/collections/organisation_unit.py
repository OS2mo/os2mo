# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Organisation Unit."""

from textwrap import dedent
from typing import TYPE_CHECKING
from typing import Annotated
from uuid import UUID

import strawberry
from strawberry.types import Info

from mora.graphapi.custom_schema import get_version
from mora.graphapi.fields import Metadata
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead
from mora.service import org

from ....version import Version as GraphQLVersion
from ..filters import ManagerFilter
from ..filters import OrganisationUnitFilter
from ..filters import OwnerFilter
from ..lazy import LazyAddress
from ..lazy import LazyAssociation
from ..lazy import LazyClass
from ..lazy import LazyEngagement
from ..lazy import LazyITUser
from ..lazy import LazyKLE
from ..lazy import LazyLeave
from ..lazy import LazyManager
from ..lazy import LazyOrganisationUnit
from ..lazy import LazyOwner
from ..lazy import LazyRelatedUnit
from ..models import AddressRead
from ..models import ClassRead
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import address_resolver
from ..resolvers import association_resolver
from ..resolvers import class_resolver
from ..resolvers import engagement_resolver
from ..resolvers import it_user_resolver
from ..resolvers import kle_resolver
from ..resolvers import leave_resolver
from ..resolvers import manager_resolver
from ..resolvers import organisation_unit_child_count
from ..resolvers import organisation_unit_has_children
from ..resolvers import organisation_unit_resolver
from ..resolvers import owner_resolver
from ..resolvers import related_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..seed_resolver import strip_args
from ..utils import uuid2list
from ..validity import Validity
from .utils import gen_uuid_field_deprecation
from .utils import to_arbitrary_only
from .utils import to_list
from .utils import to_only
from .utils import to_paged_response
from .utils import to_response

if TYPE_CHECKING:
    pass


@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRead,
    description="Organisation unit within the organisation tree",
)
class OrganisationUnit:
    @strawberry.field(
        description=dedent(
            """
            The parent organisation unit in the organisation tree.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )
    async def parent_response(
        self, root: OrganisationUnitRead, info: Info
    ) -> Response[LazyOrganisationUnit] | None:
        # Root units aren't actually at the root, but have the special "org"
        # UUID as parent. That's confusing. Remove it.
        if root.parent_uuid is None:  # pragma: no cover
            return None
        if get_version(info.schema) >= GraphQLVersion.VERSION_28:
            if root.parent_uuid == await org.get_configured_organisation_uuid():
                return None
        return Response(model=OrganisationUnitRead, uuid=root.parent_uuid)  # type: ignore

    parent: LazyOrganisationUnit | None = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                organisation_unit_resolver,
                {"uuids": lambda root: uuid2list(root.parent_uuid)},
            )
        ),
        description=dedent(
            """
            The parent organisation unit in the organisation tree.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'parent_response' instead. Will be removed in a future version of OS2mo.",
    )

    root_response: Response[LazyOrganisationUnit] | None = strawberry.field(
        resolver=to_response(OrganisationUnitRead)(
            strip_args(
                seed_resolver(
                    organisation_unit_resolver,
                    {
                        "descendant": lambda root: OrganisationUnitFilter(
                            uuids=[root.uuid]
                        ),
                        "parent": lambda root: None,
                    },
                ),
                # We filter out:
                # * 'cursor' and 'limit' as there is at most one object returned
                # * 'filter' as you cannot filter on uuids and something else at once
                # Once the resolver supports mixed uuid and non-uuid filtering we may
                # remove 'filter' from the list here.
                {"cursor", "limit", "filter"},
            )
        ),
        description=dedent(
            """
            The top-unit (root) of the organisation unit, in the hierarchy.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    root: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=to_list(
            seed_resolver(
                organisation_unit_resolver,
                {
                    "descendant": lambda root: OrganisationUnitFilter(
                        uuids=[root.uuid]
                    ),
                    "parent": lambda root: None,
                },
            )
        ),
        description=dedent(
            """
            The top-unit (root) of the organisation unit, in the hierarchy.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'root_response' instead. Will be removed in a future version of OS2mo.",
    )

    # TODO: Add Paged[Response[LazyClass]] for ancestors_response
    @strawberry.field(
        description=dedent(
            """
            All ancestor organisational units in the organisation tree.

            The result of collecting organisational units by following `parent` until `parent` becomes `null`.
            I.e. the list of all ancestors on the way to the organisation tree root.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )
    async def ancestors(
        self, root: OrganisationUnitRead, info: Info
    ) -> list[LazyOrganisationUnit]:
        """Get all ancestors in the organisation tree.

        Returns:
            A list of all the ancestors.
        """
        parent = await OrganisationUnit.parent(root=root, info=info)  # type: ignore
        if parent is None:
            return []
        ancestors = await OrganisationUnit.ancestors(self=self, root=parent, info=info)  # type: ignore
        return [parent] + ancestors

    children_response: Paged[Response[LazyOrganisationUnit]] = strawberry.field(
        resolver=to_paged_response(OrganisationUnitRead)(
            seed_resolver(
                organisation_unit_resolver,
                {
                    "parent": lambda root: OrganisationUnitFilter(
                        uuids=[root.uuid],
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description=dedent(
            """
            The immediate descendants in the organisation tree
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    children: list[LazyOrganisationUnit] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                organisation_unit_resolver,
                {
                    "parent": lambda root: OrganisationUnitFilter(
                        uuids=[root.uuid],
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description=dedent(
            """
            The immediate descendants in the organisation tree
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'children_response' instead. Will be removed in a future version of OS2mo.",
    )

    child_count: int = strawberry.field(
        resolver=seed_resolver(
            organisation_unit_child_count,
            {
                "parent": lambda root: OrganisationUnitFilter(
                    uuids=[root.uuid],
                    from_date=None,
                    to_date=None,
                )
            },
        ),
        description="Children count of the organisation unit. For performance, consider if `has_children` can answer your query instead.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    has_children: bool = strawberry.field(
        resolver=seed_resolver(
            organisation_unit_has_children,
            {
                "parent": lambda root: OrganisationUnitFilter(
                    uuids=[root.uuid],
                    from_date=None,
                    to_date=None,
                )
            },
        ),
        description="Returns whether the organisation unit has children.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Should this be a list?
    unit_hierarchy_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.org_unit_hierarchy)
        if root.org_unit_hierarchy
        else None,
        description=dedent(
            """
            Organisation unit hierarchy.

            Can be used to label an organisational structure to belong to a certain subset of the organisation tree.

            Examples of user-keys:
            * "Line-management"
            * "Self-owned institution"
            * "Outside organisation"
            * "Hidden"

            Note:
            The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
        """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    # TODO: Add _uuid suffix to RAModel and remove _model suffix here
    # TODO: Should this be a list?
    org_unit_hierarchy_model: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.org_unit_hierarchy)},
            )
        ),
        description=dedent(
            """
            Organisation unit hierarchy.

            Can be used to label an organisational structure to belong to a certain subset of the organisation tree.

            Examples of user-keys:
            * "Line-management"
            * "Self-owned institution"
            * "Outside organisation"
            * "Hidden"

            Note:
            The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
        """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'unit_hierarchy_response' instead. Will be removed in a future version of OS2mo.",
    )

    unit_type_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.unit_type_uuid)
        if root.unit_type_uuid
        else None,
        description=dedent(
            """
            Organisation unit type.

            Organisation units can represent a lot of different classes of hierarchical structures.
            Sometimes they represent cooperations, governments, NGOs or other true organisation types.
            Oftentimes they represent the inner structure of these organisations.
            Othertimes they represent project management structures such as project or teams.

            This field is used to distriguish all these different types of organisations.

            Examples of user-keys:
            * "Private Company"
            * "Educational Institution"
            * "Activity Center"
            * "Daycare"
            * "Team"
            * "Project"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    unit_type: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver, {"uuids": lambda root: uuid2list(root.unit_type_uuid)}
            )
        ),
        description=dedent(
            """
            Organisation unit type.

            Organisation units can represent a lot of different classes of hierarchical structures.
            Sometimes they represent cooperations, governments, NGOs or other true organisation types.
            Oftentimes they represent the inner structure of these organisations.
            Othertimes they represent project management structures such as project or teams.

            This field is used to distriguish all these different types of organisations.

            Examples of user-keys:
            * "Private Company"
            * "Educational Institution"
            * "Activity Center"
            * "Daycare"
            * "Team"
            * "Project"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'unit_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    unit_level_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.org_unit_level_uuid)
        if root.org_unit_level_uuid
        else None,
        # TODO: Document this
        description=dedent(
            """
            Organisation unit level.

            Examples of user-keys:
            * "N1"
            * "N5"
            * "N7"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    org_unit_level: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.org_unit_level_uuid)},
            )
        ),
        # TODO: Document this
        description=dedent(
            """
            Organisation unit level.

            Examples of user-keys:
            * "N1"
            * "N5"
            * "N7"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'unit_level_response' instead. Will be removed in a future version of OS2mo.",
    )

    time_planning_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.time_planning_uuid)
        if root.time_planning_uuid
        else None,
        # TODO: Document this
        description=dedent(
            """
            Time planning strategy.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    time_planning: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.time_planning_uuid)},
            )
        ),
        # TODO: Document this
        description=dedent(
            """
            Time planning strategy.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'time_planning_response' instead. Will be removed in a future version of OS2mo.",
    )

    engagements_response: Paged[Response[LazyEngagement]] = strawberry.field(
        resolver=to_paged_response(EngagementRead)(
            seed_resolver(
                engagement_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Engagements for the organistion unit.

            May be an empty list if the organistion unit does not have any people employeed.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagements: list[LazyEngagement] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                engagement_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Engagements for the organistion unit.

            May be an empty list if the organistion unit does not have any people employeed.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagements_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `org_unit`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: OrganisationUnitRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: OrganisationUnitRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to be set to the key used in external systems.

            Examples:
            * "CBCM"
            * "SPHA"
            * "1414"
            """
        )
    )
    async def user_key(self, root: OrganisationUnitRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            Human readable name of the organisation unit.

            This is the value that should be shown to users in UIs.

            Examples:
            * "Lunderskov skole"
            * "IT-Support"
            * "Teknik og Miljø"
            """
        )
    )
    async def name(self, root: OrganisationUnitRead) -> str:
        return root.name

    @strawberry.field(
        name="managers",
        description=dedent(
            """
            Managerial roles for the organisation unit.

            May be empty in which case managers are usually inherited from parents.
            See the `inherit`-flag for details.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
        metadata=Metadata(version=lambda v: v <= GraphQLVersion.VERSION_23),
    )
    async def managers__v23(
        self,
        root: OrganisationUnitRead,
        info: Info,
        filter: ManagerFilter | None = None,
        inherit: Annotated[
            bool,
            strawberry.argument(
                description=dedent(
                    """
                    Whether to inherit managerial roles or not.

                    If managerial roles exist directly on this organisation unit, the flag does nothing and these managerial roles are returned.
                    However if no managerial roles exist directly, and this flag is:
                    * Not set: An empty list is returned.
                    * Is set: The result from calling `managers` with `inherit=True` on the parent of this organistion unit is returned.

                    Calling with `inherit=True` can help ensure that a manager is always found.
                    """
                )
            ),
        ] = False,
    ) -> list[LazyManager]:
        if filter is None:  # pragma: no cover
            filter = ManagerFilter()
        filter.org_units = [root.uuid]

        resolver = to_list(seed_resolver(manager_resolver))
        return await resolver(root=root, info=info, filter=filter, inherit=inherit)

    managers_response: Paged[Response[LazyManager]] = strawberry.field(
        resolver=to_paged_response(ManagerRead)(
            seed_resolver(
                manager_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Managerial roles for the organisation unit.

            May be empty in which case managers are usually inherited from parents.
            See the `inherit`-flag for details.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_24),
    )

    managers: list[LazyManager] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                manager_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Managerial roles for the organisation unit.

            May be empty in which case managers are usually inherited from parents.
            See the `inherit`-flag for details.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_24),
        deprecation_reason="Use 'managers_response' instead. Will be removed in a future version of OS2mo.",
    )

    # TODO: Add Paged[Response[LazyClass]] for owners_response
    @strawberry.field(
        description=dedent(
            """
            Owner roles for the organisation unit.

            May be empty in which case owners are usually inherited from parents.
            See the `inherit`-flag for details.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )
    async def owners(
        self,
        root: OrganisationUnitRead,
        info: Info,
        filter: OwnerFilter | None = None,
        inherit: Annotated[
            bool,
            strawberry.argument(
                description=dedent(
                    """
                    Whether to inherit owner roles or not.

                    If owner roles exist directly on this organisaion unit, the flag does nothing and these owner roles are returned.
                    However if no owner roles exist directly, and this flag is:
                    * Not set: An empty list is returned.
                    * Is set: The result from calling `owners` with `inherit=True` on the parent of this organistion unit is returned.

                    Calling with `inherit=True` can help ensure that an owner is always found.
                    """
                )
            ),
        ] = False,
    ) -> list[LazyOwner]:
        # TODO: Move inherit to resolver, like `manager_resolver`
        if filter is None:
            filter = OwnerFilter()
        filter.org_units = [root.uuid]

        resolver = to_list(seed_resolver(owner_resolver))
        result = await resolver(root=root, info=info, filter=filter)
        if result:
            return result  # type: ignore
        if not inherit:
            return []
        parent = await OrganisationUnit.parent(root=root, info=info)  # type: ignore
        if parent is None:  # pragma: no cover
            return []
        return await OrganisationUnit.owners(
            self=self, root=parent, info=info, inherit=True
        )

    addresses_response: Paged[Response[LazyAddress]] = strawberry.field(
        resolver=to_paged_response(AddressRead)(
            seed_resolver(
                address_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Addresses for the organisation unit.

            Commonly contain addresses such as, their:
            * Location
            * Contact phone number
            * Contact email
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                address_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Addresses for the organisation unit.

            Commonly contain addresses such as, their:
            * Location
            * Contact phone number
            * Contact email
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
        deprecation_reason="Use 'address_response' instead. Will be removed in a future version of OS2mo.",
    )

    leaves_response: Paged[Response[LazyLeave]] = strawberry.field(
        resolver=to_paged_response(LeaveRead)(
            seed_resolver(
                leave_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Connection to employees leaves of absence relevant for the organisation unit.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                leave_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Connection to employees leaves of absence relevant for the organisation unit.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
        deprecation_reason="Use 'leaves_response' instead. Will be removed in a future version of OS2mo.",
    )

    associations_response: Paged[Response[LazyAssociation]] = strawberry.field(
        resolver=to_paged_response(AssociationRead)(
            seed_resolver(
                association_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Associations for the organistion unit.

            May be an empty list if the organistion unit is purely hierarchical.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                association_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Associations for the organistion unit.

            May be an empty list if the organistion unit is purely hierarchical.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
        deprecation_reason="Use 'associations_response' instead. Will be removed in a future version of OS2mo.",
    )

    itusers_response: Paged[Response[LazyITUser]] = strawberry.field(
        resolver=to_paged_response(ITUserRead)(
            seed_resolver(
                it_user_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            IT (service) accounts.

            May be an empty list if the organistion unit does not have any IT (service) accounts whatsoever.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                it_user_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            IT (service) accounts.

            May be an empty list if the organistion unit does not have any IT (service) accounts whatsoever.
            This situation may occur especially in the middle or the organisation tree.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'itusers_response' instead. Will be removed in a future version of OS2mo.",
    )

    kles_response: Paged[Response[LazyKLE]] = strawberry.field(
        resolver=to_paged_response(KLERead)(
            seed_resolver(
                kle_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            KLE responsibilities for the organisation unit.

            Can help out with regards to GDPR by identifying which organisational units operate with sensitive tasks.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    kles: list[LazyKLE] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                kle_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            KLE responsibilities for the organisation unit.

            Can help out with regards to GDPR by identifying which organisational units operate with sensitive tasks.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
        deprecation_reason="Use 'kles_response' instead. Will be removed in a future version of OS2mo.",
    )

    related_units_response: Paged[Response[LazyRelatedUnit]] = strawberry.field(
        resolver=to_paged_response(RelatedUnitRead)(
            seed_resolver(
                related_unit_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Related units for the organisational unit.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    related_units: list[LazyRelatedUnit] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                related_unit_resolver,
                {"org_units": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Related units for the organisational unit.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
        deprecation_reason="Use 'related_units_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description="UUID of the parent organisation unit.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit_hierarchy_model"),
    )
    async def org_unit_hierarchy(self, root: OrganisationUnitRead) -> UUID | None:
        return root.org_unit_hierarchy

    @strawberry.field(
        description="UUID of the parent organisation unit.",
        deprecation_reason=gen_uuid_field_deprecation("parent"),
    )
    async def parent_uuid(self, root: OrganisationUnitRead, info: Info) -> UUID | None:
        # Root units aren't actually at the root, but have the special "org"
        # UUID as parent. That's confusing. Remove it.
        if root.parent_uuid is None:  # pragma: no cover
            return None
        if get_version(info.schema) >= GraphQLVersion.VERSION_28:
            if root.parent_uuid == await org.get_configured_organisation_uuid():
                return None
        return root.parent_uuid

    @strawberry.field(
        description="UUID of the organisation unit type.",
        deprecation_reason=gen_uuid_field_deprecation("unit_type"),
    )
    async def unit_type_uuid(self, root: OrganisationUnitRead) -> UUID | None:
        return root.unit_type_uuid

    @strawberry.field(
        description="UUID of the organisation unit level.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit_level"),
    )
    async def org_unit_level_uuid(self, root: OrganisationUnitRead) -> UUID | None:
        return root.org_unit_level_uuid

    @strawberry.field(
        description="UUID of the time planning object.",
        deprecation_reason=gen_uuid_field_deprecation("time_planning"),
    )
    async def time_planning_uuid(self, root: OrganisationUnitRead) -> UUID | None:
        return root.time_planning_uuid

    validity: Validity = strawberry.auto
