# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import cache
from typing import Any

from fastapi import HTTPException
from prometheus_client import Counter
from strawberry import BasePermission
from strawberry.types import Info

from mora.config import get_settings

rbac_counter = Counter("graphql_rbac", "Number of RBAC checks", ["role", "allowed"])


class IsAuthenticatedPermission(BasePermission):
    """Permission class that checks that the request is authenticated."""

    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        """Returns `True` if a valid token exists."""
        settings = get_settings()
        # Always grant access if auth is disabled
        if not settings.os2mo_auth:
            return True
        try:
            token = await info.context["get_token"]()
        except HTTPException as e:
            raise PermissionError(e.detail) from e
        return token is not None


@cache
def gen_role_permission(
    role_name: str, message: str | None = None, force_permission_check: bool = False
) -> type[BasePermission]:
    """Generator function for permission classes.

    Args:
        role_name: The role to check existence for.
        message: Optional message override.

    Returns:
        Permission class that checks if `role_name` is in the OIDC token.
    """
    fail_message = message or f"User does not have required role: {role_name}"

    class CheckRolePermission(BasePermission):
        """Permission class that checks that a given role exists on the OIDC token."""

        message = fail_message

        async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
            """Returns `True` if `role_name` exists in the token's roles."""
            settings = get_settings()
            # If GraphQL RBAC is not enabled, do not check permissions, unless forced
            if (not settings.graphql_rbac) and (not force_permission_check):
                return True
            # Allow access only if expected role is in roles
            token = await info.context["get_token"]()
            roles = token.realm_access.roles
            allow_access = role_name in roles
            rbac_counter.labels(role=role_name, allowed=allow_access).inc()
            return allow_access

    return CheckRolePermission


# Should this list should either just be dynamic or an enum?
PERMISSIONS = {
    f"read_{collection_name}"
    for collection_name in {
        "address",
        "association",
        "class",
        "configuration",
        "employee",
        "engagement_association",
        "engagement",
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
        "related_unit",
        "role",
        "version",
    }
}


def gen_read_permission(collection_name: str) -> type[BasePermission]:
    """Generator function for permission classes.

    Utilizes `gen_role_permission` with a generated role-name and a custom message.

    Args:
        collection_name: Name of the collection to check access to.

    Returns:
        Permission class that checks if the `collection_name` derived role is in the
        OIDC token.
    """
    permission_name = f"read_{collection_name}"
    assert permission_name in PERMISSIONS, f"{permission_name} not in PERMISSIONS"
    return gen_role_permission(
        permission_name,
        f"User does not have read-access to {collection_name}",
    )
