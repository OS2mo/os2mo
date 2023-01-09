# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from ..v3.version import GraphQLSchema3
from ..v3.version import GraphQLVersion3
from .query import Query


class GraphQLSchema2(GraphQLSchema3):
    """Version 2 of the GraphQL Schema.

    Implements backwards-compatibility of healths, making it a non-paged endpoint
    like the original implementation.
    """

    query = Query


class GraphQLVersion2(GraphQLVersion3):
    """Latest GraphQL version."""

    version = 2
    deprecation_date = date(2023, 4, 1)
    schema = GraphQLSchema2
