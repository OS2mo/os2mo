# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..v20.version import GraphQLVersion as NextGraphQLVersion


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 19 of the GraphQL Schema.

    Prior to this version, facets ignored start_date and end_date filtering. This is no
    longer the case.
    """


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 19."""

    version = 19
    schema = GraphQLSchema
