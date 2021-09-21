# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json
import os

from typing import List, Union, Optional
from pydantic import BaseModel, Extra
from fastapi import APIRouter, Query

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
    directory = config.get_settings().query_export_dir
    if not os.path.isdir(directory):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    if q == ["all"]:
        return [
            json.load(open(os.path.join(directory, filename)))
            for filename in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, filename))
        ]
    else:
        return [
            json.load(open(os.path.join(directory, filename)))
            for filename in q
            if os.path.isfile(os.path.join(directory, filename))
        ]


@router.get("/insight/files")
async def get_insight_filenames() -> List[str]:
    """Lists all available files"""
    directory = config.get_settings().query_export_dir
    if not os.path.isdir(directory):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    return [
        filename
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename))
    ]
