# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import wraps
from textwrap import dedent
from typing import Any

import strawberry
from starlette_context import context
from strawberry.types import Info

from mora.util import now

from ..latest.audit import AuditLog as AuditLogLatest
from ..latest.audit import AuditLogFilter as AuditLogFilterLatest
from ..latest.audit import AuditLogModel
from ..latest.audit import audit_log_resolver
from ..latest.filters import gen_filter_table
from ..latest.paged import CursorType
from ..latest.paged import LimitType
from ..latest.paged import Paged
from ..latest.paged import PageInfo
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.permissions import gen_read_permission
from ..latest.types import Cursor
from ..v18.version import GraphQLVersion as NextGraphQLVersion


class PagedResolver:
    async def resolve(
        self,
        *args: Any,
        limit: LimitType = None,
        cursor: CursorType = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError


def to_paged(  # type: ignore
    resolver: PagedResolver,
    result_transformer: Callable[[PagedResolver, Any], list[Any]] | None = None,
):
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver.resolve)
    async def resolve_response(*args, limit: LimitType, cursor: CursorType, **kwargs):  # type: ignore
        if limit and cursor is None:
            cursor = Cursor(
                offset=0,
                registration_time=str(now()),
            )

        result = await resolver.resolve(*args, limit=limit, cursor=cursor, **kwargs)

        end_cursor: CursorType = None
        if limit and cursor is not None:
            end_cursor = Cursor(
                offset=cursor.offset + limit,
                registration_time=cursor.registration_time,
            )
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(resolver, result),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response


@strawberry.input(description="Audit log filter.")
class AuditLogFilter(AuditLogFilterLatest):
    models: list[str] | None = strawberry.field(  # type: ignore
        default=None,
        description=dedent(
            """\
            Filter audit events by their model type.

            Can be used to select all reads for a data type.

            Can be one of:
            * `"AuditLog"`
            * `"Bruger"`
            * `"Facet"`
            * `"ItSystem"`
            * `"Klasse"`
            * `"Organisation"`
            * `"OrganisationEnhed"`
            * `"OrganisationFunktion"`
            """
        )
        + gen_filter_table("models"),
    )


@strawberry.type(
    description=dedent(
        """\
        AuditLog entry.

        Mostly useful for auditing purposes seeing when data-reads were done and by whom.
        """
    )
)
class AuditLog(AuditLogLatest):
    @strawberry.field(  # type: ignore
        description=dedent(
            """\
        Model of the modified entity.

        Can be one of:
        * `"AuditLog"`
        * `"Bruger"`
        * `"Facet"`
        * `"ItSystem"`
        * `"Klasse"`
        * `"Organisation"`
        * `"OrganisationEnhed"`
        * `"OrganisationFunktion"`
        """
        )
    )
    async def model(self, root: AuditLogLatest) -> str:
        try:
            return AuditLogModel(root.model).value
        except ValueError:
            return root.model  # type: ignore


class AuditLogResolver(PagedResolver):
    # TODO: Implement using a dataloader
    async def resolve(  # type: ignore[override]
        self,
        info: Info,
        filter: AuditLogFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ) -> list[AuditLog]:
        # Unaffected query, only new behavior if filter.models is set
        if filter is None or filter.models is None:
            return await audit_log_resolver(  # type: ignore
                info=info, filter=filter, limit=limit, cursor=cursor
            )

        # Convert models to latest format
        models = []
        for model in filter.models:
            try:
                models.append(AuditLogModel(model))
            except ValueError:
                # Simply ignore illegal values
                pass

        # Construct new filter
        new_filter = AuditLogFilterLatest(
            ids=filter.ids,
            uuids=filter.uuids,
            actors=filter.actors,
            models=models,
            start=filter.start,
            end=filter.end,
        )
        return await audit_log_resolver(  # type: ignore
            info=info, filter=new_filter, limit=limit, cursor=cursor
        )


@strawberry.type(description="Entrypoint for all read-operations")
class Query(NextGraphQLVersion.schema.query):  # type: ignore[name-defined]
    auditlog: Paged[AuditLog] = strawberry.field(
        resolver=to_paged(AuditLogResolver()),
        description=dedent(
            """\
            Get a list of audit events.

            Mostly useful for auditing purposes seeing when data was read and by whom.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("auditlog")],
    )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 17 of the GraphQL Schema.

    Version 18 introduced a breaking change to the `auditlog`'s `model` filter type
    such that it is now an enum exposing the potential values directly, rather than
    only exposing them in textual documentation.
    Version 17 ensures that the old functionality is still available.
    """

    query = Query


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 17."""

    version = 17
    schema = GraphQLSchema
