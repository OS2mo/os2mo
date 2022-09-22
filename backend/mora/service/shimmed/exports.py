# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from base64 import b64decode
from operator import itemgetter
from typing import Any
from typing import Optional

from fastapi import Cookie
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import Response
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from more_itertools import one
from starlette.datastructures import UploadFile

from .errors import handle_gql_error
from mora import exceptions
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import validate_token
from mora.graphapi.shim import execute_graphql
from mora.service.exports import router as exports_router


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="service/token")


@exports_router.get(
    "/exports/",
    response_model=list[str],
    response_model_exclude_unset=True,
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(auth)],
)
async def list_export_files(response: Response, token: str = Depends(oauth2_scheme)):
    """List the available exports.

    Example:
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
    query = "query FilesQuery { files(file_store: EXPORTS) { file_name } }"
    gql_response = await execute_graphql(query)
    handle_gql_error(gql_response)
    files = gql_response.data["files"]
    return list(map(itemgetter("file_name"), files))


@exports_router.post(
    "/exports/{file_name}",
    response_model=str,
    response_model_exclude_unset=True,
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(auth)],
)
async def upload_export_file(
    file_name: str = Path(..., description="Name of the export file."),
    file: bytes = File(..., description="The file contents."),
    force: bool = Query(False, description="Whether to override existing files."),
) -> str:
    """Upload an export file with a given name.

    Called as:
        curl -X POST -F file=@NEWS.md -H "Authorization: Bearer $TOKEN" URL

    Returns:
        "OK"
    """
    fake_file = UploadFile(filename=file_name)
    await fake_file.write(file)
    await fake_file.seek(0)
    variables = {
        "file": fake_file,
        "force": force,
    }
    query = """
    mutation($file: Upload!, $force: Boolean!) {
      upload_file(file_store: EXPORTS, file: $file, force: $force)
    }
    """
    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    status = response.data["upload_file"]
    return status


async def _check_auth_cookie(auth_cookie=Optional[str]) -> None:
    if auth_cookie is None:
        raise HTTPException(status_code=401, detail="Missing download cookie!")
    await validate_token(str(auth_cookie))


@exports_router.get(
    "/exports/{file_name}",
    responses={"500": {"description": "Directory does not exist"}},
)
async def download_export_file(
    file_name: str = Path(..., description="Name of the export file."),
    mo_file_download: Optional[str] = Cookie(None, alias="MO_FILE_DOWNLOAD"),
) -> StreamingResponse:
    """Download an export file with a given name.

    :param string file_name: Name of the export file.
    :param string mo_file_download: OIDC Token used for authentication.

    :return: The file data corresponding to the given export file name.
    """
    await _check_auth_cookie(mo_file_download)

    variables = {
        "file_name": file_name,
    }
    query = """
    query FileQuery($file_name: String!) {
      files(file_store: EXPORTS, file_names: [$file_name]) {
        base64_contents
      }
    }
    """
    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    files = response.data["files"]
    if not files:
        exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)
    try:
        file: dict[str, Any] = one(files)
    except ValueError as err:
        raise ValueError("Wrong number of files returned, expected one.") from err
    content = file["base64_contents"]
    data = b64decode(content.encode("ascii"))

    async def data_streamer():
        yield data

    return StreamingResponse(data_streamer(), media_type="application/octet-stream")
