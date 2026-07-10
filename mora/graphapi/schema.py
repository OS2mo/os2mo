# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
from collections.abc import AsyncIterator
from collections.abc import Callable
from contextlib import suppress
from functools import cache
from types import SimpleNamespace
from typing import Any

import strawberry
from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from graphql import GraphQLResolveInfo
from graphql import is_introspection_type
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
from mora.graphapi.permissions import _check_rbac
from mora.graphapi.query import Query
from mora.graphapi.rbac_map import RBAC_MAP
from mora.graphapi.types import CPRType
from mora.graphapi.version import Version
from mora.log import canonical_gql_context
from mora.util import CPR
from mora.util import ensure_list

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


async def _enforce_rbac(
    info: GraphQLResolveInfo,
    kwargs: dict[str, Any],
) -> None:
    """Check the RBAC requirement for *info* and raise `GraphQLError` if unsatisfied."""
    parent_type_name = info.parent_type.name
    field_name = info.field_name
    # Introspection is available to all users
    if field_name in ("__typename", "__schema", "__type") or is_introspection_type(
        info.parent_type
    ):
        return
    # We expect all accesses to be described in the RBAC_MAP; anything else is
    # an error. test_rbac_map_covers_schema helps ensure everything is captured.
    requirement = RBAC_MAP[(parent_type_name, field_name)]
    if requirement is None:
        # The field is explicitly public: everyone is allowed access
        return
    role, collection, permission_type = requirement
    check_kwargs = kwargs
    if "input" in kwargs:
        check_kwargs = {
            **kwargs,
            "input": [SimpleNamespace(**item) for item in ensure_list(kwargs["input"])],
        }
    allowed = await _check_rbac(
        info,
        role,
        # TODO(#61411) remove along with the graphql_rbac flag.
        permission_type != "read",
        collection,
        permission_type,
        check_kwargs,
    )
    if allowed:
        return
    msg = f"User does not have required role: {role}"
    if collection is not None and permission_type is not None:
        msg = f"User does not have {permission_type}-access to {collection}"
    raise GraphQLError(msg)


class RBACExtension(SchemaExtension):
    """Schema-level extension that enforces RBAC for every field.

    The required role is looked up in `RBAC_MAP` by
    `(parent_type, field_name)`, replacing the per-field
    `gen_read_permission` / `gen_create_permission` / etc. declarations.

    Access is rejected by default: every field must have an entry in
    `RBAC_MAP`, either a requirement tuple or `None` for public fields.
    """

    async def resolve(  # type: ignore[override]
        self,
        next_: Callable[..., Any],
        root: Any,
        info: GraphQLResolveInfo,
        **kwargs: dict[str, Any],
    ) -> Any:
        await _enforce_rbac(info, kwargs)
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
