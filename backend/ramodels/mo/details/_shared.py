#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Optional

from ramodels.base import RABase
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import OrgUnitRef

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class Details(RABase):
    employee: Optional[EmployeeRef]
    org_unit: Optional[OrgUnitRef]
