# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from .address import AddressRead
from .association import AssociationRead
from .engagement import EngagementRead
from .it_system import ITSystemRead
from .it_system import ITUserRead
from .kle import KLERead
from .leave import LeaveRead
from .manager import ManagerRead
from .owner import OwnerRead
from .related_unit import RelatedUnitRead

__all__ = [
    "AddressRead",
    "AssociationRead",
    "EngagementRead",
    "ITSystemRead",
    "ITUserRead",
    "KLERead",
    "LeaveRead",
    "ManagerRead",
    "OwnerRead",
    "RelatedUnitRead",
]
