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
from ramodels.mo._shared import MOBase

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


class ITSystemBase(MOBase):
    """A MO IT-system base object."""

    type_: str = Field("itsystem", alias="type", description="The object type")
    state: str = Field(description="The state of the IT-system")


class ITSystemWrite(ITSystemBase):
    """A MO IT-system write object."""

    name: str = Field(description="Name/title of the IT-system.", min_length=1)
    user_key: str = Field(description="Short, unique key.")
    system_type: Optional[str] = Field(description="The ITSystem type.")
