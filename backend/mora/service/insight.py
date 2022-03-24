# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json
import csv

from zipfile import ZipFile
from io import StringIO, BytesIO
from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, Extra
from fastapi import APIRouter, Query
from pathlib import Path
from asyncio import gather
from itertools import starmap
from functools import partial

from starlette.responses import StreamingResponse

from structlog import get_logger
from .. import config, exceptions


router = APIRouter()
logger = get_logger()


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


@router.get("/insight")
async def get_insight_data(q: Optional[List[str]] = Query(["all"])) -> List[Insight]:
    """Loads data from a directory of JSONs and returns it as a list

    **param q:** Enables the frontend to choose a specific file or show all files
    """
    export_dir = config.get_settings().query_export_dir
    directory = Path(export_dir) / "json_reports"
    directory_exists(directory)

    if q == ["all"]:
        return [
            read_json_from_disc(path) for path in directory.iterdir() if path.is_file()
        ]
    else:
        return [
            read_json_from_disc(directory / query_file)
            for query_file in q
            if (directory / query_file).is_file()
        ]


@router.get(
    "/insight/files", responses={"500": {"description": "Directory does not exist"}}
)
async def get_insight_filenames() -> List[str]:
    """Lists all available files"""
    export_dir = config.get_settings().query_export_dir
    directory = Path(export_dir) / "json_reports"
    directory_exists(directory)

    return [path.name for path in directory.iterdir() if path.is_file()]


@router.get(
    "/insight/download",
    response_class=StreamingResponse,
    responses={"500": {"description": "Directory does not exist"}},
)
async def download_csv() -> StreamingResponse:
    """Exports locally stored JSONs as a streamed ZIP of CSVs"""
    export_dir = config.get_settings().query_export_dir
    directory = Path(export_dir) / "json_reports"
    directory_exists(directory)

    list_of_files = list(filter(lambda path: path.is_file(), directory.iterdir()))
    iter_of_json = map(read_json_from_disc, list_of_files)
    iter_of_csv = (
        json_to_csv(json_file, extract_fieldnames(json_file))
        for json_file in iter_of_json
    )

    async def zip_writestr(zip_file: ZipFile, file: Path, csv_file: StringIO):
        zip_file.writestr(file.stem + ".csv", csv_file.getvalue().encode("utf-8-sig"))

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        zip_writestr_with_buffer = partial(zip_writestr, zip_file)
        tasks = starmap(zip_writestr_with_buffer, zip(list_of_files, iter_of_csv))
        await gather(*tasks)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"content-disposition": "attachment; filename=insights.zip"},
    )


def read_json_from_disc(file: Path):
    return json.loads(file.read_text())


def json_to_csv(json_data: Dict[str, Any], fieldnames: List[str]) -> StringIO:
    output = StringIO()

    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(json_data["data"])

    return output


def extract_fieldnames(json_data: Dict[str, Any]) -> List[str]:
    return [field["name"] for field in json_data["schema"]["fields"]]


def directory_exists(directory: Path):
    if not directory.is_dir():
        logger.error("No file directory found in ", directory=directory)
        exceptions.ErrorCodes.E_DIR_NOT_FOUND(directory=str(directory))
