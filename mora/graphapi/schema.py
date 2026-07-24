# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
from collections.abc import AsyncIterator
from collections.abc import Callable
from contextlib import suppress
from functools import cache
from typing import Any
from typing import cast

import strawberry
from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from graphql import GraphQLResolveInfo
from pydantic import PositiveInt
from strawberry import Schema
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
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
from mora.graphapi.query import Query
from mora.graphapi.types import CPRType
from mora.graphapi.version import Version
from mora.log import canonical_gql_context
from mora.util import CPR

logger = get_logger()


def add_exception_extension(error: GraphQLError) -> StrawberryGraphQLError:
    extensions = {}
    if isinstance(error.original_error, HTTPException):
        extensions["error_context"] = jsonable_encoder(error.original_error.detail)
        # Log errors like http_exception_handler in mora/app.py
        settings = config.get_settings()
        if not settings.is_production():
            logger.info(
                "http_exception",
                stack=error.original_error.stack,
                traceback=error.original_error.traceback,
            )

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
            result.errors = list(map(add_exception_extension, result.errors))


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
    """Allow access if an active DB policy grants this (type, field).

    Policy-based access control is the *only* authorization path: access to a
    field is allowed iff the calling actor has an active policy with a rule
    granting the accessed GraphQL `(type, field)`. The bootstrapped built-in
    policies define all access -- Introspection and Public (both bound to every
    actor), Legacy (role-based), Owner, Reader and Administrator. There is no
    static map and no reject/allow logic in code beyond this single delegation.
    """
    # Deferred imports to avoid a circular import at module load.
    from strawberry.types.arguments import convert_arguments
    from strawberry.types.info import Info as StrawberryInfo

    from mora.graphapi.context import MOInfo
    from mora.graphapi.policies import actor_grants_field

    token = await info.context.get_token()

    # `actor_grants_field` (and the resolver predicates its entity filters call)
    # expect a Strawberry `Info`, whose `.schema` is the `CustomSchema`. Rebuild
    # one from the raw `GraphQLResolveInfo` using the field's Strawberry
    # definition (stored on the graphql field's extensions). Introspection
    # meta-fields (`__typename`, `__schema`, `__type`) are absent from
    # `parent_type.fields`, and introspection-type fields (`__Type.name`, ...)
    # carry no Strawberry definition; for those there are no arguments to convert
    # and no entity filter can apply, so the raw info (only `.context.session` is
    # read) is passed through directly.
    gql_field = info.parent_type.fields.get(info.field_name)
    strawberry_field = (
        gql_field.extensions.get("strawberry-definition") if gql_field else None
    )
    if strawberry_field is None:
        return await actor_grants_field(
            cast(MOInfo, info),
            token,
            info.parent_type.name,
            info.field_name,
            arguments={},
        )

    strawberry_info = cast(
        MOInfo, StrawberryInfo(_raw_info=info, _field=strawberry_field)
    )

    # Convert the raw graphql argument dict into the Strawberry input instances
    # the resolver itself would receive, so unset optional fields surface as
    # `UNSET` (which a policy entity filter reads as `null`) rather than being
    # absent from the dict -- matching how the mutator sees its `input`.
    schema = strawberry_info.schema
    arguments = convert_arguments(
        kwargs,
        strawberry_field.arguments,
        scalar_registry=schema.schema_converter.scalar_registry,
        config=schema.config,
    )
    return await actor_grants_field(
        strawberry_info,
        token,
        info.parent_type.name,
        info.field_name,
        arguments=arguments,
    )


async def _enforce_pbac(
    info: GraphQLResolveInfo,
    kwargs: dict[str, Any],
) -> None:
    """Raise `GraphQLError` unless a DB policy grants access to this field."""
    if not await pbac_policy(info, kwargs):
        raise GraphQLError("No policy approved the access")


class RBACExtension(SchemaExtension):
    """Schema-level extension that enforces access control for every field.

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
        ),
        scalar_overrides={
            CPR: CPRType,
            PositiveInt: strawberry.scalar(int),
        },
    )
