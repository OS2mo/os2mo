# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from .address import Address
from .address import AddressDetail
from .address import AddressRead
from .address import AddressWrite
from .association import Association
from .association import AssociationBase
from .association import AssociationDetail
from .association import AssociationRead
from .association import AssociationWrite
from .engagement import Engagement
from .engagement import EngagementDetail
from .engagement import EngagementRead
from .engagement import EngagementWrite
from .engagement_association import EngagementAssociation
from .engagement_association import EngagementAssociationRead
from .it_system import ITSystemRead
from .it_system import ITUser
from .it_system import ITUserDetail
from .it_system import ITUserRead
from .it_system import ITUserWrite
from .kle import KLE
from .kle import KLEBase
from .kle import KLEDetail
from .kle import KLERead
from .kle import KLEWrite
from .leave import Leave
from .leave import LeaveBase
from .leave import LeaveDetail
from .leave import LeaveRead
from .leave import LeaveWrite
from .manager import Manager
from .manager import ManagerBase
from .manager import ManagerDetail
from .manager import ManagerRead
from .manager import ManagerWrite
from .related_unit import RelatedUnitBase
from .related_unit import RelatedUnitRead
from .related_unit import RelatedUnitWrite
from .role import Role
from .role import RoleBase
from .role import RoleDetail
from .role import RoleRead
from .role import RoleWrite


Details = (
    AssociationDetail
    | EngagementDetail
    | EngagementAssociation
    | KLEDetail
    | ManagerDetail
    | ITUserDetail
    | RoleDetail
)
EmployeeDetails = Details | AddressDetail | LeaveDetail
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
    "EngagementAssociationRead",
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
