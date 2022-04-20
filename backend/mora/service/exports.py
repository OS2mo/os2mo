# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from fastapi import Cookie
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer

from mora.auth.keycloak.oidc import auth
from .. import exceptions, config

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="service/token")


def get_export_dir() -> Path:
    """Get the configured export directory.

    Raises:
        E_DIR_NOT_FOUND: If the configured directory does not exist.

    Returns:
        A Path object pointing to the directory.
    """
    settings = config.get_settings()
    export_dir = Path(settings.query_export_dir)
    if not export_dir.is_dir():
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()
    return export_dir


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

    export_dir = get_export_dir()
    dir_contents = export_dir.iterdir()
    files = list(filter(lambda file: (export_dir / file).is_file(), dir_contents))
    return files


async def _check_auth_cookie(auth_cookie=Optional[str]) -> None:
    if auth_cookie is None:
        raise HTTPException(status_code=401, detail="Missing download cookie!")
    await auth(str(auth_cookie))


@router.get(
    "/exports/{file_name}",
    responses={"500": {"description": "Directory does not exist"}},
)
async def download_export_file(
    file_name: str,
    mo_file_download: Optional[str] = Cookie(None, alias="MO_FILE_DOWNLOAD"),
):
    """Download an export file with a given name.

    :param string file_name: Name of the export file.
    :param string mo_file_download: OIDC Token used for authentication.

    :return: The file data corresponding to the given export file name.
    """
    await _check_auth_cookie(mo_file_download)

    export_dir = get_export_dir()
    file_path = export_dir / file_name
    if not file_path.is_file():
        exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)

    return FileResponse(file_path)


@router.post(
    "/exports/{file_name}",
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(auth)],
)
async def upload_export_file(
    file_name: str, file: bytes = File(...), force: Optional[bool] = False
):
    """Upload an export file with a given name.

    Called as:

        curl -X POST -F file=@NEWS.md -H "Authorization: Bearer $TOKEN" URL

    :param string file_name: Name of the export file.
    :param bytes file: The file contents.
    :param bool force: Whether to override existing file.

    :return: OK
    """
    export_dir = get_export_dir()
    file_path = export_dir / file_name
    if file_path.is_file() and not force:
        exceptions.ErrorCodes.E_ALREADY_EXISTS(filename=file_name)

    with file_path.open("wb") as f:
        f.write(file)

    return "OK"
