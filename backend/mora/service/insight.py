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

from starlette.responses import StreamingResponse

from structlog import get_logger
from .. import config


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

    if not directory.is_dir():
        logger.error("No file directory found in ", directory=directory)
        return []

    if q == ["all"]:
        return [
            json.load(open(directory / file.name))
            for file in directory.iterdir()
            if (directory / file.name).is_file()
        ]
    else:
        return [
            json.load(open(directory / query_file))
            for query_file in q
            if (directory / query_file).is_file()
        ]


@router.get("/insight/files")
async def get_insight_filenames() -> List[str]:
    """Lists all available files"""
    export_dir = config.get_settings().query_export_dir
    directory = Path(export_dir) / "json_reports"

    if not directory.is_dir():
        logger.error("No file directory found in ", directory=directory)
        return []

    return [file.name for file in directory.iterdir() if file.is_file()]


@router.get("/insight/download", response_class=StreamingResponse)
async def download_csv():
    """Exports locally stored JSONs as a streamed ZIP of CSVs"""
    export_dir = config.get_settings().query_export_dir
    directory = Path(export_dir) / "json_reports"

    if not directory.is_dir():
        logger.error("No file directory found in ", directory=directory)

    list_of_files = list(filter(lambda file: file.is_file(), directory.iterdir()))

    def read_jsonfile_from_disc(file: Path) -> Dict:
        return json.load(open(file))

    list_of_json = map(read_jsonfile_from_disc, list_of_files)

    def json_to_csv(content: Dict[str, Any]) -> StringIO:
        output = StringIO()

        content_fields = content["schema"]["fields"]
        fieldnames = [field["name"] for field in content_fields]

        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in content["data"]:
            writer.writerow(row)

        return output

    list_of_csv = map(json_to_csv, list_of_json)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for file, csv_file in zip(list_of_files, list_of_csv):
            zip_file.writestr(file.stem + ".csv", csv_file.getvalue())
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"content-disposition": "attachment; filename=insights.zip"},
    )
