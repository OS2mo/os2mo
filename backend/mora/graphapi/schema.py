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

    name: str
    givenname: str
    surname: str

    nickname: str
    nickname_givenname: str
    nickname_surname: str

    seniority: str
    validity: QLValidity

    # TODO: Remove this field?
    @strawberry.field(description="The root organisation")
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)


@strawberry.type(
    description=(
        "An Organisation Unit; the hierarchical unit creating the organisation tree."
    )
)
class OrganisationUnit(Constructable):
    uuid: UUID
    user_key: str
    name: str

    unittype_uuid: Optional[UUID]
    timeplanning_uuid: Optional[UUID]
    org_unit_level_uuid: Optional[UUID]
    parent_uuid: Optional[UUID]

    validity: QLValidity

    @strawberry.field(description="The parent organisation unit above this unit")
    async def parent(self, info: Info) -> Optional["OrganisationUnit"]:
        # TODO: Return org as parent when self.parent_uuid is None?
        if self.parent_uuid:
            return await info.context["org_unit_loader"].load(self.parent_uuid)
        return None

    @strawberry.field(
        description="The list of children organisation units below this unit"
    )
    async def children(self, info: Info) -> List["OrganisationUnit"]:
        return await info.context["org_unit_children_loader"].load(self.uuid)
