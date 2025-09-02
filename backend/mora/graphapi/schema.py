# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
from collections.abc import AsyncIterator
from collections.abc import Callable
from collections.abc import Iterator
from contextlib import contextmanager
from contextlib import suppress
from functools import cache
from typing import Any

import strawberry
from fastapi.encoders import jsonable_encoder
from graphql import ExecutionResult
from graphql import GraphQLError
from graphql import GraphQLResolveInfo
from graphql.pyutils import Path
from opentelemetry import trace
from pydantic import PositiveInt
from strawberry import Schema
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.schema.config import StrawberryConfig
from strawberry.types import ExecutionContext
from strawberry.utils.await_maybe import AsyncIteratorOrIterator
from strawberry.utils.await_maybe import AwaitableOrValue
from strawberry.utils.await_maybe import await_maybe
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


class OpenTelemetryExtension(SchemaExtension):
    """Based on Strawberry's upstream OpenTelemetryExtension, but with proper nesting of spans.

    https://github.com/strawberry-graphql/strawberry/blob/58ea8c9a8d880ecdf86629bc8e521ae305fd4d10/strawberry/extensions/tracing/opentelemetry.py
    https://github.com/strawberry-graphql/strawberry/issues/3788
    """

    def __init__(self, *, execution_context: ExecutionContext) -> None:
        super().__init__(execution_context=execution_context)
        self.tracer = trace.get_tracer("strawberry")
        self.spans: dict[Path | None, trace.Span] = {}

    def on_operation(self) -> Iterator[None]:
        with self.tracer.start_as_current_span(
            name=f"GraphQL Operation: {self.execution_context.operation_name}",
        ):
            yield

    def on_validate(self) -> Iterator[None]:
        with self.tracer.start_as_current_span(
            name="GraphQL Validate",
        ):
            yield

    def on_parse(self) -> Iterator[None]:
        with self.tracer.start_as_current_span(
            name="GraphQL Parse",
        ):
            yield

    def on_execute(self) -> Iterator[None]:
        with self.tracer.start_as_current_span(
            name="GraphQL Execute",
        ) as span:
            # Use this span as the parent for resolve() spans
            self.spans[None] = span
            yield

    @contextmanager
    def _use_span(self, path: Path | None) -> Iterator[trace.Span]:
        # The GraphQL path looks something like
        #
        # ['engagements', 'objects', 5, 'validities', 2, 'org_unit', 0, 'name'],
        #
        # where strings represent GraphQL field names and integers represent
        # entries in a list. Strawberry won't call resolve() for list entries
        # (when the rightmost path component is an integer), so we CANNOT
        # assume that parent spans are created before their children.

        # Return spans that already exist without wrapping in
        # start_as_current_span(). This avoids starting and ending the same
        # span multiple times, which is illegal.
        with suppress(KeyError):
            yield self.spans[path]
            return
        assert path is not None  # self.spans[None] is inserted in on_execute()

        # If the parent is a field name (string), it was already created and
        # this call will simply return it from the cache. Otherwise, if the
        # parent is a list entry (integer), the call will create a new span
        # **and start it**. Since we don't have any lifecycle hooks without
        # calls to resolve(), we immediately close it.
        with self._use_span(path.prev) as parent_span:
            pass

        # Wrap new spans in start_as_current_span(), tying our own
        # contextmanager lifecycle to the span's.
        with self.tracer.start_as_current_span(
            name=f"GraphQL Resolve: {path.key}",
            context=trace.set_span_in_context(span=parent_span),
            attributes={
                "graphql.path": ".".join(map(str, path.as_list())),
            },
        ) as span:
            self.spans[path] = span
            yield span

    async def resolve(
        self,
        _next: Callable,
        root: Any,
        info: GraphQLResolveInfo,
        *args: str,
        **kwargs: Any,
    ) -> AwaitableOrValue[object]:
        with self._use_span(info.path):
            return await await_maybe(_next(root, info, *args, **kwargs))


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
        ],
        extensions=[
            OpenTelemetryExtension,
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
