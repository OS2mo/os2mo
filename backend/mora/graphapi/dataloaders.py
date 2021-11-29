# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from functools import partial
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar
from uuid import UUID

from pydantic import parse_obj_as
from ramodels.mo import EmployeeRead
from strawberry.dataloader import DataLoader

from mora.common import get_connector
from mora.graphapi.readers import _extract_search_params
from mora.graphapi.readers import CommonQueryParams
from mora.graphapi.readers import get_role_type_by_uuid
from mora.graphapi.readers import role_type_uuid_factory
from mora.graphapi.readers import search_role_type
from mora.graphapi.schema import Employee
from mora.graphapi.schema import Organisation
from mora.graphapi.schema import OrganisationUnitRead
from mora.handler.impl.employee import ROLE_TYPE as EMPLOYEE_ROLE_TYPE
from mora.handler.impl.org_unit import ROLE_TYPE as ORG_UNIT_ROLE_TYPE
from mora.handler.reading import get_handler_for_type
from mora.service import org

MOModel = TypeVar("MOModel", OrganisationUnitRead, EmployeeRead)

RoleType = TypeVar("RoleType")


def bulk_role_load_factory(
    roletype: str, strawberry_type: RoleType
) -> Callable[[List[UUID]], List[Optional[RoleType]]]:
    """Generates a bulk loader function for a role-type."""

    async def bulk_load_role(keys: List[UUID]) -> List[Optional[RoleType]]:
        """Bulk loader function for a role-type (Organisation Unit or Employee)."""
        factory = role_type_uuid_factory(roletype)
        result = await factory(
            uuid=list(map(str, keys)),
            common=CommonQueryParams(at=None, validity=None, changed_since=None),
        )
        uuid_map = {UUID(obj["uuid"]): strawberry_type.construct(obj) for obj in result}
        return list(map(uuid_map.get, keys))

    return bulk_load_role


def bulk_role_search_factory(
    roletype: str, strawberry_type: RoleType
) -> Callable[[], List[RoleType]]:
    """Generates a searcher function for a role-type."""

    async def bulk_search_role() -> List[RoleType]:
        """Searcher function for a role-type (Organisation Unit or Employee)."""
        result = await search_role_type(roletype)
        return list(map(strawberry_type.construct, result))

    return bulk_search_role


async def get_mo(mo_type: str) -> List[MOModel]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        mo_type (str): The MO role type used in LoRa search.

    Returns:
        List[MOModel]: List of parsed MO models.
    """
    results = await search_role_type(mo_type)
    return parse_obj_as(List[MOModel], results)


async def load_mo(uuids: List[UUID], mo_type: str) -> List[Optional[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids (List[UUID]): UUIDs to load.
        mo_type (str): The MO role type used in LoRa search.

    Returns:
        List[Optional[MOModel]]: List of parsed MO models.
    """
    results = await get_role_type_by_uuid(mo_type, uuids)
    parsed_results = parse_obj_as(List[MOModel], results)
    uuid_map = {model.uuid: model for model in parsed_results}
    return list(map(uuid_map.get, uuids))


# Use our bulk-loader generators to generate loaders for each type
load_employees = bulk_role_load_factory(EMPLOYEE_ROLE_TYPE, Employee)


# Use searcher generators to generate searchers for each type
get_employees = bulk_role_search_factory(EMPLOYEE_ROLE_TYPE, Employee)


async def load_org(keys: List[int]) -> List[Organisation]:
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
    return [Organisation.construct(obj)] * len(keys)


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
        "org_unit_loader": DataLoader(load_fn=partial(load_mo, mo_type="org_unit")),
        "org_unit_children_loader": DataLoader(load_fn=load_org_units_children),
        "employee_loader": DataLoader(load_fn=load_employees),
    }
