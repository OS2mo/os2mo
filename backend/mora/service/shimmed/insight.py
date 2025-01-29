# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import csv
import json
from asyncio import gather
from functools import partial
from io import BytesIO
from io import StringIO
from itertools import starmap
from operator import itemgetter
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from fastapi import Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic import Extra

from mora.graphapi.shim import execute_graphql
from mora.service.insight import router as insight_router

from .errors import handle_gql_error


@insight_router.get(
    "/insight/files",
    response_model=list[str],
    response_model_exclude_unset=True,
    responses={"500": {"description": "Directory does not exist"}},
)
async def get_insight_filenames() -> list[str]:
    """Lists all available files."""
    query = "query FilesQuery { files(filter: {file_store: INSIGHT}) { objects { file_name } } }"
    gql_response = await execute_graphql(query)
    handle_gql_error(gql_response)
    files = gql_response.data["files"]["objects"]
    return list(map(itemgetter("file_name"), files))


class Insight(BaseModel):
    """
    Attributes:
        title:
        data:
    """

    title: str
    data: list[int | str]

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid


@insight_router.get("/insight")
async def get_insight_data(q: list[str] | None = Query(["all"])) -> list[Insight]:
    """Loads data from a directory of JSONs and returns it as a list.

    Args:
        q: Enables the frontend to choose a specific file or show all files.

    Returns:
        List of Insight file models.
    """
    if q == ["all"]:
        query = """
        query FileQuery {
          files(filter: {file_store: INSIGHTS}) {
            objects {
              text_contents
            }
          }
        }
        """
        variables = {}
    else:
        query = """
        query FileQuery($file_names: [String!]) {
          files(filter: {file_store: INSIGHTS, file_names: $file_names}) {
            objects {
              text_contents
            }
          }
        }
        """
        variables = {"file_names": q}

    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    contents = response.data["files"]["objects"]
    jsons = map(json.loads, map(itemgetter("text_contents"), contents))
    return list(jsons)


def json_to_csv(json_data: dict[str, Any], fieldnames: list[str]) -> StringIO:
    output = StringIO()

    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(json_data["data"])

    return output


def extract_fieldnames(json_data: dict[str, Any]) -> list[str]:
    return [field["name"] for field in json_data["schema"]["fields"]]


@insight_router.get(
    "/insight/download",
    response_class=StreamingResponse,
    responses={"500": {"description": "Directory does not exist"}},
)
async def download_csv() -> StreamingResponse:
    """Exports locally stored JSONs as a streamed ZIP of CSVs."""
    query = """
    query FileQuery {
      files(filter: {file_store: INSIGHTS}) {
        objects {
          file_name
          text_contents
        }
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    contents = response.data["files"]["objects"]
    iter_of_files = map(Path, map(itemgetter("file_name"), contents))
    iter_of_json = map(json.loads, map(itemgetter("text_contents"), contents))
    iter_of_csv = (
        json_to_csv(json_file, extract_fieldnames(json_file))
        for json_file in iter_of_json
    )

    async def zip_writestr(zip_file: ZipFile, file: Path, csv_file: StringIO):
        zip_file.writestr(file.stem + ".csv", csv_file.getvalue().encode("utf-8-sig"))

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        zip_writestr_with_buffer = partial(zip_writestr, zip_file)
        tasks = starmap(zip_writestr_with_buffer, zip(iter_of_files, iter_of_csv))
        await gather(*tasks)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"content-disposition": "attachment; filename=insights.zip"},
    )
