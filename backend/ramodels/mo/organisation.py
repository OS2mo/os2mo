# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pydantic import Field

from ._shared import MOBase
from ._shared import Validity


class OrganisationRead(MOBase):
    """A MO organisation object."""

    type_: str = Field("organisation", alias="type", description="The object type")
    name: str = Field(description="Name of the organisation.")

    validity: Validity = Field(description="The from-value of the current validity.")
