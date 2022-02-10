#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Union

from .address import Address
from .address import AddressRead
from .address import AddressWrite
from .association import Association
from .association import AssociationBase
from .association import AssociationRead
from .association import AssociationWrite
from .engagement import Engagement
from .engagement import EngagementAssociation
from .engagement import EngagementRead
from .engagement import EngagementWrite
from .it_system import ITSystemRead
from .it_system import ITUser
from .it_system import ITUserRead
from .it_system import ITUserWrite
from .kle import KLE
from .kle import KLEBase
from .kle import KLERead
from .kle import KLEWrite
from .leave import Leave
from .leave import LeaveBase
from .leave import LeaveRead
from .leave import LeaveWrite
from .manager import Manager
from .manager import ManagerBase
from .manager import ManagerRead
from .manager import ManagerWrite
from .related_unit import RelatedUnitBase
from .related_unit import RelatedUnitRead
from .related_unit import RelatedUnitWrite
from .role import Role
from .role import RoleBase
from .role import RoleRead
from .role import RoleWrite

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------
Details = Union[
    Association, Engagement, EngagementAssociation, KLE, Manager, ITUser, Role
]
EmployeeDetails = Union[Details, Address, Leave]
OrgUnitDetails = Details

__all__ = [
    "EmployeeDetails",
    "OrgUnitDetails",
    "Address",
    "AddressRead",
    "AddressWrite",
    "Association",
    "AssociationBase",
    "AssociationRead",
    "AssociationWrite",
    "Engagement",
    "EngagementRead",
    "EngagementWrite",
    "EngagementAssociation",
    "ITSystemRead",
    "ITUser",
    "ITUserRead",
    "ITUserWrite",
    "KLE",
    "KLEBase",
    "KLERead",
    "KLEWrite",
    "Manager",
    "ManagerBase",
    "ManagerRead",
    "ManagerWrite",
    "RelatedUnitBase",
    "RelatedUnitRead",
    "RelatedUnitWrite",
    "Role",
    "RoleBase",
    "RoleRead",
    "RoleWrite",
    "Leave",
    "LeaveBase",
    "LeaveRead",
    "LeaveWrite",
]
