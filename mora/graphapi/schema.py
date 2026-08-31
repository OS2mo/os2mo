# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
import traceback
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from contextlib import suppress
from functools import cache
from types import SimpleNamespace
from typing import TYPE_CHECKING
from typing import Any

from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from graphql import GraphQLResolveInfo
from graphql import OperationType
from graphql import is_introspection_type
from pydantic import PositiveInt
from starlette.datastructures import UploadFile
from strawberry import Schema
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.file_uploads import UploadDefinition
from strawberry.schema.config import StrawberryConfig
from strawberry.utils.await_maybe import AsyncIteratorOrIterator
from strawberry.utils.await_maybe import await_maybe
from structlog import get_logger

from mora import config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.db import get_session
from mora.exceptions import HTTPException
from mora.graphapi.actor import SpecialActor
from mora.graphapi.actor import UnknownActor
from mora.graphapi.collections import DARAddress
from mora.graphapi.collections import DefaultAddress
from mora.graphapi.collections import MultifieldAddress
from mora.graphapi.custom_schema import CustomSchema
from mora.graphapi.events import EVENT_TOKEN_SCALAR
from mora.graphapi.events import EventToken
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import ITSystemFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.model_registration import AddressRegistration
from mora.graphapi.model_registration import AssociationRegistration
from mora.graphapi.model_registration import ClassRegistration
from mora.graphapi.model_registration import EngagementRegistration
from mora.graphapi.model_registration import FacetRegistration
from mora.graphapi.model_registration import ITSystemRegistration
from mora.graphapi.model_registration import ITUserRegistration
from mora.graphapi.model_registration import KLERegistration
from mora.graphapi.model_registration import LeaveRegistration
from mora.graphapi.model_registration import ManagerRegistration
from mora.graphapi.model_registration import OrganisationUnitRegistration
from mora.graphapi.model_registration import OwnerRegistration
from mora.graphapi.model_registration import PersonRegistration
from mora.graphapi.model_registration import RelatedUnitRegistration
from mora.graphapi.model_registration import RoleBindingRegistration
from mora.graphapi.mutators import Mutation
from mora.graphapi.owner_entities import OWNER_ENTITIES
from mora.graphapi.query import Query
from mora.graphapi.rbac_map import ADMIN_MAP
from mora.graphapi.rbac_map import PUBLIC_FIELDS
from mora.graphapi.rbac_map import RBAC_MAP
from mora.graphapi.types import CPR_SCALAR
from mora.graphapi.types import CURSOR_SCALAR
from mora.graphapi.types import INT_SCALAR
from mora.graphapi.types import Cursor
from mora.graphapi.version import Version
from mora.log import canonical_gql_context
from mora.util import CPR
from mora.util import ensure_list

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo

logger = get_logger()


def _create_info_from_raw(raw_info: GraphQLResolveInfo) -> "MOInfo":
    """Create a strawberry Info from raw GraphQLResolveInfo.

    Extensions only ever receive graphql-core's info, see
    https://github.com/strawberry-graphql/strawberry/pull/1447
    """
    # Get the strawberry schema from the GraphQL schema
    schema = raw_info.schema._strawberry_schema  # type: ignore

    # Get the strawberry field definition (may not exist for introspection fields)
    strawberry_field = None
    if raw_info.field_name in raw_info.parent_type.fields:
        field_def = raw_info.parent_type.fields[raw_info.field_name]
        strawberry_field = field_def.extensions.get("strawberry-definition")

    # Create Info using the schema's configured info class
    return schema.config.info_class(_raw_info=raw_info, _field=strawberry_field)


def add_exception_extension(
    error: GraphQLError, settings: config.Settings
) -> StrawberryGraphQLError:
    extensions = {}
    if isinstance(error.original_error, HTTPException):
        extensions["error_context"] = jsonable_encoder(error.original_error.detail)
        # Log errors like http_exception_handler in mora/app.py
        if not settings.is_production():
            stack = "".join(traceback.format_exception(error.original_error))
            logger.info("http_exception", stack=stack)

    return StrawberryGraphQLError(
        extensions=extensions,
        nodes=error.nodes,
        source=error.source,
        positions=error.positions,
        path=error.path,
        original_error=error.original_error,
        message=error.message,
    )


class LogContextExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        canonical_gql_context()["query"] = self.execution_context.query
        if self.execution_context.operation_name:  # pragma: no cover
            canonical_gql_context()["name"] = self.execution_context.operation_name
        if self.execution_context.variables:
            canonical_gql_context()["vars"] = self.execution_context.variables
        yield
        if self.execution_context.pre_execution_errors:
            canonical_gql_context()["errors"] = (
                self.execution_context.pre_execution_errors
            )


class RuntimeContextExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        start_time = time.perf_counter()
        yield
        stop_time = time.perf_counter()
        canonical_gql_context()["operation_time"] = stop_time - start_time


class ExtendedErrorFormatExtension(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        yield
        result = self.execution_context.result
        if result and hasattr(result, "errors") and result.errors is not None:
            settings = self.execution_context.context.settings
            result.errors = [
                add_exception_extension(error, settings) for error in result.errors
            ]


class RollbackOnError(SchemaExtension):
    async def on_operation(self) -> AsyncIterator[None]:
        yield
        result = self.execution_context.result
        if result and hasattr(result, "errors") and result.errors is not None:
            await get_session().rollback()


class IntrospectionQueryCacheExtension(SchemaExtension):
    cache: dict[tuple[Schema, str | None], ExecutionResult | None] = {}

    def on_execute(self) -> AsyncIteratorOrIterator[None]:  # type: ignore
        """Cache GraphQL introspection query, which otherwise takes 5-10s to execute.

        Based on the "In memory cached execution" example from
        https://strawberry.rocks/docs/guides/custom-extensions.
        """
        execution_context = self.execution_context
        cache_key = (execution_context.schema, execution_context.query)
        if (
            execution_context.operation_name == "IntrospectionQuery"
            and not execution_context.variables
        ):
            with suppress(KeyError):  # pragma: no cover
                execution_context.result = self.cache[cache_key]
        yield
        self.cache.setdefault(cache_key, execution_context.result)


class IsAuthenticatedExtension(SchemaExtension):
    """Schema-level extension that requires authentication for all GraphQL operations."""

    async def on_operation(self) -> AsyncIterator[None]:
        context = self.execution_context.context
        try:
            await context.get_token()
        except Exception as e:
            raise GraphQLError("User is not authenticated") from e
        yield


# A policy takes the resolver info and arguments, and returns whether it
# grants access to the field.
Policy = Callable[[GraphQLResolveInfo, dict[str, Any]], Awaitable[bool]]


async def introspection_policy(
    info: GraphQLResolveInfo, kwargs: dict[str, Any]
) -> bool:
    """Allow access to introspection for all users."""
    return info.field_name in (
        "__typename",
        "__schema",
        "__type",
    ) or is_introspection_type(info.parent_type)


async def no_role_required_policy(
    info: GraphQLResolveInfo, kwargs: dict[str, Any]
) -> bool:
    """Allow access to fields which are explicitly listed in `PUBLIC_FIELDS`."""
    return (info.parent_type.name, info.field_name) in PUBLIC_FIELDS


async def reader_policy(
    info: GraphQLResolveInfo,
    kwargs: dict[str, Any],
) -> bool:
    """Allow access if the field requires the `reader` role and the token has it."""
    token = await info.context.get_token()
    if "reader" not in token.realm_access.roles:
        return False
    return (info.parent_type.name, info.field_name) in RBAC_MAP


async def admin_policy(
    info: GraphQLResolveInfo,
    kwargs: dict[str, Any],
) -> bool:
    """Allow access if the field requires the `admin` role and the token has it."""
    token = await info.context.get_token()
    if "admin" not in token.realm_access.roles:
        return False
    return (info.parent_type.name, info.field_name) in ADMIN_MAP


def _actor_filter(token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor.

    With `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configured, the
    actor is the employee holding the token's uuid as an external id in that
    IT system; otherwise the employee with the token's uuid itself.
    """
    # A token with no uuid never gets this far, see `owner_policy`
    assert token.uuid is not None
    it_system = config.get_settings().keycloak_rbac_authoritative_it_system_for_owners
    if it_system is not None:
        return EmployeeFilter(
            ituser=ITUserFilter(
                itsystem=ITSystemFilter(uuids=[it_system]),
                external_ids=[str(token.uuid)],
            )
        )
    return EmployeeFilter(uuids=[token.uuid])


async def owner_policy(info: GraphQLResolveInfo, kwargs: dict[str, Any]) -> bool:
    """Allow access if the user is the owner of the accessed resources."""
    token = await info.context.get_token()
    token_roles = token.realm_access.roles

    if "owner" not in token_roles:
        return False

    # A token carrying no uuid names no employee, so it owns nothing
    if token.uuid is None:
        return False

    if info.operation.operation is not OperationType.MUTATION:
        return False

    if "input" not in kwargs:
        return False

    if info.field_name not in OWNER_ENTITIES:
        return False
    collection, permission_type = OWNER_ENTITIES[info.field_name]

    input = [SimpleNamespace(**item) for item in ensure_list(kwargs["input"])]

    # Import here to avoid circular imports 🙂👍
    from mora.auth.keycloak.rbac import check_owner
    from mora.auth.keycloak.uuid_extractor import get_entities_graphql

    moinfo = _create_info_from_raw(info)
    actor = _actor_filter(token)
    checks = [
        check
        async for check in get_entities_graphql(
            moinfo, actor, input, collection, permission_type
        )
    ]
    with suppress(AuthorizationError):
        await check_owner(moinfo, checks)
        return True

    return False


POLICIES: list[Policy] = [
    introspection_policy,
    no_role_required_policy,
    reader_policy,
    admin_policy,
    owner_policy,
]


async def _enforce_pbac(
    info: GraphQLResolveInfo,
    kwargs: dict[str, Any],
) -> None:
    """Check `POLICIES` for *info* and raise `GraphQLError` if none allow access.

    Policies are checked one by one, and access is granted as soon as any
    policy allows it.
    """
    for policy in POLICIES:
        if await policy(info, kwargs):
            return
    raise GraphQLError("No policy approved the access")


class RBACExtension(SchemaExtension):
    """Schema-level extension that enforces PBAC for every field.

    Each field access is checked against the policies in `POLICIES`, one by
    one, until a policy allows access.

    Access is rejected by default: every field must be listed in
    `PUBLIC_FIELDS` or have a requirement in `RBAC_MAP` or `ADMIN_MAP`.
    """

    async def resolve(  # type: ignore[override]
        self,
        next_: Callable[..., Any],
        root: Any,
        info: GraphQLResolveInfo,
        **kwargs: dict[str, Any],
    ) -> Any:
        await _enforce_pbac(info, kwargs)
        return await await_maybe(next_(root, info, **kwargs))


@cache
def get_schema(version: Version) -> CustomSchema:
    """Instantiate Strawberry Schema."""
    return CustomSchema(
        version=version,
        query=Query,
        mutation=Mutation,
        types=[
            DefaultAddress,
            DARAddress,
            MultifieldAddress,
            SpecialActor,
            UnknownActor,
            # Concrete registration types
            AddressRegistration,
            AssociationRegistration,
            ClassRegistration,
            PersonRegistration,
            EngagementRegistration,
            FacetRegistration,
            ITSystemRegistration,
            ITUserRegistration,
            KLERegistration,
            LeaveRegistration,
            ManagerRegistration,
            OwnerRegistration,
            OrganisationUnitRegistration,
            RelatedUnitRegistration,
            RoleBindingRegistration,
        ],
        extensions=[
            StarletteContextExtension,
            IsAuthenticatedExtension,
            RBACExtension,
            LogContextExtension,
            RuntimeContextExtension,
            RollbackOnError,
            ExtendedErrorFormatExtension,
            IntrospectionQueryCacheExtension,
        ],
        config=StrawberryConfig(
            # Automatic camelCasing disabled because under_score style is simply better
            #
            # See: An Eye Tracking Study on camelCase and under_score Identifier Styles
            # Excerpt:
            #   Although, no difference was found between identifier styles with respect
            #   to accuracy, results indicate a significant improvement in time and lower
            #   visual effort with the underscore style.
            #
            # Additionally, it preserves the naming of the underlying Python functions.
            auto_camel_case=False,
            scalar_map={
                CPR: CPR_SCALAR,
                Cursor: CURSOR_SCALAR,
                EventToken: EVENT_TOKEN_SCALAR,
                PositiveInt: INT_SCALAR,
                UploadFile: UploadDefinition,
            },
        ),
    )
