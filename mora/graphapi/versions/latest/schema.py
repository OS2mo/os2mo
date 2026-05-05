# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph."""

from .collections.address import Address
from .collections.address import DARAddress
from .collections.address import DefaultAddress
from .collections.address import MultifieldAddress
from .collections.address import ResolvedAddress
from .collections.association import Association
from .collections.classes import Class
from .collections.employee import Employee
from .collections.engagement import Engagement
from .collections.facet import Facet
from .collections.file import File
from .collections.health import Health
from .collections.it import ITSystem
from .collections.it import ITUser
from .collections.kle import KLE
from .collections.leave import Leave
from .collections.manager import Manager
from .collections.organisation import Organisation
from .collections.organisation_unit import OrganisationUnit
from .collections.owner import Owner
from .collections.related_unit import RelatedUnit
from .collections.role_binding import RoleBinding
from .collections.version import Version

__all__ = [
    "Address",
    "DARAddress",
    "DefaultAddress",
    "MultifieldAddress",
    "ResolvedAddress",
    "Association",
    "Class",
    "File",
    "Health",
    "Version",
    "Employee",
    "Engagement",
    "Facet",
    "ITSystem",
    "ITUser",
    "KLE",
    "Leave",
    "Manager",
    "Organisation",
    "OrganisationUnit",
    "Owner",
    "RelatedUnit",
    "RoleBinding",
]
