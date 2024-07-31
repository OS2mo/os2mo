# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pydantic import Field

from ._shared import MOBase


class OrganisationRead(MOBase):
    """A MO organisation object."""

    type_: str = Field("organisation", alias="type", description="The object type")
    name: str = Field(description="Name of the organisation.")
