# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from typing import get_args

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
# Permission types which are expanded into per-collection Keycloak roles.
# "read" is excluded: reads are governed by the single "reader" role.
ROLE_PERMISSION_TYPES = [p for p in get_args(CollectionPermissionType) if p != "read"]
FilePermissions = Literal[
    "list_files",
    "download_files",
    "upload_files",
]
EventPermissions = Literal[
    "fetch_event",
    "acknowledge_event",
    "send_event",
    "silence_event",
    "unsilence_event",
    "rerun_event",
]


ALL_PERMISSIONS = (
    {
        f"{permission_type}_{collection}"
        for permission_type in ROLE_PERMISSION_TYPES
        for collection in get_args(Collections)
    }.union(get_args(FilePermissions))
    .union(get_args(EventPermissions))
    .union({"reader"})
)
