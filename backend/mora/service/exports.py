# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from minio.error import S3Error

from .. import exceptions
from ..settings import app_config
from ..object_store import create_client, get_bucket_name

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
    client = create_client()
    objects = client.list_objects(get_bucket_name())
    files = [obj.object_name for obj in objects]
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
    client = create_client()
    try:
        s3object = client.get_object(get_bucket_name(), file_name)
    except S3Error as error:
        if error.code == "NoSuchKey":
            exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)
        raise error

    async def filedata():
        yield s3object.data

    return StreamingResponse(filedata())
