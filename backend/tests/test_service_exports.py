# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from base64 import b64encode
from pathlib import Path
from typing import Optional

import mock
import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from mora.config import get_settings
from mora.service.shimmed.exports import oauth2_scheme
from tests.conftest import test_app


async def _noop_check_auth_cookie(auth_cookie: Optional[str]) -> None:
    pass


@pytest.fixture(scope="class")
def fastapi_test_app_weird_auth():
    async def _noop_oauth2_scheme(request: Request) -> Optional[str]:
        return "jwt-goes-here"

    def test_app_weird_auth():
        app = test_app()
        app.dependency_overrides[oauth2_scheme] = _noop_oauth2_scheme
        return app

    yield test_app_weird_auth()


@pytest.fixture
def service_client_weird_auth(fastapi_test_app_weird_auth):
    with TestClient(fastapi_test_app_weird_auth) as client:
        yield client


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

    @mock.patch("mora.service.shimmed.exports.execute_graphql")
    async def test_get_export_reads_cookie(self, execute, service_client_weird_auth):
        """Ensure that get reads our token and attempts to validate it."""
        response = mock.MagicMock()
        response.errors = {}
        response.data = {
            "files": [{"base64_contents": b64encode(b"I am a file").decode("ascii")}]
        }
        execute.return_value = response

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
        with mock.patch(
            "mora.service.shimmed.exports._check_auth_cookie", _noop_check_auth_cookie
        ):
            response = service_client_weird_auth.get("/service/exports/filename")
            assert response.status_code == HTTP_200_OK
            assert response.text == "I am a file"


class TestFile:
    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_list_export_files_raises_on_invalid_dir(
        self, service_client_weird_auth
    ):
        """Ensure we handle missing export dir"""
        response = service_client_weird_auth.get("/service/exports/")
        assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "description": "Directory does not exist.",
            "directory": str(get_settings().filesystem_settings.query_export_dir),
            "error": True,
            "error_key": "E_DIR_NOT_FOUND",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
        }

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "iterdir")
    async def test_list_export_files_returns_filenames(
        self, mock_listdir, service_client_weird_auth
    ):
        """Ensure that we only return filenames from the export directory"""
        filenames = ["file1", "file2"]
        dirnames = ["dir"]

        def mocked_isfile(self):
            filename = str(self)
            return filename in filenames

        mock_listdir.return_value = list(map(Path, filenames + dirnames))

        with mock.patch.object(Path, "is_file", mocked_isfile):
            response = service_client_weird_auth.get("/service/exports/")
            assert response.status_code == HTTP_200_OK
            assert set(response.json()) == set(filenames)

    @mock.patch(
        "mora.service.shimmed.exports._check_auth_cookie", _noop_check_auth_cookie
    )
    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_get_export_file_raises_on_invalid_dir(
        self, service_client_weird_auth
    ):
        """Ensure we handle missing export dir"""
        response = service_client_weird_auth.get("/service/exports/whatever")
        assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "description": "Directory does not exist.",
            "directory": str(get_settings().filesystem_settings.query_export_dir),
            "error": True,
            "error_key": "E_DIR_NOT_FOUND",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
        }

    @mock.patch(
        "mora.service.shimmed.exports._check_auth_cookie", _noop_check_auth_cookie
    )
    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "iterdir")
    async def test_get_export_file_raises_on_file_not_found(
        self, mock_listdir, service_client_weird_auth
    ):
        """Ensure we handle nonexistent files"""
        mock_listdir.return_value = []
        response = service_client_weird_auth.get("/service/exports/whatever")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json() == {
            "description": "Not found.",
            "error": True,
            "error_key": "E_NOT_FOUND",
            "filename": "whatever",
            "status": HTTP_404_NOT_FOUND,
        }

    @mock.patch(
        "mora.service.shimmed.exports._check_auth_cookie", _noop_check_auth_cookie
    )
    @mock.patch("mora.service.shimmed.exports.execute_graphql")
    async def test_get_export_file_returns_file(
        self, execute, service_client_weird_auth
    ):
        """Ensure we return a file if found"""
        response = mock.MagicMock()
        response.errors = {}
        response.data = {
            "files": [{"base64_contents": b64encode(b"I am a file").decode("ascii")}]
        }
        execute.return_value = response

        response = service_client_weird_auth.get("/service/exports/whatever")
        assert response.status_code == HTTP_200_OK
        assert response.text == "I am a file"
        execute.assert_called_once()


class TestFileUpload:
    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_folder_missing(self, service_client_weird_auth):
        """Ensure we handle missing export dir."""
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

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    async def test_file_exists(self, service_client_weird_auth):
        """Ensure that we cannot upload files if they already exist."""
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

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    async def test_file_exists_but_forced(self, service_client_weird_auth):
        """Ensure that we can upload files with force, even if a file exists."""
        open_mock = mock.mock_open()
        with mock.patch.object(Path, "open", open_mock, create=True):
            response = service_client_weird_auth.post(
                "/service/exports/filename.csv?force=true", files=dict(file=b"bar")
            )
            assert response.status_code == HTTP_200_OK
            assert response.json() == "OK"

        open_mock.assert_called_once_with("wb")
        open_mock().write.assert_called_once_with(b"bar")

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: False)
    async def test_successful_file_upload(self, service_client_weird_auth):
        """Ensure that we can upload files."""
        open_mock = mock.mock_open()
        with mock.patch.object(Path, "open", open_mock, create=True):
            response = service_client_weird_auth.post(
                "/service/exports/filename.csv", files=dict(file=b"bar")
            )
            assert response.status_code == HTTP_200_OK
            assert response.json() == "OK"

        open_mock.assert_called_once_with("wb")
        open_mock().write.assert_called_once_with(b"bar")
