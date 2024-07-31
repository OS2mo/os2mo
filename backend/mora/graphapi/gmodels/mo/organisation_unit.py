# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic.v1 import Field

from ._shared import MOBase
from ._shared import Validity


class OrganisationUnitRead(MOBase):
    """A MO organisation unit object."""

    type_: str = Field("org_unit", alias="type", description="The object type.")
    name: str = Field(description="Name of the created organisation unit.")
    validity: Validity = Field(description="Validity of the created organisation unit.")

    parent_uuid: UUID | None = Field(
        description="UUID of the parent organisation unit."
    )
    org_unit_hierarchy: UUID | None = Field(
        description="UUID of the organisation unit hierarchy."
    )
    unit_type_uuid: UUID | None = Field(
        description="UUID of the organisation unit type."
    )
    org_unit_level_uuid: UUID | None = Field(
        description="UUID of the organisation unit level."
    )
    time_planning_uuid: UUID | None = Field(
        description="UUID of the time planning object."
    )
