#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
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

    from_date: Optional[datetime.date] = Field(
        alias="from", description="Start date of the validity."
    )

    to_date: Optional[datetime.date] = Field(
        alias="to", description="End date of the validity, if applicable."
    )
