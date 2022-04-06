# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os
from typing import Optional

from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer

from mora.auth.keycloak.oidc import auth
from .. import exceptions, config

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="service/token")


@router.get(
    "/exports/",
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(auth)],
)
def list_export_files(response: Response, token: str = Depends(oauth2_scheme)):
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
    response.set_cookie(
        key="MO_FILE_DOWNLOAD",
        value=token,
        secure=True,
        httponly=True,
        samesite="strict",
        path="/service/exports/",
    )

    settings = config.get_settings()
    export_dir = settings.query_export_dir
    if not os.path.isdir(export_dir):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()
    dir_contents = os.listdir(export_dir)
    files = [
        file for file in dir_contents if os.path.isfile(os.path.join(export_dir, file))
    ]
    return files


async def _check_auth_cookie(auth_cookie=Optional[str]) -> None:
    if auth_cookie is None:
        raise HTTPException(status_code=401, detail="Missing download cookie!")
    await auth(str(auth_cookie))


@router.get(
    "/exports/{file_name}",
    responses={"500": {"description": "Directory does not exist"}},
)
async def get_export_file(
    file_name: str,
    mo_file_download: Optional[str] = Cookie(None, alias="MO_FILE_DOWNLOAD"),
):
    """
    Fetch a export file with a given name

    .. :quickref: Exports; Get

    :param string file_name: Name of the export file

    :return: The file corresponding to the given export file name
    """
    await _check_auth_cookie(mo_file_download)

    settings = config.get_settings()
    export_dir = settings.query_export_dir
    if not os.path.isdir(export_dir):
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()

    file_path = os.path.join(export_dir, file_name)
    if not os.path.isfile(file_path):
        exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)

    return FileResponse(export_dir + "/" + file_name)
