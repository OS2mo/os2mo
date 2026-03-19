# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import Validity


class RelatedUnitRead(MOBase):
    """A MO RelatedUnitRead object."""

    type_: str = Field("related_unit", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the relatedUnit object.")

    org_unit_uuid: UUID = Field(
        description="UUID of the first/origin organisation unit."
    )
    related_org_unit_uuid: UUID = Field(
        description="UUID of the second/destination organisation unit."
    )
    org_unit_uuids: list[UUID] = Field(
        description="UUIDs of the related organisation units.",
        deprecated="Use 'org_unit_uuid' and 'related_org_unit_uuid' instead.",
    )
