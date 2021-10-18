# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import strawberry
from strawberry.types import Info

from mora.api.v1.models import Validity


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


@strawberry.experimental.pydantic.type(
    model=Validity, fields=Validity.__fields__.keys()
)
class QLValidity:
    # XXX: There is currently something very broken with using Validities like this
    pass


@strawberry.type(
    description=("The root-organisation." "One and only one of these can exist.")
)
class Organisation(Constructable):
    uuid: UUID
    name: str
    user_key: str


@strawberry.type(
    description=("An Employee; containing personal information about an identity.")
)
class Employee(Constructable):
    uuid: UUID
    cpr_no: Optional[str]

    user_key: str

    givenname: str
    surname: str

    nickname_givenname: Optional[str]
    nickname_surname: Optional[str]

    seniority: Optional[str]
    validity: QLValidity

    @classmethod
    def construct(cls, obj: Dict[str, Any]) -> "Constructable":
        """Construct the employee strawberry type from the MO employee object.

        Args:
            obj: The MO employee dictionary.

        Returns:
            The constructed employee.
        """
        obj.pop("name", None)
        obj.pop("nickname", None)
        return cls(**obj)


@strawberry.type(
    description=(
        "An Organisation Unit; the hierarchical unit creating the organisation tree."
    )
)
class OrganisationUnit(Constructable):
    uuid: UUID
    user_key: str
    name: str

    unit_type_uuid: Optional[UUID]
    time_planning_uuid: Optional[UUID]
    org_unit_level_uuid: Optional[UUID]
    parent_uuid: Optional[UUID]

    validity: QLValidity

    @strawberry.field(description="The parent organisation unit above this unit")
    async def parent(self, info: Info) -> Optional["OrganisationUnit"]:
        if self.parent_uuid:
            if not isinstance(self.parent_uuid, UUID):
                self.parent_uuid = UUID(self.parent_uuid)
            return await info.context["org_unit_loader"].load(self.parent_uuid)
        return None

    @strawberry.field(
        description="The list of children organisation units below this unit"
    )
    async def children(self, info: Info) -> List["OrganisationUnit"]:
        if not isinstance(self.uuid, UUID):
            self.parent_uuid = UUID(self.uuid)
        return await info.context["org_unit_children_loader"].load(self.uuid)
