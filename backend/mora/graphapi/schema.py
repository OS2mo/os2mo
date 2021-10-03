# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from typing import Any
from typing import Dict

import strawberry


class Constructable:
    """Common interface to construct strawberry types from MO types."""

    @classmethod
    def construct(cls, obj: Dict[str, Any]) -> "Constructable":
        """Construct the subclass strawberry type from the MO type object.

        Args:
            obj: The MO type object dictionary.

        Returns:
            The constructed subclass.
        """
        return cls(**obj)


@strawberry.type(
    description=("The root-organisation." "One and only one of these can exist.")
)
class Organisation(Constructable):
    uuid: UUID
    name: str
    user_key: str
