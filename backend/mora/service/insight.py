# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json
import os
from typing import List, Union, Optional, Dict
from pydantic import BaseModel

from fastapi import APIRouter, Query

router = APIRouter()


# TODO: Schema and Fields shadows BaseModel attributes - Find better names
class Skema(BaseModel):
    felter: List[Dict[str, str]]
    primary_key: List[str]
    pandas_version = str


class Insight(BaseModel):
    title: str
    # TODO: Might be able to do something smart with Panda's schema
    skema: Skema
    data: List[Union[int, str]]


@router.get('/insight')
async def get_insight_data(q: Optional[str] = Query('all')
                           ) -> List[Insight]:
    """Loads data from a directory of JSONs and returns it as a list

    **param q:** Enables the frontend to choose a specific file or show all files
    """
    directory = 'backend/mora/service/dummy-data'

    if q == 'all':
        return [
            json.load(
                open(os.path.join(directory, filename))
            )
            for filename in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, filename))
        ]
    elif os.path.isfile(os.path.join(directory, q)):
        return json.load(
            open(os.path.join(directory, q))
        )


@router.get('/insight/files')
async def get_insight_filenames() -> List[str]:
    """Lists all available files
    """
    directory = 'backend/mora/service/dummy-data'

    return [
        filename
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename))
    ]
