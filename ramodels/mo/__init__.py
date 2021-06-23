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
from .association import Association
from .employee import Employee
from .engagement import Engagement
from .engagement import EngagementAssociation
from .facet import FacetClass
from .manager import Manager
from .organisation_unit import OrganisationUnit

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------

__all__ = [
    "MOBase",
    "Address",
    "Association",
    "Employee",
    "Engagement",
    "EngagementAssociation",
    "FacetClass",
    "Manager",
    "OrganisationUnit",
]
