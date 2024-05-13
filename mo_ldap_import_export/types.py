# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""New types for mypy validation."""
from typing import NewType
from typing import TypeAlias
from uuid import UUID

# TODO: Consider a proper type with validation
CPRNumber = NewType("CPRNumber", str)
OrgUnitUUID = NewType("OrgUnitUUID", UUID)
# TODO: Convert this to a NewType
DN: TypeAlias = str
