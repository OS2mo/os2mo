# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The collections access can be granted on."""

import enum


class Collection(enum.StrEnum):
    """Names the collections a rule may grant on."""

    Address = "Address"
    Association = "Association"
    Class = "Class"
    Employee = "Employee"
    Engagement = "Engagement"
    Facet = "Facet"
    ITSystem = "ITSystem"
    ITUser = "ITUser"
    KLE = "KLE"
    Leave = "Leave"
    Manager = "Manager"
    Organisation = "Organisation"
    OrganisationUnit = "OrganisationUnit"
    Owner = "Owner"
    RelatedUnit = "RelatedUnit"
    RoleBinding = "RoleBinding"
