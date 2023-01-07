# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from base64 import b64encode
from pathlib import Path
from pathlib import PosixPath
from typing import Any
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi import Request
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from strawberry.types import ExecutionResult

import mora.graphapi.versions.latest.files
from mora.config import get_settings
from mora.service.shimmed.exports import oauth2_scheme
from tests.conftest import test_app
from tests.conftest import YieldFixture


@pytest.fixture(scope="class")
def fastapi_test_app_weird_auth() -> FastAPI:
    async def _noop_oauth2_scheme(request: Request) -> str | None:
        return "jwt-goes-here"

    def test_app_weird_auth() -> FastAPI:
        app = test_app()
        app.dependency_overrides[oauth2_scheme] = _noop_oauth2_scheme
        return app

    return test_app_weird_auth()


@pytest.fixture(scope="class")
def service_client_weird_auth(
    fastapi_test_app_weird_auth: FastAPI,
) -> YieldFixture[TestClient]:
    with TestClient(fastapi_test_app_weird_auth) as client:
        yield client


async def _noop_check_auth_cookie(auth_cookie: str | None) -> None:
    pass


@pytest.fixture()
def mock_no_auth_cookie(monkeypatch):
    monkeypatch.setattr(
        mora.service.shimmed.exports, "_check_auth_cookie", _noop_check_auth_cookie
    )


@pytest.fixture
def file_storage_filesystem(set_settings):
    set_settings(file_storage="filesystem")


@pytest.fixture
def mock_execute_graphql(monkeypatch):
    async def _mock_execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
        response = mock.MagicMock()
        response.errors = {}
        response.data = {
            "files": [{"base64_contents": b64encode(b"I am a file").decode("ascii")}]
        }
        return response

    monkeypatch.setattr(
        mora.service.shimmed.exports, "execute_graphql", _mock_execute_graphql
    )


@pytest.fixture
def mock_path(monkeypatch):
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


class TestAuth:
    async def test_list_export_files_sets_cookie(self, service_client_weird_auth):
        """Ensure that list sets a token."""
        response = service_client_weird_auth.get("/service/exports/")
        assert response.status_code == HTTP_200_OK
        cookie_set = set(response.headers["set-cookie"].split("; "))
        assert cookie_set == {
            "MO_FILE_DOWNLOAD=jwt-goes-here",
            "HttpOnly",
            "Path=/service/exports/",
            "SameSite=strict",
            "Secure",
        }

    async def test_get_export_reads_cookie(
        self, service_client_weird_auth, mock_execute_graphql, monkeypatch
    ):
        """Ensure that get reads our token and attempts to validate it."""

        # No cookie, not okay
        response = service_client_weird_auth.get("/service/exports/filename")
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.text == '"Missing download cookie!"'

        # Invalid cookie, jwt says no
        response = service_client_weird_auth.get(
            "/service/exports/filename", cookies={"MO_FILE_DOWNLOAD": "invalid"}
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "status": "Unauthorized",
            "msg": "Not enough segments",
        }

        # No validation, no problem
        with monkeypatch.context() as m:
            m.setattr(
                mora.service.shimmed.exports,
                "_check_auth_cookie",
                _noop_check_auth_cookie,
            )
            response = service_client_weird_auth.get("/service/exports/filename")
            assert response.status_code == HTTP_200_OK
            assert response.text == "I am a file"


@pytest.mark.usefixtures("file_storage_filesystem")
class TestFile:
    async def test_list_export_files_raises_on_invalid_dir(
        self, service_client_weird_auth, mock_path
    ):
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

    async def test_list_export_files_returns_filenames(
        self, service_client_weird_auth, mock_path, monkeypatch
    ):
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

    async def test_get_export_file_raises_on_invalid_dir(
        self, service_client_weird_auth, mock_path, mock_no_auth_cookie
    ):
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

    async def test_get_export_file_raises_on_file_not_found(
        self, service_client_weird_auth, mock_path, mock_no_auth_cookie
    ):
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

    async def test_get_export_file_returns_file(
        self,
        service_client_weird_auth,
        mock_execute_graphql,
        mock_no_auth_cookie,
    ):
        """Ensure we return a file if found"""
        response = service_client_weird_auth.get("/service/exports/whatever")
        assert response.status_code == HTTP_200_OK
        assert response.text == "I am a file"


@pytest.mark.usefixtures("file_storage_filesystem")
class TestFileUpload:
    async def test_folder_missing(self, service_client_weird_auth, mock_path):
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

    async def test_file_exists(self, service_client_weird_auth, mock_path):
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

    async def test_file_exists_but_forced(self, service_client_weird_auth, mock_path):
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

    async def test_successful_file_upload(self, service_client_weird_auth, mock_path):
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
