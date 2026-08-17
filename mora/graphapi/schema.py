# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
import traceback
from collections.abc import AsyncIterator
from collections.abc import Callable
from contextlib import suppress
from functools import cache
from typing import TYPE_CHECKING
from typing import Any

from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from graphql import GraphQLResolveInfo
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
from mora.graphapi.policies import entity_filter_grants
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import check_condition
from mora.graphapi.query import Query
from mora.graphapi.types import CPR_SCALAR
from mora.graphapi.types import CURSOR_SCALAR
from mora.graphapi.types import INT_SCALAR
from mora.graphapi.types import Cursor
from mora.graphapi.version import Version
from mora.log import canonical_gql_context
from mora.util import CPR

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


async def pbac_policy(info: GraphQLResolveInfo, kwargs: dict[str, Any]) -> bool:
    """Allow access if an active DB policy grants this (type, field)."""
    token = await info.context.get_token()
    index = await info.context.dataloaders.policy_loader.load(
        frozenset(token.realm_access.roles)
    )
    type, field = info.parent_type.name, info.field_name
    # A rule matches this exact (type, field) or a wildcard in either component
    relevant_rules = (
        index.get((type, field), [])
        + index.get((type, "*"), [])
        + index.get(("*", field), [])
        + index.get(("*", "*"), [])
    )
    if not relevant_rules:
        return False
    # Check unfiltered rules first, as entity filters are expensive
    unfiltered = [condition for condition, filter in relevant_rules if not filter]
    # A rule without a condition grants outright, so no CEL is needed
    if "" in unfiltered:
        return True
    # A condition may read the field's own arguments, just as a filter may, so
    # both are evaluated against the one activation. An upload is named by its
    # filename alone: encoding it would read the payload out from under the
    # resolver, which has yet to read it itself
    activation = build_activation(
        token,
        jsonable_encoder(
            kwargs, custom_encoder={UploadFile: lambda file: file.filename}
        ),
    )
    if any(check_condition(condition, activation) for condition in unfiltered):
        return True

    # Only the filtered rules are left
    filtered = [(condition, filter) for condition, filter in relevant_rules if filter]
    # Keep only rules whose condition passes
    applicable = [
        filter
        for condition, filter in filtered
        if check_condition(condition, activation)
    ]
    if not applicable:
        return False
    # A policy is handed graphql-core's info, but the entity filters (and the
    # resolver predicates they call) want Strawberry's
    strawberry_info = _create_info_from_raw(info)
    # Introspection fields have no Strawberry field definition, and a filter
    # cannot run without one, so bail out
    if strawberry_info._field is None:
        return False
    for filter in applicable:
        if await entity_filter_grants(filter, strawberry_info, activation):
            return True
    return False


class PBACExtension(SchemaExtension):
    """Schema-level extension that enforces PBAC for every field.

    Every field access is checked by `pbac_policy` against the database-managed
    policies. Access is rejected by default: a field granted by no policy raises
    `"No policy approved the access"`.
    """

    async def resolve(  # type: ignore[override]
        self,
        next_: Callable[..., Any],
        root: Any,
        info: GraphQLResolveInfo,
        **kwargs: dict[str, Any],
    ) -> Any:
        if not await pbac_policy(info, kwargs):
            raise GraphQLError("No policy approved the access")
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
            PBACExtension,
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
