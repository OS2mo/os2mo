#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List

from fastapi import Depends
from fastapi import File
from fastapi import Path
from fastapi import Query
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from starlette.datastructures import UploadFile

from .errors import handle_gql_error
from mora.auth.keycloak.oidc import auth
from mora.graphapi.shim import execute_graphql
from mora.service.exports import router as exports_router

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="service/token")


@exports_router.get(
    "/exports/",
    response_model=List[str],
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
    query = "query FilesQuery { files }"
    gql_response = await execute_graphql(query)
    handle_gql_error(gql_response)
    files = gql_response.data["files"]
    return files


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
      upload_file(file: $file, force: $force)
    }
    """
    response = await execute_graphql(query, variable_values=variables)
    handle_gql_error(response)
    status = response.data["upload_file"]
    return status
