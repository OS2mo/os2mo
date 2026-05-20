# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""

import asyncio
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from functools import partial
from typing import TypeVar
from uuid import UUID

from more_itertools import bucket
from pydantic import parse_obj_as
from strawberry.dataloader import DataLoader
from strawberry.types.unset import UnsetType

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import OwnerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead
from mora.graphapi.middleware import with_graphql_dates
from mora.service import org

from .graphql_utils import LoadKey
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .momodel import MOModel
from .readers import get_role_type_by_uuid
from .resolvers import get_date_interval

RoleType = TypeVar("RoleType")


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
        registration_time: datetime | None,
    ) -> list[MOModel]:
        dates = get_date_interval(start, end)
        with with_graphql_dates(dates):
            results = await get_role_type_by_uuid(mo_type, uuids, registration_time)
        parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore[valid-type]
        return parsed_results

    # Group keys by start/end intervals to allowing batching request(s) to LoRa
    interval_buckets = bucket(
        keys, key=lambda key: (key.start, key.end, key.registration_time)
    )
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
        "org_loader": DataLoader[int, OrganisationRead](load_fn=load_org),
        "org_unit_loader": DataLoader[LoadKey, list[OrganisationUnitRead]](
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "employee_loader": DataLoader[LoadKey, list[EmployeeRead]](
            load_fn=partial(load_mo, model=EmployeeRead)
        ),
        "engagement_loader": DataLoader[LoadKey, list[EngagementRead]](
            load_fn=partial(load_mo, model=EngagementRead)
        ),
        "kle_loader": DataLoader[LoadKey, list[KLERead]](
            load_fn=partial(load_mo, model=KLERead)
        ),
        "address_loader": DataLoader[LoadKey, list[AddressRead]](
            load_fn=partial(load_mo, model=AddressRead)
        ),
        "leave_loader": DataLoader[LoadKey, list[LeaveRead]](
            load_fn=partial(load_mo, model=LeaveRead)
        ),
        "association_loader": DataLoader[LoadKey, list[AssociationRead]](
            load_fn=partial(load_mo, model=AssociationRead)
        ),
        "rolebinding_loader": DataLoader[LoadKey, list[RoleBindingRead]](
            load_fn=partial(load_mo, model=RoleBindingRead)
        ),
        "ituser_loader": DataLoader[LoadKey, list[ITUserRead]](
            load_fn=partial(load_mo, model=ITUserRead)
        ),
        "manager_loader": DataLoader[LoadKey, list[ManagerRead]](
            load_fn=partial(load_mo, model=ManagerRead)
        ),
        "owner_loader": DataLoader[LoadKey, list[OwnerRead]](
            load_fn=partial(load_mo, model=OwnerRead)
        ),
        "class_loader": DataLoader[LoadKey, list[ClassRead]](
            load_fn=partial(load_mo, model=ClassRead)
        ),
        "rel_unit_loader": DataLoader[LoadKey, list[RelatedUnitRead]](
            load_fn=partial(load_mo, model=RelatedUnitRead)
        ),
        "facet_loader": DataLoader[LoadKey, list[FacetRead]](
            load_fn=partial(load_mo, model=FacetRead)
        ),
        "itsystem_loader": DataLoader[LoadKey, list[ITSystemRead]](
            load_fn=partial(load_mo, model=ITSystemRead)
        ),
    }
