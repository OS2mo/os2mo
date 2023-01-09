# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from ..v2.version import GraphQLSchema2
from ..v2.version import GraphQLVersion2
from .schema import OrganisationUnit


class GraphQLSchema1(GraphQLSchema2):
    """First pinned version of the GraphQL Schema.

    Implements backwards-compatibility of org unit parent, making it return an optional
    list of exactly one element.
    """

    # Override organisation unit object type to object with legacy behaviour
    types = [OrganisationUnit]


class GraphQLVersion1(GraphQLVersion2):
    """First pinned version of the GraphQL API."""

    version = 1
    deprecation_date = date(2023, 3, 1)
    schema = GraphQLSchema1
