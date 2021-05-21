#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from ._shared import MOBase
from .address import Address
from .employee import Employee
from .engagement import Engagement
from .engagement import EngagementAssociation
from .manager import Manager
from .organisation_unit import OrganisationUnit

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------

__all__ = [
    "MOBase",
    "Address",
    "Employee",
    "Engagement",
    "EngagementAssociation",
    "Manager",
    "OrganisationUnit",
]
