# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any

import strawberry
from pydantic import Extra
from pydantic import Field

from ramodels.mo._shared import UUIDBase


class ITSystemCreate(UUIDBase):
    """Model representing an itsystem creation."""

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    user_key: str
    name: str
    from_date: datetime | None = Field(
        None, alias="from", description="Start date of the validity."
    )
    to_date: datetime | None = Field(
        None, alias="to", description="End date of the validity, if applicable."
    )

    def to_latest_dict(self) -> dict[str, Any]:
        return {
            "user_key": self.user_key,
            "name": self.name,
            "validity": {
                "from": self.from_date,
                "to": self.to_date,
            },
        }


@strawberry.experimental.pydantic.input(
    model=ITSystemCreate,
    all_fields=True,
)
class ITSystemCreateInput:
    """input model for creating ITSystems."""
