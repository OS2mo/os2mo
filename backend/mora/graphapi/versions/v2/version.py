# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from .query import Query
from ..v3.version import GraphQLSchema3
from ..v3.version import GraphQLVersion3


class GraphQLSchema2(GraphQLSchema3):
    query = Query


class GraphQLVersion2(GraphQLVersion3):
    """Latest versioned GraphQL API."""

    version = 2
    deprecation_date = date(2023, 2, 1)
    schema = GraphQLSchema2
