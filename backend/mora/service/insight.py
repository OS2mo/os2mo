# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json

from typing import List, Union, Optional
from pydantic import BaseModel, Extra
from fastapi import APIRouter, Query
from pathlib import Path

from .. import exceptions, config

router = APIRouter()


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
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    if q == ["all"]:
        return [
            json.load(open(directory / filename.name))
            for filename in directory.iterdir()
            if (directory / filename.name).is_file()
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
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    return [filename.name for filename in directory.iterdir() if filename.is_file()]
