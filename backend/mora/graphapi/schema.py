#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Strawberry types describing the MO graph."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import asyncio
from typing import List
from typing import Optional
from uuid import UUID

import strawberry
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo._shared import DynamicClasses as DynamicClassesRead
from ramodels.mo._shared import OpenValidity as OpenValidityModel
from ramodels.mo._shared import Validity as ValidityModel
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import RoleRead
from strawberry.types import Info

from mora import config
from mora import lora
from mora.graphapi.health import health_map
from mora.graphapi.models import ClassRead
from mora.graphapi.models import FacetRead
from mora.graphapi.models import HealthRead
from mora.graphapi.models import ITSystemRead
from mora.graphapi.models import SemanticVersionRead

# --------------------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------------------


@strawberry.experimental.pydantic.type(
    model=SemanticVersionRead, all_fields=True, description="Semantic version"
)
class SemanticVersion:
    pass


@strawberry.experimental.pydantic.type(
    model=DynamicClassesRead,
    all_fields=True,
    description="Dynamic class overload for associations",
)
class DynamicClasses:
    pass


@strawberry.experimental.pydantic.type(
    model=ValidityModel,
    all_fields=True,
    description="Validity of objects with required from date",
)
class Validity:
    pass


@strawberry.experimental.pydantic.type(
    model=OpenValidityModel,
    all_fields=True,
    description="Validity of objects with optional from date",
)
class OpenValidity:
    pass


@strawberry.experimental.pydantic.type(
    model=KLERead,
    all_fields=True,
    description="Kommunernes Landsforenings Emnesystematik",
)
class KLE:
    @strawberry.field(description="KLE number")
    async def kle_number(self, root: KLERead, info: Info) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.kle_number)

    @strawberry.field(description="KLE Aspect")
    async def kle_aspect(self, root: KLERead, info: Info) -> List["Class"]:
        if not root.kle_aspect_uuid:
            return []
        tasks = map(info.context["class_loader"].load, root.kle_aspect_uuid)
        return await asyncio.gather(*tasks)

    @strawberry.field(description="Associated organisation unit")
    async def org_unit(self, root: KLERead, info: Info) -> Optional["OrganisationUnit"]:
        if not root.org_unit_uuid:
            return None
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=RoleRead,
    all_fields=True,
    description="Role an employee has within an organisation unit",
)
class Role:
    @strawberry.field(description="Role type")
    async def role_type(self, root: RoleRead, info: Info) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.role_type_uuid)

    @strawberry.field(description="Connected employee")
    async def employee(self, root: RoleRead, info: Info) -> "Employee":
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Connected organisation unit")
    async def org_unit(self, root: RoleRead, info: Info) -> "OrganisationUnit":
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=AddressRead,
    all_fields=True,
    description="Address information for an employee or organisation unit",
)
class Address:
    @strawberry.field(description="Address type")
    async def address_type(self, root: AddressRead, info: Info) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.address_type_uuid)

    @strawberry.field(description="Address visibility")
    async def visibility(self, root: AddressRead, info: Info) -> Optional["Class"]:
        if not root.visibility_uuid:
            return None
        return await info.context["class_loader"].load(root.visibility_uuid)

    @strawberry.field(
        description="Connected employee. "
        "Note that this is mutually exclusive with the org_unit field"
    )
    async def employee(self, root: AddressRead, info: Info) -> Optional["Employee"]:
        if not root.employee_uuid:
            return None
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(
        description="Connected organisation unit. "
        "Note that this is mutually exclusive with the employee field"
    )
    async def org_unit(
        self, root: AddressRead, info: Info
    ) -> Optional["OrganisationUnit"]:
        if not root.org_unit_uuid:
            return None
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    all_fields=True,
    description="Connects organisation units and employees",
)
class Association:
    @strawberry.field(description="Association type")
    async def association_type(
        self, root: AssociationRead, info: Info
    ) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.association_type_uuid)

    @strawberry.field(description="Primary status")
    async def primary(self, root: AssociationRead, info: Info) -> Optional["Class"]:
        if not root.primary_uuid:
            return None
        return await info.context["class_loader"].load(root.primary_uuid)

    @strawberry.field(description="Connected employee")
    async def employee(self, root: AssociationRead, info: Info) -> "Employee":
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Connected organisation unit")
    async def org_unit(self, root: AssociationRead, info: Info) -> "OrganisationUnit":
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=ITUserRead,
    all_fields=True,
    description="User information related to IT systems",
)
class ITUser:
    @strawberry.field(description="Connected employee")
    async def employee(self, root: ITUserRead, info: Info) -> Optional["Employee"]:
        if not root.employee_uuid:
            return None
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Connected organisation unit")
    async def org_unit(
        self, root: ITUserRead, info: Info
    ) -> Optional["OrganisationUnit"]:
        if not root.org_unit_uuid:
            return None
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=RelatedUnitRead,
    all_fields=True,
    description="List of related organisation units",
)
class RelatedUnit:
    @strawberry.field(description="Related organisation units")
    async def org_unit(
        self, root: RelatedUnitRead, info: Info
    ) -> Optional["OrganisationUnit"]:
        if not root.org_unit_uuid:
            return None
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=OrganisationRead,
    all_fields=True,
    description="Root organisation - one and only one of these can exist",
)
class Organisation:
    pass


@strawberry.experimental.pydantic.type(
    model=EmployeeRead,
    all_fields=True,
    description="Employee/identity specific information",
)
class Employee:
    @strawberry.field(description="Full name of the employee")
    async def name(self, root: EmployeeRead) -> str:
        return f"{root.givenname} {root.surname}"

    @strawberry.field(description="Full nickname of the employee")
    async def nickname(self, root: EmployeeRead) -> str:
        return f"{root.nickname_givenname} {root.nickname_surname}"

    @strawberry.field(description="Engagements for the employee")
    async def engagements(self, root: EmployeeRead, info: Info) -> List["Engagement"]:
        return await info.context["employee_engagement_loader"].load(root.uuid)

    @strawberry.field(description="Manager roles for the employee")
    async def manager_roles(self, root: EmployeeRead, info: Info) -> List["Manager"]:
        return await info.context["employee_manager_role_loader"].load(root.uuid)

    @strawberry.field(description="Addresses for the employee")
    async def addresses(self, root: EmployeeRead, info: Info) -> List["Address"]:
        return await info.context["employee_address_loader"].load(root.uuid)

    @strawberry.field(description="Leaves for the employee")
    async def leaves(self, root: EmployeeRead, info: Info) -> List["Leave"]:
        return await info.context["employee_leave_loader"].load(root.uuid)

    @strawberry.field(description="Associations for the employee")
    async def associations(self, root: EmployeeRead, info: Info) -> List["Association"]:
        return await info.context["employee_association_loader"].load(root.uuid)

    @strawberry.field(description="Roles for the employee")
    async def roles(self, root: EmployeeRead, info: Info) -> List["Role"]:
        return await info.context["employee_role_loader"].load(root.uuid)

    @strawberry.field(description="IT users for the employee")
    async def itusers(self, root: EmployeeRead, info: Info) -> List["ITUser"]:
        return await info.context["employee_ituser_loader"].load(root.uuid)


@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRead,
    all_fields=True,
    description="Hierarchical unit within the organisation tree",
)
class OrganisationUnit:
    @strawberry.field(description="The immediate ancestor in the organisation tree")
    async def parent(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["OrganisationUnit"]:
        """Get the immediate ancestor in the organisation tree.

        Returns:
            Optional[OrganisationUnit]: The ancestor, if any.
        """
        if not root.parent_uuid:
            return None

        return await info.context["org_unit_loader"].load(root.parent_uuid)

    @strawberry.field(description="The immediate descendants in the organisation tree")
    async def children(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["OrganisationUnit"]:
        """Get the immediate descendants of the organistion unit.

        Returns:
            List[OrganisationUnit]: List of descendants, if any.
        """
        return await info.context["org_unit_children_loader"].load(root.uuid)

    # TODO: Add UUID to RAModel and remove model prefix here
    @strawberry.field(description="Organisation unit hierarchy")
    async def org_unit_hierarchy_model(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["Class"]:
        if not root.org_unit_hierarchy:
            return None
        return await info.context["class_loader"].load(root.org_unit_hierarchy)

    @strawberry.field(description="Organisation unit type")
    async def unit_type(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["Class"]:
        if not root.unit_type_uuid:
            return None
        return await info.context["class_loader"].load(root.unit_type_uuid)

    # TODO: Remove org prefix from RAModel and remove it here too
    @strawberry.field(description="Organisation unit level")
    async def org_unit_level(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["Class"]:
        if not root.org_unit_level_uuid:
            return None
        return await info.context["class_loader"].load(root.org_unit_level_uuid)

    @strawberry.field(description="Time planning strategy")
    async def time_planning(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional["Class"]:
        if not root.time_planning_uuid:
            return None
        return await info.context["class_loader"].load(root.time_planning_uuid)

    @strawberry.field(description="Related engagements")
    async def engagements(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["Engagement"]:
        return await info.context["org_unit_engagement_loader"].load(root.uuid)

    @strawberry.field(description="Managers of the organisation unit")
    async def managers(self, root: OrganisationUnitRead, info: Info) -> List["Manager"]:
        return await info.context["org_unit_manager_loader"].load(root.uuid)

    @strawberry.field(description="Related addresses")
    async def addresses(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["Address"]:
        return await info.context["org_unit_address_loader"].load(root.uuid)

    @strawberry.field(description="Related leaves")
    async def leaves(self, root: OrganisationUnitRead, info: Info) -> List["Leave"]:
        return await info.context["org_unit_leave_loader"].load(root.uuid)

    @strawberry.field(description="Related associations")
    async def associations(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["Association"]:
        return await info.context["org_unit_association_loader"].load(root.uuid)

    @strawberry.field(description="Related roles")
    async def roles(self, root: OrganisationUnitRead, info: Info) -> List["Role"]:
        return await info.context["org_unit_role_loader"].load(root.uuid)

    @strawberry.field(description="Related IT users")
    async def itusers(self, root: OrganisationUnitRead, info: Info) -> List["ITUser"]:
        return await info.context["org_unit_ituser_loader"].load(root.uuid)

    @strawberry.field(description="KLE responsibilites for the organisation unit")
    async def kles(self, root: OrganisationUnitRead, info: Info) -> List["KLE"]:
        return await info.context["org_unit_kle_loader"].load(root.uuid)

    @strawberry.field(description="Related units for the organisational unit")
    async def related_units(
        self, root: OrganisationUnitRead, info: Info
    ) -> List["RelatedUnit"]:
        return await info.context["org_unit_role_loader"].load(root.uuid)


@strawberry.experimental.pydantic.type(
    model=EngagementRead,
    all_fields=True,
    description="Employee engagement in an organisation unit",
)
class Engagement:
    @strawberry.field(description="Engagement type")
    async def engagement_type(
        self, root: EngagementRead, info: Info
    ) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.engagement_type_uuid)

    @strawberry.field(description="Job function")
    async def job_function(self, root: EngagementRead, info: Info) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.job_function_uuid)

    @strawberry.field(description="The primary status")
    async def primary(self, root: EngagementRead, info: Info) -> Optional["Class"]:
        if not root.primary_uuid:
            return None
        return await info.context["class_loader"].load(root.primary_uuid)

    @strawberry.field(description="Related leave")
    async def leave(self, root: EngagementRead, info: Info) -> Optional["Leave"]:
        if not root.leave_uuid:
            return None
        return await info.context["leave_loader"].load(root.leave_uuid)

    @strawberry.field(description="Related employee")
    async def employee(self, root: EngagementRead, info: Info) -> "Employee":
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Related organisation unit")
    async def org_unit(self, root: EngagementRead, info: Info) -> "OrganisationUnit":
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=LeaveRead,
    all_fields=True,
    description="Leave (e.g. parental leave) for employees",
)
class Leave:
    @strawberry.field(description="Leave type")
    async def leave_type(self, root: LeaveRead, info: Info) -> Optional["Class"]:
        return await info.context["class_loader"].load(root.leave_type_uuid)

    @strawberry.field(description="Related employee")
    async def employee(self, root: LeaveRead, info: Info) -> "Employee":
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Related engagement")
    async def engagement(self, root: LeaveRead, info: Info) -> Optional["Engagement"]:
        if not root.engagement_uuid:
            return None
        return await info.context["engagement_loader"].load(root.engagement_uuid)


@strawberry.experimental.pydantic.type(
    model=ManagerRead,
    all_fields=True,
    description="Managers of organisation units and their connected identities",
)
class Manager:
    @strawberry.field(description="Manager type")
    async def manager_type(self, root: ManagerRead, info: Info) -> Optional["Class"]:
        if not root.manager_type_uuid:
            return None
        return await info.context["class_loader"].load(root.manager_type_uuid)

    @strawberry.field(description="Manager level")
    async def manager_level(self, root: ManagerRead, info: Info) -> Optional["Class"]:
        if not root.manager_level_uuid:
            return None
        return await info.context["class_loader"].load(root.manager_level_uuid)

    @strawberry.field(description="Manager responsibilities")
    async def responsibilities(self, root: ManagerRead, info: Info) -> List["Class"]:
        if not root.responsibility_uuids:
            return []
        tasks = map(info.context["class_loader"].load, root.responsibility_uuids)
        return await asyncio.gather(*tasks)

    @strawberry.field(description="Manager identity details")
    async def employee(self, root: ManagerRead, info: Info) -> Optional["Employee"]:
        if not root.employee_uuid:
            return None
        return await info.context["employee_loader"].load(root.employee_uuid)

    @strawberry.field(description="Managed organisation unit")
    async def org_unit(
        self, root: ManagerRead, info: Info
    ) -> Optional["OrganisationUnit"]:
        if not root.org_unit_uuid:
            return None
        return await info.context["org_unit_loader"].load(root.org_unit_uuid)


@strawberry.experimental.pydantic.type(
    model=ClassRead,
    all_fields=True,
    description="The value component of the class/facet choice setup",
)
class Class:
    @strawberry.field(description="Immediate parent class")
    async def parent(self, root: ClassRead, info: Info) -> Optional["Class"]:
        """Get the immediate parent class.

        Returns:
            Class: Parent class
        """
        if not root.parent_uuid:
            return None

        return await info.context["class_loader"].load(root.parent_uuid)

    @strawberry.field(description="Immediate descendants of the class")
    async def children(self, root: ClassRead, info: Info) -> List["Class"]:
        """Get the immediate descendants of the class.

        Returns:
            List[Class]: List of descendants, if any.
        """
        if not isinstance(root.uuid, UUID):
            root.parent_uuid = UUID(root.uuid)
        return await info.context["class_children_loader"].load(root.uuid)

    @strawberry.field(description="Associated facet")
    async def facet(self, root: ClassRead, info: Info) -> Optional["Facet"]:
        """Get the associated facet.

        Returns:
            The associated facet.
        """
        return await info.context["facet_loader"].load(root.facet_uuid)


@strawberry.experimental.pydantic.type(
    model=FacetRead,
    all_fields=True,
    description="The key component of the class/facet choice setup",
)
class Facet:
    @strawberry.field(description="Associated classes")
    async def classes(self, root: FacetRead, info: Info) -> List["Class"]:
        """Get the associated classes.

        Returns:
            The associated classes.
        """
        return await info.context["facet_classes_loader"].load(root.uuid)


@strawberry.type(description="MO & LoRa versions")
class Version:
    @strawberry.field(description="OS2mo Version")
    async def mo_version(self) -> Optional[SemanticVersion]:
        """Get the mo version.

        Returns:
            The version.
        """
        settings = config.get_settings()
        commit_tag = settings.commit_tag
        if not commit_tag:
            return None
        major, minor, patch = commit_tag.split(".")
        return SemanticVersionRead(major=major, minor=minor, patch=patch)

    @strawberry.field(description="OS2mo commit hash")
    async def mo_hash(self) -> Optional[str]:
        """Get the mo commit hash.

        Returns:
            The commit hash.
        """
        settings = config.get_settings()
        commit_sha = settings.commit_sha
        if not commit_sha:
            return None
        return commit_sha

    @strawberry.field(description="LoRa version")
    async def lora_version(self) -> Optional[SemanticVersion]:
        """Get the lora version.

        Returns:
            The version.
        """
        commit_tag = await lora.get_version()
        if not commit_tag:
            return None
        major, minor, patch = commit_tag.split(".")
        return SemanticVersionRead(major=major, minor=minor, patch=patch)


@strawberry.experimental.pydantic.type(
    model=HealthRead,
    all_fields=True,
    description="Checks whether a specific subsystem is working",
)
class Health:
    @strawberry.field(description="Healthcheck status")
    async def status(self, root: HealthRead) -> bool:
        return await health_map[root.identifier]()


@strawberry.experimental.pydantic.type(
    model=ITSystemRead,
    all_fields=True,
    description="Systems that IT users are connected to",
)
class ITSystem:
    pass
