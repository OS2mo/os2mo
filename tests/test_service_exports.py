# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import timedelta
from unittest import mock
from uuid import uuid4

import mora
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mora.service.shimmed.exports import check_auth_cookie
from mora.service.shimmed.exports import purge_all_filetokens
from more_itertools import first
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT

from tests.conftest import YieldFixture


async def noop() -> None:
    pass


@pytest.fixture
def fastapi_test_app_weird_auth(fastapi_test_app: FastAPI) -> FastAPI:
    fastapi_test_app.dependency_overrides[purge_all_filetokens] = noop
    fastapi_test_app.dependency_overrides[check_auth_cookie] = noop
    return fastapi_test_app


@pytest.fixture
def service_client_weird_auth(
    fastapi_test_app_weird_auth: FastAPI,
) -> YieldFixture[TestClient]:
    with TestClient(fastapi_test_app_weird_auth) as client:
        yield client


@pytest.fixture
def mock_no_auth_cookie(monkeypatch) -> None:
    monkeypatch.setattr(mora.service.shimmed.exports, "check_auth_cookie", noop)


@pytest.fixture
def uploaded_file(
    empty_db,
    service_client_weird_auth: TestClient,
) -> tuple[str, bytes]:
    filename = "filename.csv"
    content = b"I'm a file"
    service_client_weird_auth.post(
        f"/service/exports/{filename}",
        files=dict(file=content),
    )
    return filename, content


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_list_export_files_sets_cookie(
    service_client_weird_auth: TestClient,
) -> None:
    """Ensure that list sets a token."""
    secret = "alfa123"

    with mock.patch("mora.service.shimmed.exports.token_hex", new=lambda _: secret):
        response = service_client_weird_auth.get("/service/exports/")

    assert response.status_code == HTTP_200_OK
    cookie_set = set(response.headers["set-cookie"].split("; "))
    assert cookie_set == {
        "MO_FILE_DOWNLOAD=" + secret,
        "HttpOnly",
        "Path=/service/exports/",
        "SameSite=strict",
        "Secure",
    }


@pytest.mark.integration_test
async def test_get_export_reads_cookie(
    service_client_weird_auth: TestClient,
    fastapi_test_app_weird_auth: FastAPI,
    uploaded_file: tuple[str, bytes],
) -> None:
    """Ensure that get reads our token and attempts to validate it."""
    filename, content = uploaded_file

    # No cookie checking code
    response = service_client_weird_auth.get(f"/service/exports/{filename}")
    assert response.status_code == HTTP_200_OK
    assert response.text == content.decode("utf8")

    # Reinstall the cookie checking code
    fastapi_test_app_weird_auth.dependency_overrides[check_auth_cookie] = (
        check_auth_cookie
    )

    # No cookie, not okay
    response = service_client_weird_auth.get(f"/service/exports/{filename}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Missing download cookie!"


@pytest.mark.integration_test
async def test_list_export_files_returns_filenames(
    service_client_weird_auth: TestClient,
    uploaded_file: tuple[str, bytes],
) -> None:
    """Ensure that we get filenames from the export directory"""
    filename, _ = uploaded_file
    additional_filename = "file2"

    # uploaded one more file
    service_client_weird_auth.post(
        f"/service/exports/{additional_filename}",
        files=dict(file=b"test"),
    )

    filenames = [filename, additional_filename]

    response = service_client_weird_auth.get("/service/exports/")
    assert response.status_code == HTTP_200_OK
    assert set(response.json()) == set(filenames)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_get_export_file_raises_on_file_not_found(
    service_client_weird_auth: TestClient,
) -> None:
    """Ensure we handle nonexistent files"""
    response = service_client_weird_auth.get("/service/exports/whatever")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {
        "description": "Not found.",
        "error": True,
        "error_key": "E_NOT_FOUND",
        "filename": "whatever",
        "status": HTTP_404_NOT_FOUND,
    }


@pytest.mark.integration_test
async def test_get_export_file_returns_file(
    service_client_weird_auth: TestClient,
    uploaded_file: tuple[str, bytes],
) -> None:
    """Ensure we return a file if found"""
    filename, content = uploaded_file
    response = service_client_weird_auth.get(f"/service/exports/{filename}")
    assert response.status_code == HTTP_200_OK
    assert response.text == content.decode("utf-8")


@pytest.mark.integration_test
async def test_file_exists(
    service_client_weird_auth: TestClient, uploaded_file: tuple[str, bytes]
) -> None:
    """Ensure that we cannot upload files if they already exist."""
    filename, _ = uploaded_file
    response = service_client_weird_auth.post(
        f"/service/exports/{filename}", files=dict(file=b"bar")
    )
    assert response.status_code == HTTP_409_CONFLICT
    assert response.json() == {
        "description": "File already exists.",
        "error": True,
        "error_key": "E_ALREADY_EXISTS",
        "filename": "filename.csv",
        "status": HTTP_409_CONFLICT,
    }


@pytest.mark.integration_test
async def test_file_exists_but_forced(
    service_client_weird_auth: TestClient,
    uploaded_file: tuple[str, bytes],
) -> None:
    """Ensure that we can upload files with force, even if a file exists."""
    filename, _ = uploaded_file
    response = service_client_weird_auth.post(
        f"/service/exports/{filename}?force=true", files=dict(file=b"bar")
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == "OK"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_filesystem(service_client: TestClient) -> None:
    uuid = uuid4()
    filename = f"{uuid}.csv"

    # Test that our file does not exist
    response = service_client.request("GET", "/service/exports/")
    assert response.status_code == HTTP_200_OK
    assert filename not in response.json()
    download_cookie = first(response.headers["set-cookie"].split(";"))
    download_cookie_header, download_cookie = download_cookie.split("=")
    assert download_cookie_header == "MO_FILE_DOWNLOAD"

    # Create a file
    response = service_client.request(
        "POST", f"/service/exports/{filename}", files=dict(file=b"bar")
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == "OK"

    # Test that our file exists now
    response = service_client.request("GET", "/service/exports/")
    assert response.status_code == HTTP_200_OK
    assert filename in response.json()
    download_cookie = first(response.headers["set-cookie"].split(";"))
    download_cookie_header, download_cookie = download_cookie.split("=")
    assert download_cookie_header == "MO_FILE_DOWNLOAD"

    # Download our file
    response = service_client.request(
        "GET",
        f"/service/exports/{filename}",
        cookies={"MO_FILE_DOWNLOAD": download_cookie},
    )
    assert response.status_code == HTTP_200_OK
    assert response.text == "bar"

    # Error without a cookie
    response = service_client.request("GET", f"/service/exports/{filename}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Missing download cookie!"

    # Error with invalid cookie
    response = service_client.request(
        "GET", f"/service/exports/{filename}", cookies={"MO_FILE_DOWNLOAD": "incorrect"}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Invalid download cookie!"

    # Error when cookie has expired
    # Patch time delta to make it seem like the cookie has expired
    with mock.patch("mora.service.shimmed.exports.timedelta") as delta:
        delta.return_value = timedelta(minutes=-1)
        response = service_client.request(
            "GET",
            f"/service/exports/{filename}",
            cookies={"MO_FILE_DOWNLOAD": download_cookie},
        )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Expired download cookie!"
