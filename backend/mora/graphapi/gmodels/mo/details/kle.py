# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic.v1 import Field

from .._shared import MOBase
from .._shared import Validity


class KLERead(MOBase):
    """A MO KLERead object.

    An overview of KLE, Kommunernes Landsforenings Emnesystematik, can be found
    http://www.kle-online.dk/emneplan
    """

    type_: str = Field("kle", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the kle object.")

    kle_number_uuid: UUID = Field(description="UUID of the KLE number.")
    kle_aspect_uuids: list[UUID] = Field(description="List of UUIDs of the KLE aspect.")
    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the KLE."
    )
