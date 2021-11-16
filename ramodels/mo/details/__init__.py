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
from .it_system import ITSystemBinding
from .it_system import ITSystemBindingRead
from .it_system import ITSystemBindingWrite
from .leave import Leave
from .leave import LeaveBase
from .leave import LeaveRead
from .leave import LeaveWrite
from .manager import Manager
from .role import Role

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------
Details = Union[
    Association, Engagement, EngagementAssociation, Manager, ITSystemBinding, Role
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
    "ITSystemBinding",
    "ITSystemBindingRead",
    "ITSystemBindingWrite",
    "Manager",
    "Role",
    "Leave",
    "LeaveBase",
    "LeaveRead",
    "LeaveWrite",
]
