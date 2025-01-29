# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# TODO: How do we wanna audit file-access? - Files in Postgres would make it simple
import io
from base64 import b64decode
from datetime import timedelta
from operator import itemgetter
from secrets import token_hex
from typing import Any

from fastapi import Cookie
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import Response
from fastapi.responses import StreamingResponse
from more_itertools import one
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from starlette.datastructures import UploadFile

from mora import exceptions
from mora.auth.keycloak.oidc import auth
from mora.db import FileToken
from mora.graphapi.shim import execute_graphql
from mora.service.exports import router as exports_router

from ... import depends
from .errors import handle_gql_error

cookie_key = "MO_FILE_DOWNLOAD"
file_token_expiration_minutes = 10


async def purge_all_filetokens(
    session: depends.Session,
) -> None:
    """Purge expired filetokens."""
    await session.execute(
        delete(FileToken).where(
            FileToken.created_at + timedelta(minutes=file_token_expiration_minutes)
            < func.now()
        )
    )


@exports_router.get(
    "/exports/",
    response_model=list[str],
    response_model_exclude_unset=True,
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(auth), Depends(purge_all_filetokens)],
)
async def list_export_files(
    response: Response,
    session: depends.Session,
) -> list[str]:
    """List the available exports.

    Example:
      [
        "export1.xlsx",
        "export2.xlsx"
      ]
    """
    secret = token_hex(127)
    response.set_cookie(
        key=cookie_key,
        value=secret,
        secure=True,
        httponly=True,
        samesite="strict",
        path="/service/exports/",
    )
    await session.execute(
        insert(FileToken),
        [
            {"secret": secret},
        ],
    )

    query = "query FilesQuery { files(filter: {file_store: EXPORTS}) { objects { file_name } } }"
    gql_response = await execute_graphql(query)
    handle_gql_error(gql_response)
    files = gql_response.data["files"]["objects"]
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
    fake_file = UploadFile(file=io.BytesIO(file), filename=file_name)
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


async def check_auth_cookie(
    session: depends.Session,
    auth_cookie: str | None = Cookie(None, alias=cookie_key),
) -> None:
    """Check the provided auth cookie in the file_token table.

    Args:
        session: DB session to run our query on.
        auth_cookie: The cookie value provided by the user.

    Raises:
        HTTPException if the cookie value was not acceptable.
    """
    if auth_cookie is None:
        raise HTTPException(status_code=401, detail="Missing download cookie!")

    result = await session.scalar(
        select(FileToken).where(FileToken.secret == auth_cookie)
    )
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid download cookie!")

    # Use database time instead of datetime.now as database time might be different
    now = await session.scalar(func.now())
    if result.created_at + timedelta(minutes=file_token_expiration_minutes) < now:
        raise HTTPException(status_code=401, detail="Expired download cookie!")


@exports_router.get(
    "/exports/{file_name}",
    responses={"500": {"description": "Directory does not exist"}},
    dependencies=[Depends(check_auth_cookie)],
)
async def download_export_file(
    file_name: str = Path(..., description="Name of the export file."),
) -> StreamingResponse:
    """Download an export file with a given name.

    Args:
        file_name: Name of the export file.

    Returns:
        The file data corresponding to the given export file name.
    """
    variables = {
        "file_name": file_name,
    }
    query = """
    query FileQuery($file_name: String!) {
      files(filter: {file_store: EXPORTS, file_names: [$file_name]}) {
        objects {
          base64_contents
        }
      }
    }
    """
    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    files = response.data["files"]["objects"]
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
