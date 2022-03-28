#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from typing import Any, Optional, Union
from uuid import UUID

from more_itertools import flatten
from pydantic import BaseModel, Field, validator, root_validator
from strawberry.types import ExecutionResult

from mora import util
from ramodels.mo import ClassRead, OrganisationUnitRead
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationRead
from ramodels.mo.details import AddressRead

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class MOEmployee(EmployeeRead):
    name: str
    nickname: str
    org: Optional[OrganisationRead]
    validity: Optional[Any]  # not part of the "old" MO response

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        # noop overriding parent method - we need name & nickname
        return values


class UUIDObject(BaseModel):
    # Lots of old service endpoints return {"uuid": UUID} objects.
    uuid: UUID


class ValidityDates(BaseModel):
    """Validity with (imprecise) `date` types."""

    from_date: Optional[date] = Field(alias="from")
    to_date: Optional[date] = Field(alias="to")

    @validator("from_date", pre=True, always=True)
    def parse_from_date(cls, v: Any) -> Optional[date]:
        return v and util.parsedatetime(v).date()

    @validator("to_date", pre=True, always=True)
    def parse_to_date(cls, v: Any) -> Optional[date]:
        return v and util.parsedatetime(v).date()


class MOAddressType(ClassRead):
    org_uuid: Optional[Any]
    facet_uuid: Optional[Any]
    facet: Optional[Any]
    top_level_facet: Optional[Any]


class OrgUnitType(OrganisationUnitRead):
    validity: ValidityDates


class MOAddress(AddressRead):
    address_type_uuid: Optional[UUID]
    address_type: Union[None, MOAddressType, UUIDObject]
    person: Union[None, list[MOEmployee], UUIDObject]
    org_unit: Union[None, OrgUnitType, UUIDObject]
    validity: ValidityDates
    href: Optional[str]
    name: Optional[str]


async def execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
    from mora.graphapi.main import get_schema
    from mora.graphapi.dataloaders import get_loaders
    from mora.graphapi.middleware import set_is_shim

    set_is_shim()

    loaders = await get_loaders()
    if "context_value" not in kwargs:
        kwargs["context_value"] = loaders

    return await get_schema().execute(*args, **kwargs)


def flatten_data(resp_dicts: list[dict[str, Any]]) -> list[Any]:
    """Function to flatten response data into just the objects.

    Args:
        resp_dicts: Response dicts to flatten.

    Returns:
        List of response objects.
    """
    return list(flatten([d["objects"] for d in resp_dicts]))
