# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

import strawberry
from strawberry.extensions.tracing import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

from mora.graphapi.dataloaders import get_addresses
from mora.graphapi.dataloaders import get_employees
from mora.graphapi.dataloaders import get_engagements
from mora.graphapi.dataloaders import get_leaves
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.dataloaders import get_kles
from mora.graphapi.dataloaders import get_org_units
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.schema import EmployeeType
from mora.graphapi.schema import EngagementType
from mora.graphapi.schema import KLEType
from mora.graphapi.schema import AddressType
from mora.graphapi.schema import LeaveType
from mora.graphapi.schema import OrganisationType
from mora.graphapi.schema import OrganisationUnitType


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
        if uuids:
            tasks = map(info.context["org_unit_loader"].load, uuids)
            org_units = await gather(*tasks)
            return list(filter(lambda ou: ou is not None, org_units))
        return await get_org_units()

    # Employees
    # ---------
    @strawberry.field(
        description="Get a list of all employees, optionally by uuid(s)",
    )
    async def employees(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[EmployeeType]:
        if uuids:
            tasks = map(info.context["employee_loader"].load, uuids)
            employees = await gather(*tasks)
            return list(filter(lambda empl: empl is not None, employees))
        return await get_employees()

    # Engagement
    # ----------
    @strawberry.field(
        description="Get a list of all engagements, optionally by uuid(s)"
    )
    async def engagement(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[EngagementType]:
        if uuids:
            tasks = map(info.context["engagement_loader"].load, uuids)
            engagements = await gather(*tasks)
            return list(filter(lambda eng: eng is not None, engagements))
        return await get_engagements()

    # KLE
    # ---------
    @strawberry.field(
        description="Get a list of all KLE's, optionally by uuid(s)",
    )
    async def kle(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[KLEType]:
        if uuids:
            tasks = map(info.context["kle_loader"].load, uuids)
            kles = await gather(*tasks)
            return list(filter(lambda kle: kle is not None, kles))
        return await get_kles()

    # Addresses
    # ---------
    @strawberry.field(
        description="Get a list of all addresses, optionally by uuid(s)",
    )
    async def address(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[AddressType]:
        if uuids:
            tasks = map(info.context["address_loader"].load, uuids)
            addresses = await gather(*tasks)
            return list(filter(lambda addr: addr is not None, addresses))
        return await get_addresses()

    # Leave
    # -----
    @strawberry.field(description="Get a list of all leaves, optionally by uuid(s)")
    async def leave(
        self, info: Info, uuids: Optional[List[UUID]] = None
    ) -> List[LeaveType]:
        if uuids:
            tasks = map(info.context["leave_loader"].load, uuids)
            leaves = await gather(*tasks)
            return list(filter(lambda leave: leave is not None, leaves))
        return await get_leaves()


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
