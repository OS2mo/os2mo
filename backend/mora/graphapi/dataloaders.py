# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from functools import partial
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar
from uuid import UUID

from pydantic import parse_obj_as
from strawberry.dataloader import DataLoader

from mora.common import get_connector
from mora.graphapi.readers import _extract_search_params
from mora.graphapi.readers import get_role_type_by_uuid
from mora.graphapi.readers import search_role_type
from mora.graphapi.schema import AddressRead
from mora.graphapi.schema import EmployeeRead
from mora.graphapi.schema import EngagementRead
from mora.graphapi.schema import LeaveRead
from mora.graphapi.schema import KLERead
from mora.graphapi.schema import OrganisationRead
from mora.graphapi.schema import OrganisationUnitRead
from mora.handler.impl.org_unit import ROLE_TYPE as ORG_UNIT_ROLE_TYPE
from mora.handler.reading import get_handler_for_type
from mora.service import org

MOModel = TypeVar(
    "MOModel",
    OrganisationUnitRead,
    EmployeeRead,
    EngagementRead,
    KLERead,
    AddressRead,
    LeaveRead,
)

RoleType = TypeVar("RoleType")


async def get_mo(model: MOModel) -> List[MOModel]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        model (MOModel): The MO model to parse into.

    Returns:
        List[MOModel]: List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await search_role_type(mo_type)

    return parse_obj_as(List[model], results)  # type: ignore


async def load_mo(uuids: List[UUID], model: MOModel) -> List[Optional[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids (List[UUID]): UUIDs to load.
        model (MOModel): The MO model to parse into.

    Returns:
        List[Optional[MOModel]]: List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await get_role_type_by_uuid(mo_type, uuids)
    parsed_results = parse_obj_as(List[model], results)  # type: ignore
    uuid_map = {model.uuid: model for model in parsed_results}  # type: ignore
    return list(map(uuid_map.get, uuids))


# get all models
get_org_units = partial(get_mo, model=OrganisationUnitRead)
get_employees = partial(get_mo, model=EmployeeRead)
get_engagements = partial(get_mo, model=EngagementRead)
get_kles = partial(get_mo, model=KLERead)
get_addresses = partial(get_mo, model=AddressRead)
get_leaves = partial(get_mo, model=LeaveRead)


async def load_org(keys: List[int]) -> List[OrganisationRead]:
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


async def get_org_unit_children(parent_uuid: UUID) -> List[MOModel]:
    """Non-bulk loader for organisation unit children."""
    c = get_connector()
    cls = get_handler_for_type(ORG_UNIT_ROLE_TYPE)
    result = await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={
                "at": None,
                "validity": None,
                "overordnet": str(parent_uuid),
                "gyldighed": "Aktiv",
            }
        ),
        changed_since=None,
    )
    return parse_obj_as(List[MOModel], result)


async def load_org_units_children(keys: List[UUID]) -> List[List[MOModel]]:
    """Non-bulk loader for organisation unit children with bulk interface."""
    # TODO: This function should be replaced with a bulk version
    tasks = map(get_org_unit_children, keys)
    return await gather(*tasks)


async def get_loaders() -> Dict[str, DataLoader]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        "org_unit_loader": DataLoader(
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "org_unit_children_loader": DataLoader(load_fn=load_org_units_children),
        "employee_loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
        "engagement_loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
        "kle_loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
        "address_loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
        "leave_loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
    }
