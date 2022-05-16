# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Optional

import mock
from fastapi import Request
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED

import tests.cases
from mora.config import Settings
from mora.service.exports import oauth2_scheme
from tests import util


async def _noop_check_auth_cookie(auth_cookie: Optional[str]) -> None:
    pass


async def _noop_oauth2_scheme(request: Request) -> Optional[str]:
    return "jwt-goes-here"


class AuthTests(tests.cases.AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

        # Bypass Oauth2 per default
        self.app.dependency_overrides[oauth2_scheme] = _noop_oauth2_scheme

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "iterdir")
    async def test_list_export_files_sets_cookie(self, mock_listdir):
        """Ensure that list sets a token."""
        response = await self.request("/service/exports/")
        cookie_set = set(response.headers["set-cookie"].split("; "))
        assert cookie_set == {
            "MO_FILE_DOWNLOAD=jwt-goes-here",
            "HttpOnly",
            "Path=/service/exports/",
            "SameSite=strict",
            "Secure",
        }

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    @mock.patch("mora.service.exports.FileResponse")
    async def test_get_export_reads_cookie(self, mock_send_file):
        """Ensure that get reads our token and attempts to validate it."""
        mock_send_file.return_value = "I am a file"

        # No cookie, not okay
        response = await self.request("/service/exports/filename")
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.text == '"Missing download cookie!"'

        # Invalid cookie, jwt says no
        response = await self.request(
            "/service/exports/filename", cookies={"MO_FILE_DOWNLOAD": "invalid"}
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "status": "Unauthorized",
            "msg": "Not enough segments",
        }

        # No validation, no problem
        with mock.patch(
            "mora.service.exports._check_auth_cookie", _noop_check_auth_cookie
        ):
            response = await self.request("/service/exports/filename")
            assert response.status_code == HTTP_200_OK
            assert response.text == '"I am a file"'


class FileTests(tests.cases.AsyncTestCase):
    maxDiff = None

    async def asyncSetUp(self):
        await super().asyncSetUp()

        # Bypass Oauth2 per default
        self.app.dependency_overrides[oauth2_scheme] = _noop_oauth2_scheme

    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_list_export_files_raises_on_invalid_dir(self):
        """Ensure we handle missing export dir"""
        await self.assertRequestResponse(
            "/service/exports/",
            {
                "description": "Directory does not exist.",
                "error": True,
                "error_key": "E_DIR_NOT_FOUND",
                "status": 500,
            },
            status_code=500,
        )

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "iterdir")
    async def test_list_export_files_returns_filenames(self, mock_listdir):
        """Ensure that we only return filenames from the export directory"""
        filenames = ["file1", "file2"]
        dirnames = ["dir"]

        def mocked_isfile(self):
            filename = str(self)
            return filename in filenames

        mock_listdir.return_value = list(map(Path, filenames + dirnames))

        with mock.patch.object(Path, "is_file", mocked_isfile):
            with util.override_config(Settings(query_export_dir="")):
                await self.assertRequestResponse("/service/exports/", filenames)

    @mock.patch("mora.service.exports._check_auth_cookie", _noop_check_auth_cookie)
    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_get_export_file_raises_on_invalid_dir(self):
        """Ensure we handle missing export dir"""
        await self.assertRequestResponse(
            "/service/exports/whatever",
            {
                "description": "Directory does not exist.",
                "error": True,
                "error_key": "E_DIR_NOT_FOUND",
                "status": 500,
            },
            status_code=500,
        )

    @mock.patch("mora.service.exports._check_auth_cookie", _noop_check_auth_cookie)
    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: False)
    async def test_get_export_file_raises_on_file_not_found(self):
        """Ensure we handle nonexistent files"""
        await self.assertRequestResponse(
            "/service/exports/whatever",
            {
                "description": "Not found.",
                "error": True,
                "error_key": "E_NOT_FOUND",
                "filename": "whatever",
                "status": 404,
            },
            status_code=404,
        )

    @mock.patch("mora.service.exports._check_auth_cookie", _noop_check_auth_cookie)
    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    @mock.patch("mora.service.exports.FileResponse")
    async def test_get_export_file_returns_file(self, mock_send_file):
        """Ensure we return a file if found"""

        mock_send_file.return_value = "I am a file"

        await self.assertRequestResponse("/service/exports/whatever", "I am a file")
        mock_send_file.assert_called_once()


class FileUploadTests(tests.cases.AsyncTestCase):
    maxDiff = None

    @mock.patch.object(Path, "is_dir", lambda x: False)
    async def test_folder_missing(self):
        """Ensure we handle missing export dir."""
        response = await self.client.post(
            "/service/exports/filename.csv", files=dict(file=b"bar")
        )
        assert response.status_code == 500
        assert response.json() == {
            "description": "Directory does not exist.",
            "error": True,
            "error_key": "E_DIR_NOT_FOUND",
            "status": 500,
        }

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    async def test_file_exists(self):
        """Ensure that we cannot upload files if they already exist."""
        open_mock = mock.mock_open()
        with mock.patch("mora.service.exports.open", open_mock, create=True):
            response = await self.client.post(
                "/service/exports/filename.csv", files=dict(file=b"bar")
            )
            assert response.status_code == 409
            assert response.json() == {
                "description": "File already exists.",
                "error": True,
                "error_key": "E_ALREADY_EXISTS",
                "filename": "filename.csv",
                "status": 409,
            }

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: True)
    async def test_file_exists_but_forced(self):
        """Ensure that we can upload files with force, even if a file exists."""
        open_mock = mock.mock_open()
        with mock.patch.object(Path, "open", open_mock, create=True):
            response = await self.client.post(
                "/service/exports/filename.csv?force=true", files=dict(file=b"bar")
            )
            assert response.status_code == 200
            assert response.json() == "OK"

        open_mock.assert_called_once_with("wb")
        open_mock().write.assert_called_once_with(b"bar")

    @mock.patch.object(Path, "is_dir", lambda x: True)
    @mock.patch.object(Path, "is_file", lambda x: False)
    async def test_successful_file_upload(self):
        """Ensure that we can upload files."""
        open_mock = mock.mock_open()
        with mock.patch.object(Path, "open", open_mock, create=True):
            response = await self.client.post(
                "/service/exports/filename.csv", files=dict(file=b"bar")
            )
            assert response.status_code == 200
            assert response.json() == "OK"

        open_mock.assert_called_once_with("wb")
        open_mock().write.assert_called_once_with(b"bar")
