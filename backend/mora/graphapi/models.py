#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
import typing
from enum import Enum
from typing import Optional
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Field


# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------


@strawberry.enum
class FileStore(Enum):
    EXPORTS = 1
    INSIGHTS = 2


class HealthRead(BaseModel):
    """Payload model for health."""

    identifier: str = Field(description="Short, unique key.")


class FileRead(BaseModel):
    """Payload model for file download."""

    file_store: FileStore = Field(description="The file store the file is stored in.")
    file_name: str = Field(description="Name of the export file.")


class OrganisationUnitRefreshRead(BaseModel):
    """Payload model for organisation unit refresh mutation."""

    message: str = Field(description="Refresh message containing trigger responses.")


class ConfigurationRead(BaseModel):
    """Payload model for configuration."""

    key: str = Field(description="Settings key.")


class OrganisationUnit(BaseModel):
    """Model representing a Organization-Unit."""

    uuid: UUID = Field(description="Unique ID identifying the organization unit")


class OrganisationUnitTerminate(OrganisationUnit):
    """Model representing a organization-unit termination."""

    from_date: Optional[datetime.datetime] = Field(
        alias="from", description="Start date of the validity."
    )

    to_date: Optional[datetime.datetime] = Field(
        alias="to", description="End date of the validity, if applicable."
    )

    trigger_less: Optional[bool] = Field(
        alias="triggerless",
        description="Flag specifying if triggers should not be invoked, if true.",
        default=False,
    )


class Validity(BaseModel):
    """Model representing an entities validity range."""

    from_date: Optional[datetime.datetime] = Field(
        alias="from", description="Start date of the validity."
    )

    to_date: Optional[datetime.datetime] = Field(
        alias="to", description="End date of the validity, if applicable."
    )

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class MoraTriggerRequest(BaseModel):
    """Model representing a MoRa Trigger Request."""

    type: str = Field(description="Type of the request, ex. 'org_unit'.")

    uuid: UUID = Field(
        description="UUID for the entity accessed in the request. "
        "Ex type=ORG_UNIT, then this UUID will be the UUID of the ORG_UNIT"
    )

    validity: Validity = Field(description="Type of the request, ex. 'org_unit'.")


class MoraTrigger(BaseModel):
    """Model representing a MoRa Trigger."""

    request_type: str = Field(
        description="Request type to do, ex CREATE, EDIT, TERMINATE or REFRESH. "
        "Ref: mora.mapping.RequestType"
    )

    request: MoraTriggerRequest = Field(description="The Request for the trigger.")

    role_type: str = Field(description="Role type for the trigger, ex 'org_unit'.")

    event_type: str = Field(
        description="Trigger event-type. " "Ref: mora.mapping.EventType"
    )

    uuid: UUID = Field(
        description="UUID of the entity being handled in the trigger. "
        "Ex. type=ORG_UNIT, this this is the org-unit-uuid."
    )

    result: typing.Any = Field(description="Result of the trigger", default=None)

    # org_unit_uuid: str


class MoraTriggerOrgUnit(MoraTrigger):
    """Model representing a mora-trigger, specific for organization-units."""

    org_unit_uuid: UUID = Field(
        description="UUID for the organization unit in question."
    )
