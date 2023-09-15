# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from ramodels.mo._shared import UUIDBase


class ITSystemCreate(UUIDBase):
    """Model representing an itsystem creation."""

    user_key: str
    name: str


@strawberry.experimental.pydantic.input(
    model=ITSystemCreate,
    all_fields=True,
)
class ITSystemCreateInput:
    """input model for creating ITSystems."""
