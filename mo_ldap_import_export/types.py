# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""New types for mypy validation."""
from typing import NewType

# TODO: Consider a proper type with validation
CPRNumber = NewType("CPRNumber", str)
