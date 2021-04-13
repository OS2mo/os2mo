# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from .. import exceptions
from ..settings import app_config

router = APIRouter()


@router.get('/exports/')
# @util.restrictargs()
def list_export_files():
    """
    List the available exports

    .. :quickref: Exports; List

    :return: A list of available export files

    **Example Response**:

    .. sourcecode:: json

      [
        "export1.xlsx",
        "export2.xlsx"
      ]
    """
    export_dir = app_config['QUERY_EXPORT_DIR']
    if not os.path.isdir(export_dir):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()
    dir_contents = os.listdir(export_dir)
    files = [
        file for file in dir_contents if
        os.path.isfile(os.path.join(export_dir, file))
    ]
    return files


@router.get('/exports/{file_name}')
# @util.restrictargs()
def get_export_file(file_name: str):
    """
    Fetch a export file with a given name

    .. :quickref: Exports; Get

    :param string file_name: Name of the export file

    :return: The file corresponding to the given export file name
    """
    export_dir = app_config['QUERY_EXPORT_DIR']
    if not os.path.isdir(export_dir):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    file_path = os.path.join(export_dir, file_name)
    if not os.path.isfile(file_path):
        exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)

    return FileResponse(export_dir + "/" + file_name)
