# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import Validity


class RelatedUnitBase(MOBase):
    """A MO relatedUnit object."""

    type_: str = Field("related_unit", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the relatedUnit object.")


class RelatedUnitRead(RelatedUnitBase):
    """A MO RelatedUnitRead object."""

    org_unit_uuids: list[UUID] = Field(
        description="UUIDs of the related organisation units."
    )


class RelatedUnitWrite(RelatedUnitBase):
    """A MO RelatedUnitWrite object."""

    org_units: list[OrgUnitRef] = Field(
        description="List of references of the related the organisation units."
    )
