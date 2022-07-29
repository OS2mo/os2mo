# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from mora.util import CPR
from .dataloaders import get_loaders
from .mutation import Mutation
from .query import Query
from .types import CPRType
from ..base import BaseGraphQLSchema
from ..base import BaseGraphQLVersion


class LatestGraphQLSchema(BaseGraphQLSchema):
    query = Query
    mutation = Mutation

    scalar_overrides = {
        CPR: CPRType,  # type: ignore
    }


class LatestGraphQLVersion(BaseGraphQLVersion):
    """TODO."""

    schema = LatestGraphQLSchema

    @classmethod
    async def get_context(cls) -> dict[str, Any]:
        loaders = await get_loaders()
        return {**loaders}
