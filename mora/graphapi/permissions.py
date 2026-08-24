# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

Collections = Literal[
    "accesslog",
    "actor",
    "address",
    "association",
    "class",
    "configuration",
    "employee",
    "engagement",
    "event",
    "event_listener",
    "event_namespace",
    "facet",
    "file",
    "health",
    "itsystem",
    "ituser",
    "kle",
    "leave",
    "manager",
    "org",
    "org_unit",
    "owner",
    "registration",
    "related_unit",
    "rolebinding",
    "version",
]
CollectionPermissionType = Literal[
    "read", "create", "update", "terminate", "delete", "refresh"
]

# Writes are governed by the "admin" role, reads by the "reader" role.
# "owner" grants write access to owned entities via the owner-policy.
ALL_PERMISSIONS = {"admin", "reader", "owner"}
