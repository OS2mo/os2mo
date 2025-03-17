# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""New types for mypy validation."""

from typing import NewType
from typing import TypeAlias
from uuid import UUID

# TODO: Consider a proper type with validation
CPRNumber = NewType("CPRNumber", str)
OrgUnitUUID = NewType("OrgUnitUUID", UUID)
EmployeeUUID = NewType("EmployeeUUID", UUID)
EngagementUUID = NewType("EngagementUUID", UUID)
ManagerUUID = NewType("ManagerUUID", UUID)


class LDAPUUID(UUID):
    pass


# TODO: Convert this to a NewType
DN: TypeAlias = str
RDN: TypeAlias = str
