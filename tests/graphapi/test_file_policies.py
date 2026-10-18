# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of files are guarded by read policies."""

from base64 import b64encode
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import Collection
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules
from tests.conftest import UploadFile


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_reads_the_fields_of_a_file(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, upload_file: UploadFile
) -> None:
    """A reader reads every field of a file."""
    content = b"Year,Model,Make\n1997,Ford,E350\n"
    # Uploaded as the admin, before the caller is switched
    assert upload_file("report.csv", content).errors is None
    set_auth({"reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          files(filter: { file_store: EXPORTS }) {
            objects { file_store file_name text_contents base64_contents }
          }
        }
        """
    )

    assert response.errors is None
    assert response.data == {
        "files": {
            "objects": [
                {
                    "file_store": "EXPORTS",
                    "file_name": "report.csv",
                    "text_contents": content.decode(),
                    "base64_contents": b64encode(content).decode(),
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_file_field_no_rule_grants_is_denied(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    upload_file: UploadFile,
) -> None:
    """A field of a file no rule grants is denied where it is read."""
    # Uploaded as the admin, before the caller is switched
    assert upload_file("report.csv", b"data").errors is None
    await set_rules("policy_reader", Collection.File, {"file_name"})
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          files(filter: { file_store: EXPORTS }) { objects { file_name text_contents } }
        }
        """
    )

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["files", "objects", 0, "text_contents"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_file_gets_the_fields_of_the_rules_matching_it(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    upload_file: UploadFile,
) -> None:
    """A file is matched by its filter, telling it apart from other files."""
    # Uploaded as the admin, before the caller is switched
    for file_store, file_name in [
        ("INSIGHTS", "report.csv"),
        ("INSIGHTS", "annual.csv"),
        ("EXPORTS", "report.csv"),
    ]:
        content = f"{file_store}/{file_name}".encode()
        assert upload_file(file_name, content, file_store=file_store).errors is None

    # Files are paged by an opaque key, so read the order `annual.csv` lands in
    # while the admin may still read every file
    insights = graphapi_post(
        """
        query {
          files(filter: { file_store: INSIGHTS }) { objects { file_name } }
        }
        """
    )
    assert insights.errors is None
    denied_index = [f["file_name"] for f in insights.data["files"]["objects"]].index(
        "annual.csv"
    )

    await set_rules(
        "policy_reader",
        Collection.File,
        {"text_contents"},
        condition='{"file_store": "INSIGHTS", "file_names": ["report.csv"]}',
    )
    set_auth({"policy_reader"}, uuid4())
    query = """
        query ReadFiles($file_store: FileStore!, $file_names: [String!]) {
          files(filter: { file_store: $file_store, file_names: $file_names }) {
            objects { text_contents }
          }
        }
    """

    response = graphapi_post(
        query, variables={"file_store": "INSIGHTS", "file_names": ["report.csv"]}
    )
    assert response.errors is None
    assert response.data == {
        "files": {"objects": [{"text_contents": "INSIGHTS/report.csv"}]}
    }

    # Files are told apart from files of the same name in another store
    response = graphapi_post(
        query, variables={"file_store": "EXPORTS", "file_names": ["report.csv"]}
    )
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["files", "objects", 0, "text_contents"]

    # Files are told apart from files of another name in the same store
    response = graphapi_post(query, variables={"file_store": "INSIGHTS"})
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["files", "objects", denied_index, "text_contents"]
