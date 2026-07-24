# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from typing import get_args

Collections = Literal[
    "accesslog",
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
    "policy",
    "registration",
    "related_unit",
    "rolebinding",
    "version",
]
CollectionPermissionType = Literal[
    "read", "create", "update", "terminate", "delete", "refresh"
]
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


ALL_PERMISSIONS = {
    f"{permission_type}_{collection}"
    for permission_type in get_args(CollectionPermissionType)
    for collection in get_args(Collections)
}.union(get_args(FilePermissions)).union(get_args(EventPermissions))
