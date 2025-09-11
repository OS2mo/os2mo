# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import validator


class StrictBaseModel(BaseModel):
    """Pydantic BaseModel with strict(er) defaults."""

    class Config:
        extra = Extra.forbid
        frozen = True
        # TODO: do we want this? grandfathered-in from ramodels
        allow_population_by_field_name = True


class Validity(StrictBaseModel):
    start: datetime = Field(alias="from")
    end: datetime | None = Field(alias="to")


class Address(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str = None  # type: ignore[assignment]

    value: str
    value2: str | None
    address_type: UUID
    person: UUID | None
    org_unit: UUID | None
    ituser: UUID | None
    engagement: UUID | None
    visibility: UUID | None
    validity: Validity

    @validator("user_key", pre=True, always=True)
    def set_user_key(cls, user_key: Any | None, values: dict) -> str:
        # TODO: don't default to useless user-key (grandfathered-in from ramodels)
        if user_key or isinstance(user_key, str):
            return user_key
        return str(values["uuid"])


class Employee(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str = None  # type: ignore[assignment]

    given_name: str | None  # TODO: don't allow none (grandfathered-in from ramodels)
    surname: str | None  # TODO: don't allow none (grandfathered-in from ramodels)
    cpr_number: str | None = Field(regex=r"^\d{10}$")
    seniority: datetime | None  # TODO: ensure this field is read from MO, #64576
    nickname_given_name: str = ""
    nickname_surname: str = ""

    @validator("user_key", pre=True, always=True)
    def set_user_key(cls, user_key: Any | None, values: dict) -> str:
        # TODO: don't default to useless user-key (grandfathered-in from ramodels)
        if user_key or isinstance(user_key, str):
            return user_key
        return str(values["uuid"])


class OrganisationUnit(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str

    name: str
    parent: UUID | None = None
    unit_type: UUID
    validity: Validity


class Engagement(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str

    org_unit: UUID
    person: UUID
    job_function: UUID
    engagement_type: UUID
    primary: UUID | None
    extension_1: str | None
    extension_2: str | None
    extension_3: str | None
    extension_4: str | None
    extension_5: str | None
    extension_6: str | None
    extension_7: str | None
    extension_8: str | None
    extension_9: str | None
    extension_10: str | None
    validity: Validity


class ITUser(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str

    external_id: str | None
    itsystem: UUID
    person: UUID | None
    org_unit: UUID | None
    engagement: UUID | None
    validity: Validity


class ITSystem(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str

    name: str
    validity: Validity


class Class(StrictBaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_key: str

    name: str
    scope: str
    facet: UUID
    it_system: UUID | None

    owner: UUID | None
    parent: UUID | None
    published: str = "Publiceret"

    validity: Validity


# NOTE: This model solely exists to allow us to call sync_JobTitleFromADToMO
# NOTE: This model is scheduled for removal, see #62802
class JobTitleFromADToMO(StrictBaseModel):
    # NOTE: These fields can be removed once removed from the configuration
    uuid: UUID = Field(default_factory=uuid4)  # unused
    user_key: str | None  # unused

    user: UUID | None  # unused
    job_function: UUID | None  # unused

    class Config(StrictBaseModel.Config):
        extra = Extra.allow


MOBase = (
    Address
    | Employee
    | Engagement
    | ITUser
    | JobTitleFromADToMO
    | OrganisationUnit
    | ITSystem
    | Class
)


class Termination(StrictBaseModel):
    mo_class: type[MOBase]
    uuid: UUID
    at: datetime
