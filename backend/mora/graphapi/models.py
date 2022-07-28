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

import strawberry
from pydantic import BaseModel
from pydantic import Field

from backend.ramodels.mo.class_ import ClassBase

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


class ClassTerminate(ClassBase):
    """Model representing a mo-class termination."""

    from_date: Optional[datetime.date] = Field(
        alias="from", description="Start date of the validity."
    )

    to_date: Optional[datetime.date] = Field(
        alias="to", description="End date of the validity, if applicable."
    )


@strawberry.experimental.pydantic.input(model=ClassTerminate, all_fields=True)
class ClassDelete:
    """Pydantic -> Strawberry model for mo-class mutator"""

    uuid: strawberry.auto
    type_: strawberry.auto
    facet_uuid: strawberry.auto
    org_uuid: strawberry.auto
    scope: strawberry.auto
    published: strawberry.auto
    parent_uuid: strawberry.auto
    example: strawberry.auto
    owner: strawberry.auto
    name: strawberry.auto
    user_key: strawberry.auto
    