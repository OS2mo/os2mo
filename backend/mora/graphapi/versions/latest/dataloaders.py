# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""
from collections.abc import Callable
from collections.abc import Iterable
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
from .schema import RoleRead
from mora.service import org

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
    RoleRead,
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


async def get_loaders() -> dict[Any, dict[str, DataLoader | Callable]]:
    """Get all available dataloaders as a dictionary."""
    return {
        OrganisationRead: {
            "loader": DataLoader(load_fn=load_org),
        },
        OrganisationUnitRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=OrganisationUnitRead)),
            "getter": partial(get_mo, model=OrganisationUnitRead),
        },
        EmployeeRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
            "getter": partial(get_mo, model=EmployeeRead),
        },
        EngagementRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
            "getter": partial(get_mo, model=EngagementRead),
        },
        KLERead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
            "getter": partial(get_mo, model=KLERead),
        },
        AddressRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
            "getter": partial(get_mo, model=AddressRead),
        },
        LeaveRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
            "getter": partial(get_mo, model=LeaveRead),
        },
        AssociationRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=AssociationRead)),
            "getter": partial(get_mo, model=AssociationRead),
        },
        RoleRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=RoleRead)),
            "getter": partial(get_mo, model=RoleRead),
        },
        ITUserRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=ITUserRead)),
            "getter": partial(get_mo, model=ITUserRead),
        },
        ManagerRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=ManagerRead)),
            "getter": partial(get_mo, model=ManagerRead),
        },
        OwnerRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=OwnerRead)),
            "getter": partial(get_mo, model=OwnerRead),
        },
        ClassRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=ClassRead)),
            "getter": partial(get_mo, model=ClassRead),
        },
        RelatedUnitRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=RelatedUnitRead)),
            "getter": partial(get_mo, model=RelatedUnitRead),
        },
        FacetRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=FacetRead)),
            "getter": partial(get_mo, model=FacetRead),
        },
        ITSystemRead: {
            "loader": DataLoader(load_fn=partial(load_mo, model=ITSystemRead)),
            "getter": partial(get_mo, model=ITSystemRead),
        },
    }
