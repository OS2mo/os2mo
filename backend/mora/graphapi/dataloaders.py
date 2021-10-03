# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar

from strawberry.dataloader import DataLoader

from mora.api.v1.reading_endpoints import role_type_search_factory
from mora.api.v1.reading_endpoints import role_type_uuid_factory
from mora.api.v1.reading_endpoints import EMPLOYEE_ROLE_TYPE
from mora.api.v1.reading_endpoints import CommonQueryParams
from mora.service import org

from mora.graphapi.schema import Employee
from mora.graphapi.schema import Organisation


RoleType = TypeVar("RoleType")


def bulk_role_load_factory(
    roletype: str, strawberry_type: RoleType
) -> Callable[[List[UUID]], RoleType]:
    """Generates a bulk loader function for a role-type."""

    async def bulk_load_role(keys: List[UUID]) -> List[Optional[strawberry_type]]:
        """Bulk loader function for a role-type (Organisation Unit or Employee)."""
        result = await role_type_uuid_factory(roletype)(
            uuid=keys,
            common=CommonQueryParams(at=None, validity=None, changed_since=None),
        )
        uuid_map = {obj["uuid"]: strawberry_type.construct(obj) for obj in result}
        return list(map(uuid_map.get, keys))

    return bulk_load_role


def bulk_role_search_factory(
    roletype: str, strawberry_type: RoleType
) -> Callable[[], RoleType]:
    """Generates a searcher function for a role-type."""

    async def bulk_search_role() -> List[strawberry_type]:
        """Searcher function for a role-type (Organisation Unit or Employee)."""
        result = await role_type_search_factory(roletype)(
            common=CommonQueryParams(at=None, validity=None, changed_since=None)
        )
        return list(map(strawberry_type.construct, result))

    return bulk_search_role


# Use our bulk-loader generators to generate loaders for each type
load_employees = bulk_role_load_factory(EMPLOYEE_ROLE_TYPE, Employee)


# Use searcher generators to generate searchers for each type
get_employees = bulk_role_search_factory(EMPLOYEE_ROLE_TYPE, Employee)


async def load_org(keys: List[int]) -> List[Organisation]:
    """Dataloader function to load Organisation.

    A dataloader is used even though only a single Organisation can ever exist, as the
    dataloader also implements caching, and as there may be more than one reference to
    the organisation within one query.
    """
    # We fake the ID of our Organisation as 0 and expect nothing else as inputs
    keyset = set(keys)
    if keyset != {0}:
        raise ValueError("Only one organisation can exist!")

    obj = await org.get_configured_organisation()
    return [Organisation.construct(obj)] * len(keys)


def get_loaders() -> Dict[str, DataLoader]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        "employee_loader": DataLoader(load_fn=load_employees),
    }
