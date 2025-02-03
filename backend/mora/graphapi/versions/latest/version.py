# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import strawberry
from pydantic import PositiveInt

from mora.graphapi.versions.latest.schema import DARAddress
from mora.graphapi.versions.latest.schema import DefaultAddress
from mora.graphapi.versions.latest.schema import MultifieldAddress
from mora.util import CPR

from ..base import BaseGraphQLSchema
from ..base import BaseGraphQLVersion
from .mutators import Mutation as LatestMutation
from .query import Query as LatestQuery
from .types import CPRType


class LatestGraphQLSchema(BaseGraphQLSchema):
    """Latest GraphQL Schema."""

    query = LatestQuery
    mutation = LatestMutation

    types = [DefaultAddress, DARAddress, MultifieldAddress]

    scalar_overrides = {
        CPR: CPRType,
        PositiveInt: strawberry.scalar(int),
    }


class LatestGraphQLVersion(BaseGraphQLVersion):
    """Latest GraphQL API version.

    The latest version is never explicitly versioned or exposed directly. Clients should
    always refer and pin themselves to a specific version, which is available as the
    latest `vN` version package, inheriting from this class without modifications.
    When a new breaking change must be introduced to the GraphQL schema, the change is
    made in `latest` and the `vN` package is changed to be an adapter which maintains
    backwards-compatibility. A new `vN+1` package is created to expose latest.

    As an example, see the merge request for the first breaking change:
    https://git.magenta.dk/rammearkitektur/os2mo/-/merge_requests/1184
    """

    # Even though the latest version isn't exposed, we use it internally for the
    # service API shims. Therefore, we must define a version number to avoid
    # having None-checks everywhere.
    version = 1000
    schema = LatestGraphQLSchema
