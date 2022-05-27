# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import csv
import json
from asyncio import gather
from functools import partial
from io import BytesIO
from io import StringIO
from itertools import starmap
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from zipfile import ZipFile

from fastapi import APIRouter
from starlette.responses import StreamingResponse
from structlog import get_logger

from .. import config
from .. import exceptions


router = APIRouter()
logger = get_logger()


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
