# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..v20.version import GraphQLVersion as NextGraphQLVersion


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 19 of the GraphQL Schema.

    Version 20 introduced a breaking change so facets no longer ignore start_date and
    end_date filtering.
    Version 19 ensures that the old functionality is still available.
    """


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 19."""

    version = 19
    schema = GraphQLSchema
