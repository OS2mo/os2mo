# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from functools import cache
from functools import partial
from typing import Any
from typing import Literal
from typing import get_args

from fastapi import HTTPException
from graphql import OperationType
from strawberry import BasePermission
from strawberry.types import Info

from mora.auth.exceptions import AuthorizationError
from mora.config import get_settings

Collections = Literal[
    "address",
    "association",
    "auditlog",
    "class",
    "configuration",
    "employee",
    "engagement",
    "facet",
    "file",
    "health",
    "itsystem",
    "ituser",
    "kle",
    "leave",
    "manager",
    "owner",
    "org",
    "org_unit",
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


ALL_PERMISSIONS = {
    f"{permission_type}_{collection}"
    for permission_type in get_args(CollectionPermissionType)
    for collection in get_args(Collections)
}.union(get_args(FilePermissions))


class IsAuthenticatedPermission(BasePermission):
    """Permission class that checks that the request is authenticated."""

    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        """Returns `True` if a valid token exists."""
        settings = get_settings()
        # Always grant access if auth is disabled
        if not settings.os2mo_auth:  # pragma: no cover
            return True
        try:
            token = await info.context["get_token"]()
        except HTTPException as e:
            raise PermissionError(e.detail) from e
        return token is not None


@cache
def gen_role_permission(
    permission_role: str,
    message: str | None = None,
    force_permission_check: bool = False,
    collection: Collections | None = None,
    permission_type: CollectionPermissionType | None = None,
) -> type[BasePermission]:
    """Generator function for permission classes.

    Args:
        permission_role: The role to check existence for.
        message: Optional message override.
        collection: Optional collection used for owner check.
        collection: Optional permission type used for owner check.

    Returns:
        Permission class that checks if `role_name` is in the OIDC token.
    """
    fail_message = message or f"User does not have required role: {permission_role}"

    class CheckRolePermission(BasePermission):
        """Permission class that checks that a given role exists on the OIDC token.

        If the simple role-check fails, we additionally allow access if the operation
        is a mutation and the user is an owner of the object. This probably should be
        implemented in a separate permission class, but Strawberry does not support
        combining multiple permissions with OR.
        https://github.com/strawberry-graphql/strawberry/issues/2350
        """

        message = fail_message

        async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
            """Returns `True` if `role_name` exists in the token's roles."""
            settings = get_settings()

            # Do not check permissions (always allow) if GraphQL RBAC is disabled,
            # unless forced.
            if (not settings.graphql_rbac) and (not force_permission_check):
                return True

            token = await info.context["get_token"]()
            token_roles = token.realm_access.roles

            # TODO (#55042): Backwards-compatible fix for !1594. Remove when Aarhus is
            # migrated to Azure.
            if (
                settings.graphql_rbac_legacy_admin_role and "admin" in token_roles
            ):  # pragma: no cover
                return True

            # Allow access if token has required role
            if permission_role in token_roles:
                return True

            # Allow access if user is owner. This only works for mutations at the
            # moment, since we need access to the object's UUID to determine ownership.
            if (
                "owner" in token_roles
                and info.operation.operation is OperationType.MUTATION
                and collection is not None
                and permission_type is not None
            ):
                # Import here to avoid circular imports 🙂👍
                from mora.auth.keycloak.rbac import check_owner
                from mora.auth.keycloak.uuid_extractor import get_entities_graphql

                # The arguments to this function are the same as the arguments given to the
                # mutator. Therefore, if the mutator takes an `input` argument, `input`
                # will be available to us in the kwargs. We don't catch KeyErrors on
                # purpose to expose a potentially buggy implementation to the user; the
                # permission check would have failed anyway.
                input = kwargs["input"]
                entities = {
                    x
                    async for x in get_entities_graphql(
                        input, collection, permission_type
                    )
                }
                with suppress(AuthorizationError):
                    await check_owner(token, entities)
                    return True

            return False

    return CheckRolePermission


def gen_permission(
    collection: Collections,
    permission_type: CollectionPermissionType,
    force_permission_check: bool = False,
) -> type[BasePermission]:
    """Generator function for permission classes.

    Utilizes `gen_role_permission` with a generated role-name and a custom message.

    Args:
        collection_name: Name of the collection to check access to.

    Returns:
        Permission class that checks if the `collection_name` derived role is in the
        OIDC token.
    """
    assert collection in get_args(Collections), f"{collection} not a valid collection"
    assert permission_type in get_args(CollectionPermissionType), (
        f"{permission_type} not a valid permission type"
    )

    permission_name = f"{permission_type}_{collection}"
    return gen_role_permission(
        permission_name,
        f"User does not have {permission_type}-access to {collection}",
        force_permission_check=force_permission_check,
        collection=collection,
        permission_type=permission_type,
    )


gen_read_permission = partial(gen_permission, permission_type="read")
gen_create_permission = partial(
    gen_permission, permission_type="create", force_permission_check=True
)
gen_update_permission = partial(
    gen_permission, permission_type="update", force_permission_check=True
)
gen_terminate_permission = partial(
    gen_permission, permission_type="terminate", force_permission_check=True
)
gen_delete_permission = partial(
    gen_permission, permission_type="delete", force_permission_check=True
)
gen_refresh_permission = partial(
    gen_permission, permission_type="refresh", force_permission_check=True
)
