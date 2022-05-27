# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
from operator import itemgetter
from typing import List
from typing import Optional
from typing import Union

from fastapi import Query
from pydantic import BaseModel
from pydantic import Extra

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


class Insight(BaseModel):
    """
    Attributes:
        title:
        data:
    """

    title: str
    data: List[Union[int, str]]

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid


@insight_router.get("/insight")
async def get_insight_data(q: Optional[List[str]] = Query(["all"])) -> List[Insight]:
    """Loads data from a directory of JSONs and returns it as a list.

    Args:
        q: Enables the frontend to choose a specific file or show all files.

    Returns:
        List of Insight file models.
    """
    if q == ["all"]:
        query = """
        query FileQuery {
          files(file_store: INSIGHTS) {
            text_contents
          }
        }
        """
        variables = {}
    else:
        query = """
        query FileQuery($file_names: [String!]) {
          files(file_store: INSIGHTS, file_names: $file_names) {
            text_contents
          }
        }
        """
        variables = {"file_names": q}

    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    contents = response.data["files"]
    jsons = map(json.loads, map(itemgetter("text_contents"), contents))
    return list(jsons)
