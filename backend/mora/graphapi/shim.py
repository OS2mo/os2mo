# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# type: ignore
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""
from datetime import date
from typing import Any
from typing import Optional
from typing import Type
from uuid import UUID

from more_itertools import flatten
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from strawberry.types import ExecutionResult

from .versions.base import BaseGraphQLVersion
from mora import util
from mora.auth.keycloak.oidc import noauth
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead


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
    address_type: None | MOAddressType | UUIDObject
    person: None | list[MOEmployee] | UUIDObject
    org_unit: None | OrgUnitType | UUIDObject
    visibility: Optional[VisibilityRead]
    validity: ValidityDates
    href: Optional[str]
    name: Optional[str]


async def execute_graphql(
    *args: Any,
    graphql_version: Optional[Type[BaseGraphQLVersion]] = None,
    **kwargs: Any
) -> ExecutionResult:
    # Imports must be done here to avoid circular imports... eww
    if graphql_version is None:
        from .versions.latest.version import LatestGraphQLVersion

        graphql_version = LatestGraphQLVersion

    if "context_value" not in kwargs:
        # TODO: The token should be passed from the original caller, such that the
        #  service API shims get RBAC equivalent to the GraphQL API for free.
        token = await noauth()
        kwargs["context_value"] = await graphql_version.get_context(token=token)

    schema = graphql_version.schema.get()
    return await schema.execute(*args, **kwargs)


def flatten_data(resp_dicts: list[dict[str, Any]]) -> list[Any]:
    """Function to flatten response data into just the objects.

    Args:
        resp_dicts: Response dicts to flatten.

    Returns:
        List of response objects.
    """
    return list(flatten([d["objects"] for d in resp_dicts]))
