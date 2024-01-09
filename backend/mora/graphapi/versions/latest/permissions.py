# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import cache
from functools import partial
from typing import Any
from typing import get_args
from typing import Literal

from fastapi import HTTPException
from prometheus_client import Counter
from strawberry import BasePermission
from strawberry.types import Info

from mora.config import get_settings

rbac_counter = Counter("graphql_rbac", "Number of RBAC checks", ["role", "allowed"])


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
    "role",
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
            # TODO (#55042): Backwards-compatible fix for !1594. Remove when Aarhus is
            # migrated to Azure.
            if settings.graphql_rbac_legacy_admin_role and "admin" in roles:
                return True
            allow_access = role_name in roles
            rbac_counter.labels(role=role_name, allowed=allow_access).inc()
            return allow_access

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
    assert permission_type in get_args(
        CollectionPermissionType
    ), f"{permission_type} not a valid permission type"

    permission_name = f"{permission_type}_{collection}"
    return gen_role_permission(
        permission_name,
        f"User does not have {permission_type}-access to {collection}",
        force_permission_check=force_permission_check,
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


import vakt
from vakt.rules.base import Rule
from vakt.rules import Eq, Any, Falsy, Truthy
from uuid import uuid4
from operator import itemgetter


class VaktPermission(BasePermission):
    """Permission class that checks that the request is authorized."""

    message = "Vakt rejected"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        """Evaluate the request against all vakt policies."""

        auth_enabled = get_settings().os2mo_auth

        try:
            token = await info.context["get_token"]()
        except HTTPException:
            token = None

        def nt2dict(obj) -> dict[str, Any]:
            if hasattr(obj, "_asdict"):
                return {k: nt2dict(v) for k, v in obj._asdict().items()}
            return obj

        inquiry = vakt.Inquiry(
            # TODO: Determine from top-level typename
            # If Query == 'read'
            # If Mutation, check mutator name structure
            action='read',  # read, create, delete, refresh, terminate, update
#            # Has the format of:
#            {
#                "prev": {
#                    "prev": None,
#                    "key": 'org_units',
#                    "typename": 'Query'
#                },
#                "key": 'objects',
#                "typename": 'OrganisationUnitResponsePaged'
#            }
# for:
#            query {
#              org_units {
#                objects {
#                  ...
#                }
#              }
#            }
            resource=nt2dict(info.path),
#            # Has the format of:
#            {
#                "azp": 'mo-frontend',
#                "email": 'alvidan@kolding.dk',
#                "preferred_username": 'alvida',
#                "realm_access": {
#                    "roles": {'read_version', 'file_admin', ...},
#                }
#                "uuid": UUID('0fb62199-cb9e-4083-ba45-2a63bfd142d7')
#            }
            subject=token.dict(by_alias=True),
            context={
                # True/False
                "os2mo_auth": auth_enabled,
                # Contains the object we are extracting fields on
                "source": source,
                # 20
                "version": info.context["version"],

                # "field_name": info.field_name,
                # "selected_fields": info.selected_fields,
                # "request": info.context["request"],
                # "response": info.context["response"],
            }
        )
        # Ask Vakt to run the inquiry through all policies
        guard = info.context["guard"]
        return guard.is_allowed(inquiry)


class TranslateRule(Rule):
    def __init__(self, func, rule):
        assert isinstance(rule, Rule)
        self.func = func
        self.rule = rule

    def satisfied(self, what, inquiry=None):
        return self.rule.satisfied(self.func(what), inquiry)


def GetItemRule(name: str, rule) -> TranslateRule:
    return TranslateRule(itemgetter(name), rule)


class SubsetContains(Rule):
    def __init__(self, roles):
        assert isinstance(roles, set)
        self.roles = roles

    def satisfied(self, what, inquiry=None):
        assert isinstance(what, set)
        return self.roles.issubset(what)


def get_guard() -> vakt.Guard:
    storage = vakt.MemoryStorage()
    storage.add(vakt.Policy(
        uuid4(),
        # No matter the action
        actions=[Any()],
        # No matter the resource
        resources=[Any()],
        # No matter who
        subjects=[Any()],
        # If OS2mo_auth is disabled
        context={
            "os2mo_auth": Falsy()
        },
        effect=vakt.ALLOW_ACCESS,
        description="Allow all access if os2mo_auth is disabled"
    ))
    storage.add(vakt.Policy(
        uuid4(),
        # If a read operation
        actions=[Eq('read')],
        # If we are looking up a random field on orgunits
        resources=[{
            "typename": Eq('OrganisationUnit'),
            "key": Any()
        }],
        # If we have the read_org_unit role
        subjects=[
            {
                "realm_access": GetItemRule(
                    "roles",
                    SubsetContains({'read_org_unit',})
                )
            }
        ],
        # If OS2mo_auth is enabled
        context={
            "os2mo_auth": Truthy(),
        },
        effect=vakt.ALLOW_ACCESS,
        description="""
        Allow access to read OrganisationUnits if the appropriate role is found
        """
    ))
    storage.add(vakt.Policy(
        uuid4(),
        actions=[Eq('read')],
        resources=[{
            "typename": Eq('OrganisationUnit'),
            "key": Eq('uuid')
        }],
        subjects=[Any()],
        # If OS2mo_auth is enabled
        context={
            "os2mo_auth": Truthy(),
        },
        effect=vakt.DENY_ACCESS,  # Reject for testing
        description="""
        Disallow reading OrganisationUnit.uuid
        """
    ))
    # NOTE: If no matching policies allow access, access is denied

#    query MyQuery {
#      org_units(limit: "1") {
#        objects {
#          uuid
#          current {
#            name  # This is OK
#            uuid  # This is blocked by last policy
#          }
#        }
#      }
#    }

    return vakt.Guard(storage, vakt.RulesChecker())
