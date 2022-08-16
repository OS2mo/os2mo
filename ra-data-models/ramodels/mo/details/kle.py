#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .._shared import KLEAspectRef
from .._shared import KLENumberRef
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import Validity
from ._shared import Details

# --------------------------------------------------------------------------------------
# KLE models
# --------------------------------------------------------------------------------------


class KLEBase(MOBase):
    """A MO KLE object.

    An overview of KLE, Kommunernes Landsforenings Emnesystematik, can be found
    http://www.kle-online.dk/emneplan
    """

    type_: str = Field("kle", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the kle object.")


class KLERead(KLEBase):
    """A MO KLERead object."""

    kle_number_uuid: UUID = Field(description="UUID of the KLE number.")
    kle_aspect_uuids: List[UUID] = Field(description="List of UUIDs of the KLE aspect.")
    org_unit_uuid: Optional[UUID] = Field(
        description="UUID of the organisation unit related to the KLE."
    )


class KLEWrite(KLEBase):
    """A MO KLEWrite object."""

    kle_number: KLENumberRef = Field(description="Reference to the KLE number klasse.")
    kle_aspects: List[KLEAspectRef] = Field(
        description="List of references to the KLE aspect klasse."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description="Reference to the organisation unit for the KLE."
    )


class KLEDetail(KLEWrite, Details):
    pass


class KLE(KLEBase):
    """Service API-compatible model with singular `kle_aspect`."""

    kle_number: KLENumberRef = Field(description="Reference to the KLE number klasse.")
    kle_aspect: List[KLEAspectRef] = Field(
        description="List of references to the KLE aspect klasse."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description="Reference to the organisation unit for the KLE."
    )
