# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from operator import itemgetter
from typing import List

from .errors import handle_gql_error
from mora.graphapi.shim import execute_graphql
from mora.service.insight import router as insight_router


@insight_router.get(
    "/insight/files",
    response_model=List[str],
    response_model_exclude_unset=True,
    responses={"500": {"description": "Directory does not exist"}},
)
async def get_insight_filenames() -> List[str]:
    """Lists all available files."""
    query = "query FilesQuery { files(file_store: INSIGHT) { file_name } }"
    gql_response = await execute_graphql(query)
    handle_gql_error(gql_response)
    files = gql_response.data["files"]
    return list(map(itemgetter("file_name"), files))
