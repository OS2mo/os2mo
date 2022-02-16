#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from asyncio import gather
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import cast
from typing import Optional
from uuid import UUID

import strawberry
from pydantic import parse_obj_as
from pydantic import ValidationError
from strawberry.arguments import UNSET
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
from mora.graphapi.dataloaders import get_itsystems
from mora.graphapi.dataloaders import get_itusers
from mora.graphapi.dataloaders import get_kles
from mora.graphapi.dataloaders import get_leaves
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.dataloaders import get_managers
from mora.graphapi.dataloaders import get_org_units
from mora.graphapi.dataloaders import get_related_units
from mora.graphapi.dataloaders import get_roles
from mora.graphapi.dataloaders import MOModel
from mora.graphapi.health import health_map
from mora.graphapi.middleware import set_graphql_args
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.models import HealthRead
from mora.graphapi.schema import Address
from mora.graphapi.schema import Association
from mora.graphapi.schema import Class
from mora.graphapi.schema import Employee
from mora.graphapi.schema import Engagement
from mora.graphapi.schema import Facet
from mora.graphapi.schema import Health
from mora.graphapi.schema import ITSystem
from mora.graphapi.schema import ITUser
from mora.graphapi.schema import KLE
from mora.graphapi.schema import Leave
from mora.graphapi.schema import Manager
from mora.graphapi.schema import OpenValidityModel
from mora.graphapi.schema import Organisation
from mora.graphapi.schema import OrganisationUnit
from mora.graphapi.schema import RelatedUnit
from mora.graphapi.schema import Response
from mora.graphapi.schema import Role
from mora.graphapi.schema import Version


# --------------------------------------------------------------------------------------
# Reads Query
# --------------------------------------------------------------------------------------


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    @strawberry.field(
        description="Get a list of all addresses, optionally by uuid(s)",
    )
    async def addresses(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Address]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["address_loader"], uuids)
        return cast(list[Response[Address]], await get_addresses())

    # Associations
    # ---------
    @strawberry.field(
        description="Get a list of all Associations, optionally by uuid(s)",
    )
    async def associations(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Association]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["association_loader"], uuids)
        return cast(list[Response[Association]], await get_associations())

    # Classes
    # -------
    @strawberry.field(
        description="Get a list of all classes, optionally by uuid(s)",
    )
    async def classes(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Class]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["class_loader"], uuids)
        return cast(list[Response[Class]], await get_classes())

    # Employees
    # ---------
    @strawberry.field(
        description="Get a list of all employees, optionally by uuid(s)",
    )
    async def employees(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Employee]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["employee_loader"], uuids)
        return cast(list[Response[Employee]], await get_employees())

    # Engagements
    # -----------
    @strawberry.field(
        description="Get a list of all engagements, optionally by uuid(s)"
    )
    async def engagements(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Engagement]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["engagement_loader"], uuids)
        return cast(list[Response[Engagement]], await get_engagements())

    # Facets
    # ------
    @strawberry.field(
        description="Get a list of all facets, optionally by uuid(s)",
    )
    async def facets(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Facet]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["facet_loader"], uuids)
        return cast(list[Response[Facet]], await get_facets())

    # ITSystem
    # ---------
    @strawberry.field(
        description="Get a list of all ITSystems, optionally by uuid(s)",
    )
    async def itsystems(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[ITSystem]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["itsystem_loader"], uuids)
        return cast(list[Response[ITSystem]], await get_itsystems())

    # ITUser
    # ---------
    @strawberry.field(
        description="Get a list of all ITUsers, optionally by uuid(s)",
    )
    async def itusers(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[ITUser]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["ituser_loader"], uuids)
        return cast(list[Response[ITUser]], await get_itusers())

    # KLE
    # ---------
    @strawberry.field(
        description="Get a list of all KLE's, optionally by uuid(s)",
    )
    async def kles(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[KLE]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["kle_loader"], uuids)
        return cast(list[Response[KLE]], await get_kles())

    # Leave
    # -----
    @strawberry.field(description="Get a list of all leaves, optionally by uuid(s)")
    async def leaves(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Leave]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["leave_loader"], uuids)
        return cast(list[Response[Leave]], await get_leaves())

    # Managers
    # --------
    @strawberry.field(
        description="Get a list of all managers, optionally by uuid(s)",
    )
    async def managers(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Manager]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["manager_loader"], uuids)
        return cast(list[Response[Manager]], await get_managers())

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Organisational Units
    # --------------------
    @strawberry.field(
        description="Get a list of all organisation units, optionally by uuid(s)",
    )
    async def org_units(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[OrganisationUnit]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["org_unit_loader"], uuids)
        return cast(list[Response[OrganisationUnit]], await get_org_units())

    # Related Units
    # ---------
    @strawberry.field(
        description=(
            "Get a list of all related organisational units, optionally by uuid(s)"
        ),
    )
    async def related_units(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[RelatedUnit]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["rel_unit_loader"], uuids)
        return cast(list[Response[RelatedUnit]], await get_related_units())

    # Roles
    # ---------
    @strawberry.field(
        description="Get a list of all roles, optionally by uuid(s)",
    )
    async def roles(
        self,
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ) -> list[Response[Role]]:
        set_date_interval(from_date, to_date)
        if uuids is not None:
            return await get_by_uuid(info.context["role_loader"], uuids)
        return cast(list[Response[Role]], await get_roles())

    # Version
    # -------
    @strawberry.field(
        description="Get component versions",
    )
    async def version(self) -> Version:
        return Version()

    # Health
    # ------
    @strawberry.field(
        description="Get a list of all health checks, optionally by identifier(s)",
    )
    async def healths(self, identifiers: Optional[list[str]] = None) -> list[Health]:
        healthchecks = set(health_map.keys())
        if identifiers is not None:
            healthchecks = healthchecks.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"identifier": identifier}

        healths = list(map(construct, healthchecks))
        parsed_healths = parse_obj_as(list[HealthRead], healths)
        return cast(list[Health], parsed_healths)


# --------------------------------------------------------------------------------------
# Auxiliary functions
# --------------------------------------------------------------------------------------


def set_date_interval(
    from_date: Optional[datetime], to_date: Optional[datetime]
) -> None:
    """Set the date interval for GraphQL queries to support bitemporal lookups.

    Args:
        from_date: The lower bound of the request interval
        to_date: The upper bound of the request interval

    Raises:
        ValueError: If lower bound is none and upper bound is unset
        ValueError: If the interval is invalid, e.g. lower > upper
    """
    if from_date is UNSET:
        from_date = datetime.now(tz=timezone.utc)
    if to_date is UNSET:
        if from_date is None:
            raise ValueError(
                "Cannot infer UNSET to_date from interval starting at -infinity"
            )
        to_date = from_date + timedelta(milliseconds=1)
    try:
        interval = OpenValidityModel(from_date=from_date, to_date=to_date)
    except ValidationError as v_error:
        # Pydantic errors are ugly in GraphQL so we get the msg part only
        message = ", ".join([err["msg"] for err in v_error.errors()])
        raise ValueError(message)

    set_graphql_args(interval.dict())


async def get_by_uuid(
    dataloader: DataLoader, uuids: list[UUID]
) -> list[Response[MOModel]]:
    """Get data from a list of UUIDs. Only unique UUIDs are loaded.

    Args:
        dataloader: Strawberry dataloader to use.
        uuids: List of UUIDs to load.

    Returns:
        List of objects found.
    """
    tasks = map(dataloader.load, set(uuids))
    results = await gather(*tasks)
    return results


def get_schema() -> strawberry.Schema:
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


async def get_context() -> dict[str, Any]:
    loaders = await get_loaders()
    return {**loaders}


def setup_graphql(enable_graphiql: bool = False) -> GraphQLRouter:
    schema = get_schema()

    gql_router = GraphQLRouter(
        schema, context_getter=get_context, graphiql=enable_graphiql
    )

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    return gql_router
