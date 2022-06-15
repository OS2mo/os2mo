#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# type: ignore
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional
from typing import Union
from uuid import UUID

from more_itertools import flatten
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from ramodels.base import tz_isodate
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo._shared import EngagementType
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import LeaveRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import validate_cpr
from ramodels.mo._shared import validate_names
from ramodels.mo.details import AddressRead
from ramodels.mo.details._shared import Details as DetailBase
from ramodels.mo.details.address import AddressDetail
from ramodels.mo.details.association import AssociationDetail
from ramodels.mo.details.engagement import EngagementBase
from ramodels.mo.details.it_system import ITUserDetail
from ramodels.mo.details.kle import KLEDetail
from ramodels.mo.details.leave import LeaveDetail
from ramodels.mo.details.manager import ManagerDetail
from ramodels.mo.details.role import RoleDetail
from ramodels.mo.employee import DictStrAny
from ramodels.mo.employee import EmployeeBase
from strawberry.types import ExecutionResult

from mora import util
from mora.api.v1.models import EngagementAssociation

# from ramodels.mo.employee import EmployeeWrite

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class UUIDObject(BaseModel):
    # Lots of old service endpoints return {"uuid": UUID} objects.
    uuid: UUID


class MOEmployee(EmployeeRead):
    name: str
    nickname: str
    org: Optional[OrganisationRead]
    validity: Optional[Any]  # not part of the "old" MO response

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        # noop overriding parent method - we need name & nickname
        return values


class EngagementWrite(EngagementBase):
    """A MO engagement write object."""

    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit "
            "for which the engagement should be created."
        )
    )
    # employee: EmployeeRef = Field(
    #     description=(
    #         "Reference to the employee for which the engagement should be created."
    #     )
    # )
    engagement_type: EngagementType = Field(
        description=(
            "Reference to the engagement type klasse for the created engagement object."
        )
    )
    # NOTE: Job function is set to optional in the current MO write code,
    # but that's an error. If payloads without a job function are posted,
    # MO fails spectacularly when reading the resulting engagement objects.
    job_function: JobFunction = Field(
        description=(
            "Reference to the job function klasse for the created engagement object."
        )
    )
    leave: Optional[LeaveRef] = Field(
        description="Reference to the leave for the created engagement."
    )
    primary: Optional[Primary] = Field(
        description="Reference to the primary klasse for the created engagement object."
    )


class EngagementDetail(EngagementWrite, DetailBase):
    pass


Details = Union[
    AssociationDetail,
    EngagementDetail,
    EngagementAssociation,
    KLEDetail,
    ManagerDetail,
    ITUserDetail,
    RoleDetail,
]

EmployeeDetails = Union[Details, AddressDetail, LeaveDetail]


class EmployeeWrite(EmployeeBase):
    name: Optional[str] = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    nickname: Optional[str] = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )
    details: Optional[list[EmployeeDetails]] = Field(
        description=(
            "Details to be created for the employee. Note that when this is used, the"
            " employee reference is implicit in the payload."
        )
    )

    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname")

    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname"
        )

    _validate_cpr = validator("cpr_no", allow_reuse=True)(validate_cpr)

    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None


class MOEmployeeWrite(EmployeeWrite):
    org: Optional[UUIDObject]

    class Config:
        schema_extra = {
            "example": {
                "name": "Name Name",
                "nickname": "Nickname Whatever",
                "cpr_no": "0101501234",
                "user_key": "1234",
                "org": {"uuid": "67e9a80e-6bc0-e97a-9751-02600c017844"},
                "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f",
                "details": [
                    {
                        "type": "engagement",
                        "org_unit": {"uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"},
                        "job_function": {
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                        },
                        "engagement_type": {
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                        },
                        "validity": {"from": "2016-01-01", "to": "2017-12-31"},
                    }
                ],
            },
        }


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


class MOFacetRead(FacetRead):
    org_uuid: Optional[UUID]
    user_key: Optional[str]


class MOClassRead(ClassRead):
    org_uuid: Optional[UUID]
    facet_uuid: Optional[UUID]
    facet: MOFacetRead
    top_level_facet: MOFacetRead
    full_name: Optional[str]


class OrgUnitType(OrganisationUnitRead):
    validity: ValidityDates


class OrgUnitRead(OrganisationUnitRead):
    validity: ValidityDates


class OrganisationUnitCount(OrgUnitRead):
    child_count: int
    engagement_count: int = 0
    association_count: int = 0


class MOOrgUnit(OrgUnitRead):
    class Config:
        frozen = False
        schema_extra = {
            "example": {
                "location": "Hj\u00f8rring Kommune",
                "name": "Borgmesterens Afdeling",
                "org": {
                    "name": "Hj\u00f8rring Kommune",
                    "user_key": "Hj\u00f8rring Kommune",
                    "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575",
                },
                "org_unit_type": {
                    "example": None,
                    "name": "Afdeling",
                    "scope": "TEXT",
                    "user_key": "Afdeling",
                    "uuid": "c8002c56-8226-4a72-aefa-a01dcc839391",
                },
                "parent": {
                    "location": "",
                    "name": "Hj\u00f8rring Kommune",
                    "org": {
                        "name": "Hj\u00f8rring Kommune",
                        "user_key": "Hj\u00f8rring Kommune",
                        "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575",
                    },
                    "org_unit_type": {
                        "example": None,
                        "name": "Afdeling",
                        "scope": "TEXT",
                        "user_key": "Afdeling",
                        "uuid": "c8002c56-8226-4a72-aefa-a01dcc839391",
                    },
                    "parent": None,
                    "time_planning": None,
                    "user_key": "Hj\u00f8rring Kommune",
                    "user_settings": {
                        "orgunit": {
                            "show_location": True,
                            "show_roles": True,
                            "show_user_key": False,
                        }
                    },
                    "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
                    "validity": {"from": "1960-01-01", "to": None},
                },
                "time_planning": None,
                "user_key": "Borgmesterens Afdeling",
                "user_settings": {
                    "orgunit": {
                        "show_location": True,
                        "show_roles": True,
                        "show_user_key": False,
                    }
                },
                "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                "validity": {"from": "1960-01-01", "to": None},
            }
        }

    location: str = ""
    parent: Optional["MOOrgUnit"]
    org: Optional[OrganisationRead]
    org_unit_level: Optional[MOClassRead]
    org_unit_type: MOClassRead
    time_planning: Optional[MOClassRead]
    user_settings: dict[str, Any] = {}
    engagement_count: int = 0
    association_count: int = 0


class OrganisationLevelRead(OrganisationRead):
    child_count: int
    person_count: int
    unit_count: int
    engagement_count: int
    association_count: int
    leave_count: int
    role_count: int
    manager_count: int


class VisibilityRead(ClassRead):
    org_uuid: Optional[UUID]
    facet_uuid: Optional[UUID]


class MOAddress(AddressRead):
    address_type_uuid: Optional[UUID]
    address_type: Union[None, MOAddressType, UUIDObject]
    person: Union[None, list[MOEmployee], UUIDObject]
    org_unit: Union[None, OrgUnitType, UUIDObject]
    visibility: Optional[VisibilityRead]
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
