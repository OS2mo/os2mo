# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from base64 import b64encode
from datetime import timedelta
from pathlib import Path
from pathlib import PosixPath
from typing import Any
from typing import Protocol
from unittest import mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from more_itertools import first
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from strawberry.types import ExecutionResult

import mora.graphapi.versions.latest.files
from mora import depends
from mora.config import get_settings
from mora.service.shimmed.exports import check_auth_cookie
from mora.service.shimmed.exports import purge_all_filetokens
from tests.conftest import test_app
from tests.conftest import YieldFixture


@pytest.fixture
def fastapi_test_app_weird_auth() -> FastAPI:
    app = test_app()
    app.dependency_overrides[purge_all_filetokens] = _noop_purge_file_tokens
    app.dependency_overrides[check_auth_cookie] = _noop_check_auth_cookie
    app.dependency_overrides[depends.get_sessionmaker] = _mock_session_maker
    return app


@pytest.fixture
def service_client_weird_auth(
    fastapi_test_app_weird_auth: FastAPI,
) -> YieldFixture[TestClient]:
    with TestClient(fastapi_test_app_weird_auth) as client:
        yield client


class FakeTransaction:
    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, traceback):
        pass


class FakeAsyncSession:
    def __init__(self):
        self.session = AsyncMock()
        self.session.begin = FakeTransaction

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, traceback):
        pass

    def begin(self):
        return self.session.begin()


async def _mock_session_maker() -> async_sessionmaker:
    return FakeAsyncSession


async def _noop_check_auth_cookie() -> None:
    pass


async def _noop_purge_file_tokens() -> None:
    pass


@pytest.fixture()
def mock_no_auth_cookie(monkeypatch) -> None:
    monkeypatch.setattr(
        mora.service.shimmed.exports, "check_auth_cookie", _noop_check_auth_cookie
    )


@pytest.fixture
def file_storage_filesystem(set_settings):
    set_settings(FILE_STORAGE="filesystem", QUERY_EXPORT_DIR="/tmp")
    settings = get_settings()
    assert settings.file_storage == "filesystem"
    assert settings.filesystem_settings.query_export_dir == PosixPath("/tmp")


@pytest.fixture
def mock_execute_graphql(monkeypatch) -> None:
    async def _mock_execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
        response = mock.MagicMock()
        response.errors = {}
        response.data = {
            "files": {
                "objects": [
                    {"base64_contents": b64encode(b"I am a file").decode("ascii")}
                ]
            }
        }
        return response

    monkeypatch.setattr(
        mora.service.shimmed.exports, "execute_graphql", _mock_execute_graphql
    )


class MockPath(Protocol):
    def __call__(
        self,
        is_dir_ret: bool | None = None,
        is_file_ret: bool | None = None,
        iterdir_ret: list | None = None,
    ) -> None:
        ...


@pytest.fixture
def mock_path(monkeypatch) -> MockPath:
    def _mock_path(is_dir_ret=None, is_file_ret=None, iterdir_ret=None):
        class MockPath(PosixPath):
            def is_dir(self):
                if is_dir_ret is None:
                    return super().is_dir()
                return is_dir_ret

            def is_file(self):
                if is_file_ret is None:
                    return super().is_file()
                return is_file_ret

            def iterdir(self):
                if iterdir_ret is None:
                    return super().iterdir()
                return iterdir_ret

        monkeypatch.setattr(mora.graphapi.versions.latest.files, "Path", MockPath)

    return _mock_path


@pytest.mark.usefixtures("file_storage_filesystem")
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


@pytest.mark.usefixtures("file_storage_filesystem", "mock_execute_graphql")
async def test_get_export_reads_cookie(
    service_client_weird_auth: TestClient,
    fastapi_test_app_weird_auth: FastAPI,
) -> None:
    """Ensure that get reads our token and attempts to validate it."""

    # No cookie checking code
    response = service_client_weird_auth.get("/service/exports/filename")
    assert response.status_code == HTTP_200_OK
    assert response.text == "I am a file"

    # Reinstall the cookie checking code
    fastapi_test_app_weird_auth.dependency_overrides[
        check_auth_cookie
    ] = check_auth_cookie

    # No cookie, not okay
    response = service_client_weird_auth.get("/service/exports/filename")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Missing download cookie!"


@pytest.mark.integration_test
@pytest.mark.usefixtures("file_storage_filesystem")
async def test_list_export_files_raises_on_invalid_dir(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure we handle missing export dir"""
    mock_path(is_dir_ret=False)

    response = service_client_weird_auth.get("/service/exports/")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "description": "Directory does not exist.",
        "directory": str(get_settings().filesystem_settings.query_export_dir),
        "error": True,
        "error_key": "E_DIR_NOT_FOUND",
        "status": HTTP_500_INTERNAL_SERVER_ERROR,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("file_storage_filesystem")
async def test_list_export_files_returns_filenames(
    service_client_weird_auth: TestClient, mock_path: MockPath, monkeypatch: MonkeyPatch
) -> None:
    """Ensure that we only return filenames from the export directory"""
    filenames = ["file1", "file2"]
    dirnames = ["dir"]

    mock_path(
        is_dir_ret=True,
        iterdir_ret=list(map(Path, filenames + dirnames)),
    )

    def mock_is_file(self):
        filename = str(self)
        return filename in filenames

    monkeypatch.setattr(Path, "is_file", mock_is_file)

    response = service_client_weird_auth.get("/service/exports/")
    assert response.status_code == HTTP_200_OK
    assert set(response.json()) == set(filenames)


@pytest.mark.usefixtures("file_storage_filesystem", "mock_no_auth_cookie")
async def test_get_export_file_raises_on_invalid_dir(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure we handle missing export dir"""
    mock_path(is_dir_ret=False)

    response = service_client_weird_auth.get("/service/exports/whatever")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "description": "Directory does not exist.",
        "directory": str(get_settings().filesystem_settings.query_export_dir),
        "error": True,
        "error_key": "E_DIR_NOT_FOUND",
        "status": HTTP_500_INTERNAL_SERVER_ERROR,
    }


@pytest.mark.usefixtures("file_storage_filesystem", "mock_no_auth_cookie")
async def test_get_export_file_raises_on_file_not_found(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure we handle nonexistent files"""
    mock_path(is_dir_ret=True, iterdir_ret=[])

    response = service_client_weird_auth.get("/service/exports/whatever")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {
        "description": "Not found.",
        "error": True,
        "error_key": "E_NOT_FOUND",
        "filename": "whatever",
        "status": HTTP_404_NOT_FOUND,
    }


@pytest.mark.usefixtures(
    "file_storage_filesystem", "mock_no_auth_cookie", "mock_execute_graphql"
)
async def test_get_export_file_returns_file(
    service_client_weird_auth: TestClient,
) -> None:
    """Ensure we return a file if found"""
    response = service_client_weird_auth.get("/service/exports/whatever")
    assert response.status_code == HTTP_200_OK
    assert response.text == "I am a file"


@pytest.mark.usefixtures("file_storage_filesystem")
async def test_folder_missing(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure we handle missing export dir."""
    mock_path(is_dir_ret=False)

    response = service_client_weird_auth.post(
        "/service/exports/filename.csv", files=dict(file=b"bar")
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "description": "Directory does not exist.",
        "directory": str(get_settings().filesystem_settings.query_export_dir),
        "error": True,
        "error_key": "E_DIR_NOT_FOUND",
        "status": HTTP_500_INTERNAL_SERVER_ERROR,
    }


@pytest.mark.usefixtures("file_storage_filesystem")
async def test_file_exists(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure that we cannot upload files if they already exist."""
    mock_path(is_dir_ret=True, is_file_ret=True)

    open_mock = mock.mock_open()
    with mock.patch("mora.service.shimmed.exports.open", open_mock, create=True):
        response = service_client_weird_auth.post(
            "/service/exports/filename.csv", files=dict(file=b"bar")
        )
        assert response.status_code == HTTP_409_CONFLICT
        assert response.json() == {
            "description": "File already exists.",
            "error": True,
            "error_key": "E_ALREADY_EXISTS",
            "filename": "filename.csv",
            "status": HTTP_409_CONFLICT,
        }


@pytest.mark.usefixtures("file_storage_filesystem")
async def test_file_exists_but_forced(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure that we can upload files with force, even if a file exists."""
    mock_path(is_dir_ret=True, is_file_ret=True)

    open_mock = mock.mock_open()
    with mock.patch.object(Path, "open", open_mock, create=True):
        response = service_client_weird_auth.post(
            "/service/exports/filename.csv?force=true", files=dict(file=b"bar")
        )
        assert response.status_code == HTTP_200_OK
        assert response.json() == "OK"

    open_mock.assert_called_once_with("wb")
    open_mock().write.assert_called_once_with(b"bar")


@pytest.mark.usefixtures("file_storage_filesystem")
async def test_successful_file_upload(
    service_client_weird_auth: TestClient, mock_path: MockPath
) -> None:
    """Ensure that we can upload files."""
    mock_path(is_dir_ret=True, is_file_ret=False)

    open_mock = mock.mock_open()
    with mock.patch.object(Path, "open", open_mock, create=True):
        response = service_client_weird_auth.post(
            "/service/exports/filename.csv", files=dict(file=b"bar")
        )
        assert response.status_code == HTTP_200_OK
        assert response.json() == "OK"

    open_mock.assert_called_once_with("wb")
    open_mock().write.assert_called_once_with(b"bar")


@pytest.mark.integration_test
@pytest.mark.usefixtures(
    "file_storage_filesystem",
    "load_fixture_data_with_reset",
    "fastapi_session_test_app",
)
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
        "POST", f"/service/exports/{uuid}.csv", files=dict(file=b"bar")
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
        f"/service/exports/{uuid}.csv",
        cookies={"MO_FILE_DOWNLOAD": download_cookie},
    )
    assert response.status_code == HTTP_200_OK
    assert response.text == "bar"

    # Error without a cookie
    response = service_client.request("GET", f"/service/exports/{uuid}.csv")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Missing download cookie!"

    # Error with invalid cookie
    response = service_client.request(
        "GET", f"/service/exports/{uuid}.csv", cookies={"MO_FILE_DOWNLOAD": "incorrect"}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Invalid download cookie!"

    # Error when cookie has expired
    # Patch time delta to make it seem like the cookie has expired
    with mock.patch("mora.service.shimmed.exports.timedelta") as delta:
        delta.return_value = timedelta(minutes=-1)
        response = service_client.request(
            "GET",
            f"/service/exports/{uuid}.csv",
            cookies={"MO_FILE_DOWNLOAD": download_cookie},
        )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == "Expired download cookie!"
