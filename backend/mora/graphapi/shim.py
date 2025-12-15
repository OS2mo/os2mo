# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# type: ignore
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""

from datetime import date
from typing import Any
from typing import Optional
from uuid import UUID

from more_itertools import flatten
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from starlette_context import context
from starlette_context import request_cycle_context
from strawberry.types import ExecutionResult

from mora import depends
from mora import util
from mora.auth.keycloak.oidc import noauth
from mora.graphapi.gmodels.mo import ClassRead
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import FacetRead
from mora.graphapi.gmodels.mo import OrganisationRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AddressRead
from mora.graphapi.version import LATEST_VERSION


class MOEmployee(EmployeeRead):
    name: str
    nickname: str
    org: OrganisationRead | None
    validity: Any | None  # not part of the "old" MO response

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        # noop overriding parent method - we need name & nickname
        return values


class UUIDObject(BaseModel):
    # Lots of old service endpoints return {"uuid": UUID} objects.
    uuid: UUID


class ValidityDates(BaseModel):
    """Validity with (imprecise) `date` types."""

    from_date: date | None = Field(alias="from")
    to_date: date | None = Field(alias="to")

    @validator("from_date", pre=True, always=True)
    def parse_from_date(cls, v: Any) -> date | None:
        return v and util.parsedatetime(v).date()

    @validator("to_date", pre=True, always=True)
    def parse_to_date(cls, v: Any) -> date | None:
        return v and util.parsedatetime(v).date()


class MOAddressType(ClassRead):
    org_uuid: Any | None
    facet_uuid: Any | None
    facet: Any | None
    top_level_facet: Any | None


class MOFacetRead(FacetRead):
    org_uuid: UUID | None
    user_key: str | None


class MOClassRead(ClassRead):
    org_uuid: UUID | None
    facet_uuid: UUID | None
    facet: MOFacetRead
    top_level_facet: MOFacetRead
    full_name: str | None


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
                    "user_settings": {"orgunit": {}},
                    "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
                    "validity": {"from": "1960-01-01", "to": None},
                },
                "time_planning": None,
                "user_key": "Borgmesterens Afdeling",
                "user_settings": {"orgunit": {}},
                "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                "validity": {"from": "1960-01-01", "to": None},
            }
        }

    location: str = ""
    parent: Optional["MOOrgUnit"]
    org: OrganisationRead | None
    org_unit_level: MOClassRead | None
    org_unit_type: MOClassRead
    time_planning: MOClassRead | None
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
    org_uuid: UUID | None
    facet_uuid: UUID | None


class MOAddress(AddressRead):
    address_type_uuid: UUID | None
    address_type: None | MOAddressType | UUIDObject
    person: None | list[MOEmployee] | UUIDObject
    engagement_uuid: UUID | None
    org_unit: None | OrgUnitType | UUIDObject
    visibility: VisibilityRead | None
    validity: ValidityDates
    href: str | None
    name: str | None


async def set_graphql_context_dependencies(
    amqp_system: depends.AMQPSystem, session: depends.Session
):
    """Fetch FastAPI dependencies into starlette context.

    Strawberry allows FastAPI dependency injection on the router's context_getter, i.e.
    the GraphQL version's get_context() method. execute_graphql(), however, can be
    called from anywhere, and therefore has to initialise its own context. We define
    this starlette_context middleware, which support dependency injection, to inject
    them into the context. execute_graphql() can then fetch them from the context
    later, allowing for indirect dependency injection from a non-FastAPI context.
    """
    data = {
        **context,
        "amqp_system": amqp_system,
        "session": session,
    }
    with request_cycle_context(data):
        yield


async def execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
    # Imports must be done here to avoid circular imports... eww
    from mora.graphapi.router import get_context
    from mora.graphapi.schema import get_schema

    if "context_value" not in kwargs:
        # TODO: The token should be passed from the original caller, such that the
        #  service API shims get RBAC equivalent to the GraphQL API for free.
        kwargs["context_value"] = await get_context(
            get_token=noauth,
            amqp_system=context.get("amqp_system"),
            session=context.get("session"),
        )

    schema = get_schema(LATEST_VERSION)
    return await schema.execute(*args, **kwargs)


def flatten_data(resp_dicts: list[dict[str, Any]]) -> list[Any]:
    """Function to flatten response data into just the objects.

    Args:
        resp_dicts: Response dicts to flatten.

    Returns:
        List of response objects.
    """
    return list(flatten([d["objects"] for d in resp_dicts]))
