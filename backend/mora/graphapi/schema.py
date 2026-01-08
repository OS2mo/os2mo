# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
from collections.abc import AsyncIterator
from contextlib import suppress
from functools import cache

from mora.graphapi.versions.latest.schema import Address, Association, Class, Facet, Engagement, ITSystem, ITUser, KLE, Leave, Manager, OrganisationUnit, Owner, Employee, RelatedUnit, RoleBinding
from mora.graphapi.versions.latest.registration_types import AddressRegistration, AssociationRegistration, ClassRegistration, FacetRegistration, EngagementRegistration, ITSystemRegistration, ITUserRegistration, KLERegistration, LeaveRegistration, ManagerRegistration, OrganisationUnitRegistration, OwnerRegistration, PersonRegistration, RelatedUnitRegistration, RoleBindingRegistration
import strawberry
from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from pydantic import PositiveInt
from strawberry import Schema
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.schema.config import StrawberryConfig
from strawberry.utils.await_maybe import AsyncIteratorOrIterator
from structlog import get_logger

from mora import config
from mora.db import get_session
from mora.exceptions import HTTPException
from mora.graphapi.custom_schema import CustomSchema
from mora.graphapi.middleware import StarletteContextExtension
from mora.graphapi.version import Version
from mora.graphapi.versions.latest.actor import SpecialActor
from mora.graphapi.versions.latest.actor import UnknownActor
from mora.graphapi.versions.latest.mutators import Mutation
from mora.graphapi.versions.latest.query import Query
from mora.graphapi.versions.latest.schema import DARAddress
from mora.graphapi.versions.latest.schema import DefaultAddress
from mora.graphapi.versions.latest.schema import MultifieldAddress
from mora.graphapi.versions.latest.types import CPRType
from mora.log import canonical_gql_context
from mora.util import CPR

logger = get_logger()


def add_exception_extension(error: GraphQLError) -> StrawberryGraphQLError:
    extensions = {}
    if isinstance(error.original_error, HTTPException):
        extensions["error_context"] = jsonable_encoder(error.original_error.detail)
        # Log errors like http_exception_handler in backend/mora/app.py
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
        if self.execution_context.errors:
            canonical_gql_context()["errors"] = self.execution_context.errors


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
            # Concrete validity types
            Address,
            Association,
            Class,
            Employee,
            Engagement,
            Facet,
            ITSystem,
            ITUser,
            KLE,
            Leave,
            Manager,
            Owner,
            OrganisationUnit,
            RelatedUnit,
            RoleBinding,
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
