# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

import strawberry
from strawberry.dataloader import DataLoader
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

from mora.graphapi.dataloaders import get_addresses
from mora.graphapi.dataloaders import get_associations
from mora.graphapi.dataloaders import get_classes
from mora.graphapi.dataloaders import get_employees
from mora.graphapi.dataloaders import get_engagements
from mora.graphapi.dataloaders import get_facets
from mora.graphapi.dataloaders import get_itusers
from mora.graphapi.dataloaders import get_kles
from mora.graphapi.dataloaders import get_leaves
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.dataloaders import get_managers
from mora.graphapi.dataloaders import get_org_units
from mora.graphapi.dataloaders import get_related_units
from mora.graphapi.dataloaders import get_roles
from mora.graphapi.dataloaders import MOModel
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.schema import AddressType
from mora.graphapi.schema import AssociationType
from mora.graphapi.schema import ClassType
from mora.graphapi.schema import EmployeeType
from mora.graphapi.schema import EngagementType
from mora.graphapi.schema import FacetType
from mora.graphapi.schema import ITUserType
from mora.graphapi.schema import KLEType
from mora.graphapi.schema import LeaveType
from mora.graphapi.schema import ManagerType
from mora.graphapi.schema import OrganisationType
from mora.graphapi.schema import OrganisationUnitType
from mora.graphapi.schema import RelatedUnitType
from mora.graphapi.schema import RoleType


async def get_by_uuid(dataloader: DataLoader, uuids: List[UUID]) -> List[MOModel]:
    """Get data by from a list of UUIDs. Only unique UUIDs are loaded.

    Args:
        dataloader (DataLoader): Strawberry dataloader to use.
        uuids (List[UUID]): List of UUIDs to load.

    Returns:
        List[MOModel]: List of models found. We do not return None or duplicates.
    """
    tasks = map(dataloader.load, set(uuids))
    results = await gather(*tasks)
    return list(filter(lambda result: result is not None, results))


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
    )
    async def org(self, info: Info) -> OrganisationType:
        return await info.context["org_loader"].load(0)

    # Organisational Units
    # --------------------
    @strawberry.field(
        description="Get a list of all organisation units, optionally by uuid(s)",
    )
    async def org_units(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[OrganisationUnitType]:
        if uuids is not None:
            return await get_by_uuid(info.context["org_unit_loader"], uuids)
        return await get_org_units()

    # Associations
    # ---------
    @strawberry.field(
        description="Get a list of all Associations, optionally by uuid(s)",
    )
    async def associations(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[AssociationType]:
        if uuids is not None:
            return await get_by_uuid(info.context["association_loader"], uuids)
        return await get_associations()

    # Employees
    # ---------
    @strawberry.field(
        description="Get a list of all employees, optionally by uuid(s)",
    )
    async def employees(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[EmployeeType]:
        if uuids is not None:
            return await get_by_uuid(info.context["employee_loader"], uuids)
        return await get_employees()

    # Engagement
    # ----------
    @strawberry.field(
        description="Get a list of all engagements, optionally by uuid(s)"
    )
    async def engagement(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[EngagementType]:
        if uuids is not None:
            return await get_by_uuid(info.context["engagement_loader"], uuids)
        return await get_engagements()

    # KLE
    # ---------
    @strawberry.field(
        description="Get a list of all KLE's, optionally by uuid(s)",
    )
    async def kle(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[KLEType]:
        if uuids is not None:
            return await get_by_uuid(info.context["kle_loader"], uuids)
        return await get_kles()

    # Addresses
    # ---------
    @strawberry.field(
        description="Get a list of all addresses, optionally by uuid(s)",
    )
    async def address(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[AddressType]:
        if uuids is not None:
            return await get_by_uuid(info.context["address_loader"], uuids)
        return await get_addresses()

    # Leave
    # -----
    @strawberry.field(description="Get a list of all leaves, optionally by uuid(s)")
    async def leave(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[LeaveType]:
        if uuids is not None:
            return await get_by_uuid(info.context["leave_loader"], uuids)
        return await get_leaves()

    # ITUser
    # ---------
    @strawberry.field(
        description="Get a list of all ITUsers, optionally by uuid(s)",
    )
    async def ituser(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[ITUserType]:
        if uuids is not None:
            return await get_by_uuid(info.context["ituser_loader"], uuids)
        return await get_itusers()

    # Roles
    # ---------
    @strawberry.field(
        description="Get a list of all roles, optionally by uuid(s)",
    )
    async def roles(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[RoleType]:
        if uuids is not None:
            return await get_by_uuid(info.context["role_loader"], uuids)
        return await get_roles()

    # Manager
    # -------
    @strawberry.field(
        description="Get a list of all managers, optionally by uuid(s)",
    )
    async def managers(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[ManagerType]:
        if uuids is not None:
            return await get_by_uuid(info.context["manager_loader"], uuids)
        return await get_managers()

    # Classes
    # -------
    @strawberry.field(
        description="Get a list of all classes, optionally by uuid(s)",
    )
    async def classes(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[ClassType]:
        if uuids is not None:
            return await get_by_uuid(info.context["class_loader"], uuids)
        return await get_classes()

    # Relatedunits
    # ---------
    @strawberry.field(
        description="Get a list of all related organisational units, optionally by "
        "uuid(s)",
    )
    async def related_units(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[RelatedUnitType]:
        if uuids is not None:
            return await get_by_uuid(info.context["rel_unit_loader"], uuids)
        return await get_related_units()

    # Facets
    # ------
    @strawberry.field(
        description="Get a list of all facets, optionally by uuid(s)",
    )
    async def facets(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[FacetType]:
        if uuids is not None:
            return await get_by_uuid(info.context["facet_loader"], uuids)
        return await get_facets()


def get_schema():
    schema = strawberry.Schema(
        query=Query,
        # Automatic camelCasing disabled because under_score style is simply better
        #
        # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
        # Excerpt:
        #   Although, no difference was found between identifier styles with respect
        #   to accuracy, results indicate a significant improvement in time and lower
        #   visual effort with the underscore style.
        #
        # Additionally it preserves the naming of the underlying Python functions.
        config=StrawberryConfig(auto_camel_case=False),
        extensions=[
            OpenTelemetryExtension,
            StarletteContextExtension,
        ],
    )
    return schema


async def get_context() -> Dict[str, Any]:
    loaders = await get_loaders()
    return {**loaders}


def setup_graphql():
    schema = get_schema()
    gql_router = GraphQLRouter(schema, context_getter=get_context)

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    return gql_router
