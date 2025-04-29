# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""

import asyncio
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Iterable
from datetime import datetime
from functools import partial
from typing import Any
from typing import TypeVar
from uuid import UUID

from more_itertools import bucket
from more_itertools import unique_everseen
from pydantic import parse_obj_as
from strawberry.dataloader import DataLoader
from strawberry.types.unset import UnsetType

from mora.service import org

from ...middleware import with_graphql_dates
from .graphql_utils import LoadKey
from .readers import get_role_type_by_uuid
from .readers import search_role_type
from .resolvers import get_date_interval
from .schema import AddressRead
from .schema import AssociationRead
from .schema import ClassRead
from .schema import EmployeeRead
from .schema import EngagementRead
from .schema import FacetRead
from .schema import ITSystemRead
from .schema import ITUserRead
from .schema import KLERead
from .schema import LeaveRead
from .schema import ManagerRead
from .schema import OrganisationRead
from .schema import OrganisationUnitRead
from .schema import OwnerRead
from .schema import RelatedUnitRead
from .schema import RoleBindingRead

MOModel = TypeVar(
    "MOModel",
    AddressRead,
    AssociationRead,
    ClassRead,
    EmployeeRead,
    EngagementRead,
    FacetRead,
    ITSystemRead,
    ITUserRead,
    KLERead,
    LeaveRead,
    ManagerRead,
    OrganisationUnitRead,
    OwnerRead,
    RoleBindingRead,
    RelatedUnitRead,
)

RoleType = TypeVar("RoleType")


def group_by_uuid(
    models: Iterable[MOModel], uuids: list[UUID] | None = None
) -> dict[UUID, list[MOModel]]:
    """Auxiliary function to group MOModels by their UUID.

    Args:
        models: List of MOModels to group.
        uuids: List of UUIDs that have been looked up. Defaults to None.

    Returns:
        A mapping of uuids and lists of corresponding MOModels.
    """
    uuids = uuids if uuids is not None else []
    buckets = bucket(models, lambda model: model.uuid)
    # unique keys in order by incoming uuid.
    # mypy doesn't like bucket for some reason
    keys = unique_everseen([*uuids, *list(buckets)])  # type: ignore
    return {key: list(buckets[key]) for key in keys}


from opentelemetry import trace
tracer = trace.get_tracer("graphql.dataloaders")


async def get_mo(model: type[MOModel], **kwargs: Any) -> dict[UUID, list[MOModel]]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        model: The MO model to parse into.
        kwargs: Additional query arguments passed to LoRa.

    Returns:
        Mapping from UUID to list of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    with tracer.start_as_current_span("search_role_type"):
        results = await search_role_type(mo_type, **kwargs)
    parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore
    uuid_map = group_by_uuid(parsed_results)
    return uuid_map


async def load_mo(keys: list[LoadKey], model: type[MOModel]) -> list[list[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        keys: UUIDs to load (in the given start/end interval).
        model: The MO model to parse into.

    Returns:
        List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default

    # Wrapper for get_role_type_by_uuid to pass dates using a nice(r) interface
    async def get(
        uuids: list[UUID],
        start: datetime | UnsetType | None,
        end: datetime | UnsetType | None,
    ) -> list[MOModel]:
        dates = get_date_interval(start, end)
        with with_graphql_dates(dates):
            results = await get_role_type_by_uuid(mo_type, uuids)
        parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore[valid-type]
        return parsed_results

    # Group keys by start/end intervals to allowing batching request(s) to LoRa
    interval_buckets = bucket(keys, key=lambda key: (key.start, key.end))
    gets = [
        get([key.uuid for key in interval_buckets[interval]], *interval)
        for interval in interval_buckets
    ]
    results_lists = await asyncio.gather(*gets)

    # Map results back to the original request keys to uphold the dataloader interface
    loaded = defaultdict(list)
    for results, interval in zip(results_lists, interval_buckets):
        for result in results:
            loaded[LoadKey(result.uuid, *interval)].append(result)
    return [loaded[key] for key in keys]


async def load_org(keys: list[int]) -> list[OrganisationRead]:
    """Dataloader function to load Organisation.

    A dataloader is used even though only a single Organisation can ever exist, as the
    dataloader also implements caching, which is useful as there may be more than
    one reference to the organisation within one query.
    """
    # We fake the ID of our Organisation as 0 and expect nothing else as inputs
    keyset = set(keys)
    if keyset != {0}:  # pragma: no cover
        raise ValueError("Only one organisation can exist!")

    obj = await org.get_configured_organisation()
    return [OrganisationRead.parse_obj(obj)] * len(keys)


async def get_loaders() -> dict[str, DataLoader | Callable]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        # Organisation Unit
        "org_unit_loader": DataLoader(
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "org_unit_getter": partial(get_mo, model=OrganisationUnitRead),
        # Person
        "employee_loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
        "employee_getter": partial(get_mo, model=EmployeeRead),
        # Engagement
        "engagement_loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
        "engagement_getter": partial(get_mo, model=EngagementRead),
        # KLE
        "kle_loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
        "kle_getter": partial(get_mo, model=KLERead),
        # Address
        "address_loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
        "address_getter": partial(get_mo, model=AddressRead),
        # Leave
        "leave_loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
        "leave_getter": partial(get_mo, model=LeaveRead),
        # Association
        "association_loader": DataLoader(
            load_fn=partial(load_mo, model=AssociationRead)
        ),
        "association_getter": partial(get_mo, model=AssociationRead),
        # Rolebinding
        "rolebinding_loader": DataLoader(
            load_fn=partial(load_mo, model=RoleBindingRead)
        ),
        "rolebinding_getter": partial(get_mo, model=RoleBindingRead),
        # ITUser
        "ituser_loader": DataLoader(load_fn=partial(load_mo, model=ITUserRead)),
        "ituser_getter": partial(get_mo, model=ITUserRead),
        # Manager
        "manager_loader": DataLoader(load_fn=partial(load_mo, model=ManagerRead)),
        "manager_getter": partial(get_mo, model=ManagerRead),
        # Owner
        "owner_loader": DataLoader(load_fn=partial(load_mo, model=OwnerRead)),
        "owner_getter": partial(get_mo, model=OwnerRead),
        # Class
        "class_loader": DataLoader(load_fn=partial(load_mo, model=ClassRead)),
        "class_getter": partial(get_mo, model=ClassRead),
        # Related Organisation Unit
        "rel_unit_loader": DataLoader(load_fn=partial(load_mo, model=RelatedUnitRead)),
        "rel_unit_getter": partial(get_mo, model=RelatedUnitRead),
        # Facet
        "facet_loader": DataLoader(load_fn=partial(load_mo, model=FacetRead)),
        "facet_getter": partial(get_mo, model=FacetRead),
        # ITSysterm
        "itsystem_loader": DataLoader(load_fn=partial(load_mo, model=ITSystemRead)),
        "itsystem_getter": partial(get_mo, model=ITSystemRead),
    }
