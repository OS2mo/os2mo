#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from asyncio import gather
from collections.abc import Callable
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
from strawberry.file_uploads import Upload
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.dataloaders import MOModel
from mora.graphapi.files import list_files
from mora.graphapi.files import save_file
from mora.graphapi.health import health_map
from mora.graphapi.middleware import set_graphql_dates
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.models import FileRead
from mora.graphapi.models import FileStore
from mora.graphapi.models import HealthRead
from mora.graphapi.schema import Address
from mora.graphapi.schema import Association
from mora.graphapi.schema import Class
from mora.graphapi.schema import Employee
from mora.graphapi.schema import Engagement
from mora.graphapi.schema import EngagementAssociation
from mora.graphapi.schema import Facet
from mora.graphapi.schema import File
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


def create_resolver(getter: str, loader: str, static: bool = False) -> Callable:
    """Create a field resolver by specifying getter and loader.

    Args:
        getter: Name of the getter to use.
        loader: Name of the loader to use.

    Returns:
        Callable: Resolver using specified getters/loaders from
            the context.
    """
    if static:

        async def resolve_static(  # type: ignore
            info: Info, uuids: Optional[list[UUID]] = None
        ):
            """Resolve queries with no validity, i.e. class/facet/itsystem."""
            dates = get_date_interval(None, None)  # from -inf to inf
            set_graphql_dates(dates)
            if uuids is not None:
                return await get_by_uuid(info.context[loader], uuids)
            return await info.context[getter]()

        return resolve_static

    async def resolve_query(  # type: ignore
        info: Info,
        uuids: Optional[list[UUID]] = None,
        from_date: Optional[datetime] = UNSET,
        to_date: Optional[datetime] = UNSET,
    ):
        """Resolve a query using the specified arguments.

        Args:
            uuids: Only retrieve these UUIDs. Defaults to None.
            from_date: Lower bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case from_date is today.
            to_date: Upper bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case to_date is from_date + 1 ms.

        Returns:
            List of response objects based on getters/loaders.

        Note:
            The default behaviour of from_date and to_date, i.e. both being
            UNSET, is equivalent to validity=present in the service API.
        """
        dates = get_date_interval(from_date, to_date)
        set_graphql_dates(dates)
        if uuids is not None:
            return await get_by_uuid(info.context[loader], uuids)
        return await info.context[getter]()

    return resolve_query


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: list[Response[Address]] = strawberry.field(
        resolver=create_resolver("address_getter", "address_loader"),
        description="Get a list of all addresses, optionally by uuid(s)",
    )

    # Associations
    # ---------
    associations: list[Response[Association]] = strawberry.field(
        resolver=create_resolver("association_getter", "association_loader"),
        description="Get a list of all Associations, optionally by uuid(s)",
    )

    # Classes
    # -------
    classes: list[Class] = strawberry.field(
        resolver=create_resolver("class_getter", "class_loader", static=True),
        description="Get a list of all classes, optionally by uuid(s)",
    )

    # Employees
    # ---------
    employees: list[Response[Employee]] = strawberry.field(
        resolver=create_resolver("employee_getter", "employee_loader"),
        description="Get a list of all employees, optionally by uuid(s)",
    )

    # Engagements
    # -----------
    engagements: list[Response[Engagement]] = strawberry.field(
        resolver=create_resolver("engagement_getter", "engagement_loader"),
        description="Get a list of all engagements, optionally by uuid(s)",
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: list[Response[EngagementAssociation]] = strawberry.field(
        resolver=create_resolver(
            "engagement_association_getter", "engagement_association_loader"
        ),
        description="Get a list of engagement associations",
    )

    # Facets
    # ------
    facets: list[Facet] = strawberry.field(
        resolver=create_resolver("facet_getter", "facet_loader", static=True),
        description="Get a list of all facets, optionally by uuid(s)",
    )

    # ITSystems
    # ---------
    itsystems: list[ITSystem] = strawberry.field(
        resolver=create_resolver("itsystem_getter", "itsystem_loader", static=True),
        description="Get a list of all ITSystems, optionally by uuid(s)",
    )

    # ITUsers
    # -------
    itusers: list[Response[ITUser]] = strawberry.field(
        resolver=create_resolver("ituser_getter", "ituser_loader"),
        description="Get a list of all ITUsers, optionally by uuid(s)",
    )

    # KLEs
    # ----
    kles: list[Response[KLE]] = strawberry.field(
        resolver=create_resolver("kle_getter", "kle_loader"),
        description="Get a list of all KLE's, optionally by uuid(s)",
    )

    # Leave
    # -----
    leaves: list[Response[Leave]] = strawberry.field(
        resolver=create_resolver("leave_getter", "leave_loader"),
        description="Get a list of all leaves, optionally by uuid(s)",
    )

    # Managers
    # --------
    managers: list[Response[Manager]] = strawberry.field(
        resolver=create_resolver("manager_getter", "manager_loader"),
        description="Get a list of all managers, optionally by uuid(s)",
    )

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
    org_units: list[Response[OrganisationUnit]] = strawberry.field(
        resolver=create_resolver("org_unit_getter", "org_unit_loader"),
        description="Get a list of all organisation units, optionally by uuid(s)",
    )

    # Related Units
    # ---------
    related_units: list[Response[RelatedUnit]] = strawberry.field(
        resolver=create_resolver("rel_unit_getter", "rel_unit_loader"),
        description="Get a list of related organisation units, optionally by uuid(s)",
    )

    # Roles
    # ---------
    roles: list[Response[Role]] = strawberry.field(
        resolver=create_resolver("role_getter", "role_loader"),
        description="Get a list of all roles, optionally by uuid(s)",
    )

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

    # Files
    # -----
    @strawberry.field(
        description="Get a list of all files",
    )
    async def files(self, file_store: FileStore) -> list[File]:
        files = list_files(file_store)
        parsed_files = map(
            lambda file_name: FileRead(file_store=file_store, file_name=file_name),
            files,
        )
        return cast(list[File], parsed_files)

    @strawberry.field(
        description="Get base64 encoded ascii filecontents",
    )
    async def download_file(self, file_store: FileStore, file_name: str) -> File:
        return cast(File, FileRead(file_store=file_store, file_name=file_name))


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Upload a file")
    async def upload_file(
        self, file_store: FileStore, file: Upload, force: bool = False
    ) -> str:
        file_name = file.filename
        file_bytes = await file.read()
        save_file(file_store, file_name, file_bytes, force)
        return "OK"


# --------------------------------------------------------------------------------------
# Auxiliary functions
# --------------------------------------------------------------------------------------


def get_date_interval(
    from_date: Optional[datetime] = UNSET, to_date: Optional[datetime] = UNSET
) -> OpenValidityModel:
    """Get the date interval for GraphQL queries to support bitemporal lookups.

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
    return interval


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
        mutation=Mutation,
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
