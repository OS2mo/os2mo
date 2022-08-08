#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from enum import Enum
from typing import Optional

import strawberry
from pydantic import BaseModel
from pydantic import Field
from ramodels.mo import OpenValidity
from ramodels.mo._shared import UUIDBase

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


class Employee(UUIDBase):
    """Model representing a employee."""

    pass


class EmployeeTermination(Employee, OpenValidity):
    """Model representing a EmployeeTermination termination."""

    triggerless: Optional[bool] = Field(
        description="Flag specifying if triggers should not be invoked, if true.",
        default=False,
    )
