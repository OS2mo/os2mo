# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task
from asyncio import gather
from collections.abc import Iterable
from itertools import starmap
from typing import Any
from typing import cast
from uuid import UUID

import strawberry
from more_itertools import bucket
from more_itertools import unique_everseen
from pydantic import parse_obj_as
from strawberry.types import Info

from .... import common
from .... import mapping
from .... import util
from ....graphapi.middleware import is_graphql
from ....service import orgunit
from .health import health_map
from .models import ConfigurationRead
from .models import FileRead
from .models import FileStore
from .models import HealthRead
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .resolvers import EmployeeResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import Resolver
from .resolvers import StaticResolver
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Configuration
from .schema import Employee
from .schema import Engagement
from .schema import EngagementAssociation
from .schema import Facet
from .schema import File
from .schema import Health
from .schema import ITSystem
from .schema import ITUser
from .schema import KLE
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import OrganisationUnitRead
from .schema import Paged
from .schema import PageInfo
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version
from .types import Cursor
from mora import lora
from mora.config import get_public_settings
from mora.graphapi.versions.latest.dataloaders import MOModel


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: list[Response[Address]] = strawberry.field(
        resolver=AddressResolver().resolve,
        description="Get a list of all addresses, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: list[Response[Association]] = strawberry.field(
        resolver=AssociationResolver().resolve,
        description="Get a list of all Associations, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: list[Class] = strawberry.field(
        resolver=ClassResolver().resolve,
        description="Get a list of all classes, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: list[Response[Employee]] = strawberry.field(
        resolver=EmployeeResolver().resolve,
        description="Get a list of all employees, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: list[Response[Engagement]] = strawberry.field(
        resolver=EngagementResolver().resolve,
        description="Get a list of all engagements, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: list[Response[EngagementAssociation]] = strawberry.field(
        resolver=Resolver(
            "engagement_association_getter", "engagement_association_loader"
        ).resolve,
        description="Get a list of engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )

    # Facets
    # ------
    facets: list[Facet] = strawberry.field(
        resolver=FacetResolver().resolve,
        description="Get a list of all facets, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: list[ITSystem] = strawberry.field(
        resolver=StaticResolver("itsystem_getter", "itsystem_loader").resolve,
        description="Get a list of all ITSystems, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: list[Response[ITUser]] = strawberry.field(
        resolver=Resolver("ituser_getter", "ituser_loader").resolve,
        description="Get a list of all ITUsers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: list[Response[KLE]] = strawberry.field(
        resolver=Resolver("kle_getter", "kle_loader").resolve,
        description="Get a list of all KLE's, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: list[Response[Leave]] = strawberry.field(
        resolver=Resolver("leave_getter", "leave_loader").resolve,
        description="Get a list of all leaves, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: list[Response[Manager]] = strawberry.field(
        resolver=ManagerResolver().resolve,
        description="Get a list of all managers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org")],
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Organisational Units
    # --------------------
    org_units_old: list[Response[OrganisationUnit]] = strawberry.field(
        resolver=OrganisationUnitResolver().resolve,
        description="Get a list of all organisation units, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    @strawberry.field(
        description="Get a list of all organisation units, optionally by uuid(s)",
        permission_classes=[gen_read_permission("org_unit")],
    )
    async def org_units(self, info: Info) -> list[Response[OrganisationUnit]]:
        c = lora.Connector()
        changed_since = None
        search_fields = {}

        result = await c.organisationenhed.get_all(
            changed_since=changed_since,
            **search_fields,
        )
        result_converted = await _get_obj_effects(c, result)

        result_models = parse_obj_as(list[OrganisationUnitRead], result_converted)  # type: ignore
        uuid_map = group_by_uuid(result_models)

        result_final = list(
            starmap(
                lambda uuid, objects: Response(
                    uuid=uuid, objects=objects
                ),  # noqa: FURB111
                uuid_map.items(),
            )
        )
        return result_final

        # return result

    # Related Units
    # -------------
    related_units: list[Response[RelatedUnit]] = strawberry.field(
        resolver=Resolver("rel_unit_getter", "rel_unit_loader").resolve,
        description="Get a list of related organisation units, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    roles: list[Response[Role]] = strawberry.field(
        resolver=Resolver("role_getter", "role_loader").resolve,
        description="Get a list of all roles, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    # Version
    # -------
    @strawberry.field(
        description="Get component versions",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("version")],
    )
    async def version(self) -> Version:
        return Version()

    # Health
    # ------
    @strawberry.field(
        description="Get a list of all health checks, optionally by identifier(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("health")],
    )
    async def healths(
        self,
        limit: int | None = None,
        # Cursor's input is a Base64 encoded string eg. `Mw==`, but is parsed as an int
        # and returned again as a Base64 encoded string.
        # This way we can use it for indexing and calculations
        cursor: Cursor | None = None,
        identifiers: list[str] | None = None,
    ) -> Paged[Health]:
        healthchecks = set(health_map.keys())
        if identifiers is not None:
            healthchecks = healthchecks.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"identifier": identifier}

        healths = list(map(construct, healthchecks))

        healths = healths[cursor:][:limit]

        end_cursor: int = (cursor or 0) + len(healths)

        parsed_healths = parse_obj_as(list[HealthRead], healths)
        health_objects = list(map(Health.from_pydantic, parsed_healths))
        return Paged(objects=health_objects, page_info=PageInfo(next_cursor=end_cursor))

    # Files
    # -----
    @strawberry.field(
        description="Get a list of all files, optionally by filename(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )
    async def files(
        self, info: Info, file_store: FileStore, file_names: list[str] | None = None
    ) -> list[File]:
        filestorage = info.context["filestorage"]
        found_files = filestorage.list_files(file_store)
        if file_names is not None:
            found_files = found_files.intersection(set(file_names))

        def construct(file_name: str) -> dict[str, Any]:
            return {"file_store": file_store, "file_name": file_name}

        files = list(map(construct, found_files))
        parsed_files = parse_obj_as(list[FileRead], files)
        return list(map(File.from_pydantic, parsed_files))

    # Configuration
    # -------------
    @strawberry.field(
        description="Get a list of configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )
    async def configuration(
        self, identifiers: list[str] | None = None
    ) -> list[Configuration]:
        settings_keys = get_public_settings()
        if identifiers is not None:
            settings_keys = settings_keys.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"key": identifier}

        settings = list(map(construct, settings_keys))
        parsed_settings = parse_obj_as(list[ConfigurationRead], settings)
        return cast(list[Configuration], parsed_settings)


# ------------------------------


async def _get_obj_effects(
    c: lora.Connector,
    object_tuples: Iterable[tuple[str, dict[Any, Any]]],
    flat: bool = False,
) -> list[dict[Any, Any]]:
    return [
        x
        for sublist in await gather(
            *[
                create_task(
                    _async_get_mo_object_from_effect(c, function_id, function_obj, flat)
                )
                for function_id, function_obj in object_tuples
            ]
        )
        for x in sublist
    ]


async def _async_get_mo_object_from_effect(
    c, function_id, function_obj, flat: bool = False
) -> list[Any]:
    return await gather(
        *[
            create_task(
                _get_mo_object_from_effect(effect, start, end, function_id, flat)
            )
            for start, end, effect in (await _get_effects(c, function_obj))
            if util.is_reg_valid(effect)
        ]
    )


async def _get_effects(c, obj, **params):
    relevant = {
        "attributter": ("organisationenhedegenskaber",),
        "relationer": (
            "enhedstype",
            "opgaver",
            "overordnet",
            "tilhoerer",
            "niveau",
            "opmærkning",
        ),
        "tilstande": ("organisationenhedgyldighed",),
    }
    also = {}

    return await c.organisationenhed.get_effects(obj, relevant, also, **params)


async def _get_mo_object_from_effect(effect, start, end, obj_id, flat: bool = False):
    c = common.get_connector()
    only_primary_uuid = util.get_args_flag("only_primary_uuid")
    details = orgunit.UnitDetails.FULL
    if is_graphql():
        details = orgunit.UnitDetails.MINIMAL

    return await orgunit.get_one_orgunit(
        c,
        obj_id,
        effect,
        details=details,
        validity={
            mapping.FROM: util.to_iso_date(start),
            mapping.TO: util.to_iso_date(end, is_end=True),
        },
        only_primary_uuid=only_primary_uuid,
    )


def group_by_uuid(
    models: list[MOModel], uuids: list[UUID] | None = None
) -> dict[UUID, list[MOModel]]:
    """Auxiliary function to group MOModels by their UUID.

    Args:
        models: List of MOModels to group.
        uuids: List of UUIDs that have been looked up. Defaults to None.

    Returns:
        dict[UUID, list[MOModel]]: A mapping of uuids and lists of corresponding
            MOModels.
    """
    uuids = uuids if uuids is not None else []
    buckets = bucket(models, lambda model: model.uuid)
    # unique keys in order by incoming uuid.
    # mypy doesn't like bucket for some reason
    keys = unique_everseen([*uuids, *list(buckets)])  # type: ignore
    return {key: list(buckets[key]) for key in keys}
