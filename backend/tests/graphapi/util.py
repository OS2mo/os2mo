# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Optional

from more_itertools import flatten
from strawberry.types import ExecutionResult

from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.main import get_schema
from tests.util import patch_is_graphql
from tests.util import patch_query_args


async def execute(query: str, values: Optional[dict] = None) -> ExecutionResult:
    """Execute a GraphQL query with necessary mocks and dataloaders."""
    values = values or {}

    schema = get_schema()
    with patch_query_args():
        with patch_is_graphql(True):
            loaders = await get_loaders()
            result = await schema.execute(
                query, variable_values=values, context_value=loaders
            )
    return result


def flatten_data(resp_dict: dict[str, Any]):
    return list(flatten([d["objects"] for d in resp_dict]))
