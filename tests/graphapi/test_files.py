# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from base64 import b64encode

import pytest
from more_itertools import one
from starlette.status import HTTP_409_CONFLICT

from tests.conftest import GraphAPIPost
from tests.conftest import UploadFile


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_file_name_contains_filter(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure the `file_name_contains` filter returns case-insensitive substring matches."""
    for filename in ("report.csv", "Report.txt", "summary.csv"):
        assert upload_file(filename, b"data").errors is None

    query = """
        query Files($substring: String!) {
          files(filter: {file_store: EXPORTS, file_name_contains: $substring}) {
            objects {
              file_name
            }
          }
        }
    """

    result = graphapi_post(query, variables={"substring": "report"})
    assert result.errors is None
    assert {f["file_name"] for f in result.data["files"]["objects"]} == {
        "report.csv",
        "Report.txt",
    }

    result = graphapi_post(query, variables={"substring": "MARY"})
    assert result.errors is None
    assert {f["file_name"] for f in result.data["files"]["objects"]} == {"summary.csv"}

    result = graphapi_post(query, variables={"substring": "missing"})
    assert result.errors is None
    assert result.data["files"]["objects"] == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_list_files(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that we get the filenames of the files in the file store."""
    query = """
        query Files {
          files(filter: {file_store: EXPORTS}) {
            objects {
              file_name
            }
          }
        }
    """

    # No files have been uploaded yet
    result = graphapi_post(query)
    assert result.errors is None
    assert result.data["files"]["objects"] == []

    assert upload_file("filename.csv", b"I'm a file").errors is None

    result = graphapi_post(query)
    assert result.errors is None
    assert result.data["files"]["objects"] == [{"file_name": "filename.csv"}]

    assert upload_file("file2", b"test").errors is None

    result = graphapi_post(query)
    assert result.errors is None
    assert {f["file_name"] for f in result.data["files"]["objects"]} == {
        "filename.csv",
        "file2",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "file_names,expected",
    [
        # A single file
        (["report.csv"], {"report.csv"}),
        # Multiple files
        (["report.csv", "notes.txt"], {"report.csv", "notes.txt"}),
        # Nonexistent files are simply not returned
        (["whatever"], set()),
        (["report.csv", "whatever"], {"report.csv"}),
        # An empty list is no filter at all, rather than a filter matching nothing
        ([], {"report.csv", "summary.csv", "notes.txt"}),
        (None, {"report.csv", "summary.csv", "notes.txt"}),
    ],
)
async def test_file_names_filter(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
    file_names: list[str] | None,
    expected: set[str],
) -> None:
    """Ensure the `file_names` filter returns exactly the requested files."""
    for filename in ("report.csv", "summary.csv", "notes.txt"):
        assert upload_file(filename, b"data").errors is None

    query = """
        query Files($file_names: [String!]) {
          files(filter: {file_store: EXPORTS, file_names: $file_names}) {
            objects {
              file_name
            }
          }
        }
    """

    result = graphapi_post(query, variables={"file_names": file_names})
    assert result.errors is None
    assert {f["file_name"] for f in result.data["files"]["objects"]} == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_read_file_contents(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that we can read the contents of an uploaded file."""
    filename = "filename.csv"
    content = b"I'm a file"
    assert upload_file(filename, content).errors is None

    query = """
        query File($file_name: String!) {
          files(filter: {file_store: EXPORTS, file_names: [$file_name]}) {
            objects {
              file_name
              base64_contents
              text_contents
            }
          }
        }
    """

    result = graphapi_post(query, variables={"file_name": filename})
    assert result.errors is None
    assert result.data["files"]["objects"] == [
        {
            "file_name": filename,
            "base64_contents": b64encode(content).decode("ascii"),
            "text_contents": content.decode("utf-8"),
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_read_binary_file_contents(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that binary files can be read through `base64_contents`."""
    filename = "binary.bin"
    content = bytes(range(256))
    assert upload_file(filename, content).errors is None

    query = """
        query File($file_name: String!) {
          files(filter: {file_store: EXPORTS, file_names: [$file_name]}) {
            objects {
              base64_contents
            }
          }
        }
    """

    result = graphapi_post(query, variables={"file_name": filename})
    assert result.errors is None
    assert result.data["files"]["objects"] == [
        {"base64_contents": b64encode(content).decode("ascii")}
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_file_stores_are_separate(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that files are only visible in the file store they were uploaded to."""
    filename = "filename.csv"
    assert upload_file(filename, b"exports", file_store="EXPORTS").errors is None
    assert upload_file(filename, b"insights", file_store="INSIGHTS").errors is None

    query = """
        query File($file_store: FileStore!, $file_name: String!) {
          files(filter: {file_store: $file_store, file_names: [$file_name]}) {
            objects {
              text_contents
            }
          }
        }
    """

    result = graphapi_post(
        query, variables={"file_store": "EXPORTS", "file_name": filename}
    )
    assert result.errors is None
    assert result.data["files"]["objects"] == [{"text_contents": "exports"}]

    result = graphapi_post(
        query, variables={"file_store": "INSIGHTS", "file_name": filename}
    )
    assert result.errors is None
    assert result.data["files"]["objects"] == [{"text_contents": "insights"}]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_upload_file_already_exists(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that we cannot upload files if they already exist."""
    filename = "filename.csv"
    assert upload_file(filename, b"I'm a file").errors is None

    result = upload_file(filename, b"bar")
    assert result.errors is not None
    error = one(result.errors)
    assert error["message"] == "ErrorCodes.E_ALREADY_EXISTS"
    assert error["extensions"]["error_context"] == {
        "description": "File already exists.",
        "error": True,
        "error_key": "E_ALREADY_EXISTS",
        "filename": filename,
        "status": HTTP_409_CONFLICT,
    }

    # The original file is untouched
    query = """
        query File($file_name: String!) {
          files(filter: {file_store: EXPORTS, file_names: [$file_name]}) {
            objects {
              text_contents
            }
          }
        }
    """
    read = graphapi_post(query, variables={"file_name": filename})
    assert read.errors is None
    assert read.data["files"]["objects"] == [{"text_contents": "I'm a file"}]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_upload_file_force(
    upload_file: UploadFile,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that we can upload files with force, even if a file exists."""
    filename = "filename.csv"
    assert upload_file(filename, b"I'm a file").errors is None

    result = upload_file(filename, b"bar", force=True)
    assert result.errors is None
    assert result.data == {"upload_file": "OK"}

    # The file has been overwritten, and not duplicated
    query = """
        query File($file_name: String!) {
          files(filter: {file_store: EXPORTS, file_names: [$file_name]}) {
            objects {
              text_contents
            }
          }
        }
    """
    read = graphapi_post(query, variables={"file_name": filename})
    assert read.errors is None
    assert read.data["files"]["objects"] == [{"text_contents": "bar"}]
