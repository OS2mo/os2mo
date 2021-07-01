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
from .association import Association
from .engagement import Engagement
from .engagement import EngagementAssociation
from .manager import Manager

# --------------------------------------------------------------------------------------
# All
# --------------------------------------------------------------------------------------
Details = Union[Address, Association, Engagement, EngagementAssociation, Manager]

__all__ = [
    "Details",
    "Address",
    "Association",
    "Engagement",
    "EngagementAssociation",
    "Manager",
]
