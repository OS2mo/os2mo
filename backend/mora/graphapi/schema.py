# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import List
from typing import Optional
from uuid import UUID

import strawberry
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import LeaveRead
from ramodels.mo._shared import DynamicClasses
from ramodels.mo.details import RoleRead
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import ITUserRead
from mora.graphapi.models import ClassRead
from ramodels.mo._shared import OpenValidity
from ramodels.mo._shared import Validity
from strawberry.types import Info


@strawberry.experimental.pydantic.type(model=DynamicClasses, all_fields=True)
class DynamicClassesType:
    pass


@strawberry.experimental.pydantic.type(model=Validity, all_fields=True)
class ValidityType:
    pass


@strawberry.experimental.pydantic.type(model=OpenValidity, all_fields=True)
class OpenValidityType:
    pass


@strawberry.experimental.pydantic.type(
    model=KLERead,
    all_fields=True,
    description=("Get KLE's; Kommunernes Landsforenings Emnesystematik."),
)
class KLEType:
    pass


@strawberry.experimental.pydantic.type(
    model=RoleRead,
    all_fields=True,
    description=(
        "A role; Describing the relationsship between an org_unit and a person."
    ),
)
class RoleType:
    pass


@strawberry.experimental.pydantic.type(
    model=AddressRead,
    all_fields=True,
    description=(
        "An Address; storing address information for an identity or organisation unit."
    ),
)
class AddressType:
    pass


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    all_fields=True,
    description=("An Association; connected to an org_unit and a person."),
)
class AssociationType:
    pass


@strawberry.experimental.pydantic.type(
    model=ITUserRead,
    all_fields=True,
    description=("An ITUser; storing information for an IT user."),
)
class ITUserType:
    pass


@strawberry.experimental.pydantic.type(
    model=RelatedUnitRead,
    all_fields=True,
    description=("A RelatedUnit; storing a list of related organisational units."),
)
class RelatedUnitType:
    pass


@strawberry.experimental.pydantic.type(
    model=OrganisationRead,
    all_fields=True,
    description=("The root-organisation." "One and only one of these can exist."),
)
class OrganisationType:
    pass


@strawberry.experimental.pydantic.type(
    model=EmployeeRead,
    all_fields=True,
    description=("An Employee; containing personal information about an identity."),
)
class EmployeeType:
    @strawberry.field(description="Full name of the employee")
    async def name(self, root: EmployeeRead) -> str:
        return f"{root.givenname} {root.surname}"

    @strawberry.field(description="Full nickname of the employee")
    async def nickname(self, root: EmployeeRead) -> str:
        return f"{root.nickname_givenname} {root.nickname_surname}"


@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRead,
    all_fields=True,
    description=(
        "An Organisation Unit: the hierarchical unit creating the organisation tree."
    ),
)
class OrganisationUnitType:
    @strawberry.field(description="The immediate ancestor in the organisation tree.")
    async def parent(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["OrganisationUnitType"]:
        """Get the immediate ancestor in the organisation tree

        Returns:
            Optional[OrganisationUnitType]: The ancestor, if any.
        """
        if not root.parent_uuid:
            return None

        return await info.context["org_unit_loader"].load(root.parent_uuid)

    @strawberry.field(description="The immediate descendants in the organisation tree.")
    async def children(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["OrganisationUnitType"]:
        """Get the immediate descendants of the organistion unit.

        Returns:
            List[OrganisationUnitType]: List of descendants, if any.
        """
        if not isinstance(root.uuid, UUID):
            root.parent_uuid = UUID(root.uuid)
        return await info.context["org_unit_children_loader"].load(root.uuid)


@strawberry.experimental.pydantic.type(model=EngagementRead, all_fields=True)
class EngagementType:
    pass


@strawberry.experimental.pydantic.type(model=LeaveRead, all_fields=True)
class LeaveType:
    pass


@strawberry.experimental.pydantic.type(model=ManagerRead, all_fields=True)
class ManagerType:
    pass


@strawberry.experimental.pydantic.type(
    model=ClassRead,
    all_fields=True,
    description=("A Class: the value component of the class/facet choice setup."),
)
class ClassType:
    pass
