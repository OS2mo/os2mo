# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from typing import Any
from typing import Literal
from typing import get_args

from graphql import GraphQLResolveInfo
from graphql import OperationType

from mora.auth.exceptions import AuthorizationError

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


async def _check_rbac(
    info: GraphQLResolveInfo,
    permission_role: str,
    collection: Collections | None,
    permission_type: CollectionPermissionType | None,
    kwargs: dict[str, Any],
) -> bool:
    """Returns `True` if `role_name` exists in the token's roles."""
    token = await info.context.get_token()
    token_roles = token.realm_access.roles

    # Allow access if token has required role
    if permission_role in token_roles:
        return True

    # Allow access if user is owner. This only works for mutations at the
    # moment, since we need access to the object's UUID to determine ownership.
    # The object UUID is derived from the "input" key in kwargs which holds the
    # mutators call args. Owner is currently only implemented for mutators
    # taking an "input" key as its input.
    if (
        "owner" in token_roles
        and info.operation.operation is OperationType.MUTATION
        and collection is not None
        and permission_type is not None
        and "input" in kwargs
    ):
        # Import here to avoid circular imports 🙂👍
        from mora.auth.keycloak.rbac import check_owner
        from mora.auth.keycloak.uuid_extractor import get_entities_graphql

        input = kwargs["input"]
        entities = {
            x async for x in get_entities_graphql(input, collection, permission_type)
        }
        with suppress(AuthorizationError):
            await check_owner(token, entities)
            return True

    return False
