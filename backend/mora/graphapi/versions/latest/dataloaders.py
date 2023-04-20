# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import TypeVar
from uuid import UUID

from more_itertools import bucket
from more_itertools import unique_everseen
from pydantic import parse_obj_as
from strawberry.dataloader import DataLoader

from .readers import get_role_type_by_uuid
from .readers import search_role_type
from .schema import AddressRead
from .schema import AssociationRead
from .schema import ClassRead
from .schema import EmployeeRead
from .schema import EngagementAssociationRead
from .schema import EngagementRead
from .schema import FacetRead
from .schema import ITSystemRead
from .schema import ITUserRead
from .schema import KLERead
from .schema import LeaveRead
from .schema import ManagerRead
from .schema import OrganisationRead
from .schema import OrganisationUnitRead
from .schema import RelatedUnitRead
from .schema import RoleRead
from mora.service import org

MOModel = TypeVar(
    "MOModel",
    AddressRead,
    AssociationRead,
    EmployeeRead,
    EngagementRead,
    EngagementAssociationRead,
    ITUserRead,
    KLERead,
    LeaveRead,
    ManagerRead,
    OrganisationUnitRead,
    RoleRead,
    RelatedUnitRead,
    FacetRead,
    ClassRead,
    ITSystemRead,
)

RoleType = TypeVar("RoleType")


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


async def get_mo(model: MOModel, **kwargs: Any) -> dict[UUID, list[MOModel]]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        model: The MO model to parse into.
        kwargs: Additional query arguments passed to LoRa.

    Returns:
        Mapping from UUID to list of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await search_role_type(mo_type, **kwargs)
    parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore
    uuid_map = group_by_uuid(parsed_results)
    return uuid_map


async def load_mo(uuids: list[UUID], model: MOModel) -> list[list[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids: UUIDs to load.
        model: The MO model to parse into.

    Returns:
        List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await get_role_type_by_uuid(mo_type, uuids)
    parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore
    uuid_map = group_by_uuid(parsed_results, uuids)
    return list(map(uuid_map.get, uuids))  # type: ignore


# get all models
get_org_units = partial(get_mo, model=OrganisationUnitRead)
get_employees = partial(get_mo, model=EmployeeRead)
get_engagements = partial(get_mo, model=EngagementRead)
get_engagement_associations = partial(get_mo, model=EngagementAssociationRead)
get_kles = partial(get_mo, model=KLERead)
get_addresses = partial(get_mo, model=AddressRead)
get_leaves = partial(get_mo, model=LeaveRead)
get_associations = partial(get_mo, model=AssociationRead)
get_roles = partial(get_mo, model=RoleRead)
get_itusers = partial(get_mo, model=ITUserRead)
get_managers = partial(get_mo, model=ManagerRead)
get_related_units = partial(get_mo, model=RelatedUnitRead)
get_itsystems = partial(get_mo, model=ITSystemRead)
get_classes = partial(get_mo, model=ClassRead)
get_facets = partial(get_mo, model=FacetRead)


async def load_org(keys: list[int]) -> list[OrganisationRead]:
    """Dataloader function to load Organisation.

    A dataloader is used even though only a single Organisation can ever exist, as the
    dataloader also implements caching, which is useful as there may be more than
    one reference to the organisation within one query.
    """
    # We fake the ID of our Organisation as 0 and expect nothing else as inputs
    keyset = set(keys)
    if keyset != {0}:
        raise ValueError("Only one organisation can exist!")

    obj = await org.get_configured_organisation()
    return [OrganisationRead.parse_obj(obj)] * len(keys)


async def get_loaders() -> dict[str, DataLoader | Callable]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        "org_unit_loader": DataLoader(
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "org_unit_getter": get_org_units,
        "employee_loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
        "employee_getter": get_employees,
        "engagement_loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
        "engagement_getter": get_engagements,
        "kle_loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
        "kle_getter": get_kles,
        "address_loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
        "address_getter": get_addresses,
        "leave_loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
        "leave_getter": get_leaves,
        "association_loader": DataLoader(
            load_fn=partial(load_mo, model=AssociationRead)
        ),
        "association_getter": get_associations,
        "role_loader": DataLoader(load_fn=partial(load_mo, model=RoleRead)),
        "role_getter": get_roles,
        "ituser_loader": DataLoader(load_fn=partial(load_mo, model=ITUserRead)),
        "ituser_getter": get_itusers,
        "manager_loader": DataLoader(load_fn=partial(load_mo, model=ManagerRead)),
        "manager_getter": get_managers,
        "class_loader": DataLoader(load_fn=partial(load_mo, model=ClassRead)),
        "class_getter": get_classes,
        "rel_unit_loader": DataLoader(load_fn=partial(load_mo, model=RelatedUnitRead)),
        "rel_unit_getter": get_related_units,
        "facet_loader": DataLoader(load_fn=partial(load_mo, model=FacetRead)),
        "facet_getter": get_facets,
        "itsystem_loader": DataLoader(load_fn=partial(load_mo, ITSystemRead)),
        "itsystem_getter": get_itsystems,
        "engagement_association_loader": DataLoader(
            load_fn=partial(load_mo, model=EngagementAssociationRead)
        ),
        "engagement_association_getter": get_engagement_associations,
    }
