#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from ._shared import MOBase
from .employee import Employee
from .employee import EmployeeRead
from .employee import EmployeeWrite
from .facet import FacetClass
from .organisation_unit import OrganisationUnit
from .organisation_unit import OrganisationUnitRead
from .organisation_unit import OrganisationUnitWrite

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------

__all__ = [
    "MOBase",
    "Employee",
    "EmployeeRead",
    "EmployeeWrite",
    "FacetClass",
    "OrganisationUnit",
    "OrganisationUnitRead",
    "OrganisationUnitWrite",
]
