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


GRANTED_FILES = """
    query GrantedFiles($granted: Boolean) {
      files(filter: { file_store: INSIGHTS, granted: $granted }) {
        objects { file_name }
      }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_files_are_filtered_by_whether_a_rule_grants_them(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    upload_file: UploadFile,
) -> None:
    """Filtering by granted tells the files a rule grants apart from the rest."""
    # Uploaded as the admin, before the caller is switched
    for file_name in ["report.csv", "annual.csv"]:
        assert upload_file(file_name, b"data", file_store="INSIGHTS").errors is None

    await set_rules(
        "policy_reader",
        Collection.File,
        {"file_name"},
        condition='{"file_store": "INSIGHTS", "file_names": ["report.csv"]}',
    )
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(GRANTED_FILES, variables={"granted": True})
    assert response.errors is None
    assert response.data == {"files": {"objects": [{"file_name": "report.csv"}]}}

    # The fields of a file no rule grants are denied, so tell the files apart by
    # narrowing the filter to each in turn
    query = """
        query GrantedFiles($file_names: [String!], $granted: Boolean) {
          files(
            filter: { file_store: INSIGHTS, file_names: $file_names, granted: $granted }
          ) {
            objects { file_name }
          }
        }
    """
    response = graphapi_post(
        query, variables={"file_names": ["report.csv"], "granted": False}
    )
    assert response.errors is None
    assert response.data == {"files": {"objects": []}}

    response = graphapi_post(
        query, variables={"file_names": ["annual.csv"], "granted": False}
    )
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["files", "objects", 0, "file_name"]

    # Without the filter, both files are included, so one is denied
    response = graphapi_post(
        """
        query {
          files(filter: { file_store: INSIGHTS }) { objects { file_name } }
        }
        """
    )
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"][:2] == ["files", "objects"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_no_files_are_granted_without_a_rule(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, upload_file: UploadFile
) -> None:
    """Filtering by granted includes no files, when no rule names the collection."""
    # Uploaded as the admin, before the caller is switched
    assert upload_file("report.csv", b"data", file_store="INSIGHTS").errors is None
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(GRANTED_FILES, variables={"granted": True})

    assert response.errors is None
    assert response.data == {"files": {"objects": []}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "granted,file_names",
    [
        (True, {"report.csv", "annual.csv"}),
        (False, set()),
    ],
)
async def test_every_file_is_granted_to_an_admin(
    graphapi_post: GraphAPIPost,
    upload_file: UploadFile,
    granted: bool,
    file_names: set[str],
) -> None:
    """Filtering by granted treats every file as granted to an admin."""
    for file_name in ["report.csv", "annual.csv"]:
        assert upload_file(file_name, b"data", file_store="INSIGHTS").errors is None

    response = graphapi_post(GRANTED_FILES, variables={"granted": granted})

    assert response.errors is None
    assert {f["file_name"] for f in response.data["files"]["objects"]} == file_names


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_granted_rejects_null(graphapi_post: GraphAPIPost) -> None:
    """Filtering by granted rejects `null`, which is neither omitted, true nor false."""
    response = graphapi_post(GRANTED_FILES, variables={"granted": None})

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "The granted filter must be omitted, true or false"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "condition,granted_file_names",
    [
        ("true", {"report.csv", "annual.csv", "monthly-report.csv"}),
        ("false", set()),
        ('{"file_store": "INSIGHTS", "file_names": ["report.csv"]}', {"report.csv"}),
        (
            '{"file_store": "INSIGHTS", "file_name_contains": "REPORT"}',
            {"report.csv", "monthly-report.csv"},
        ),
        ('{"file_store": "EXPORTS"}', set()),
    ],
)
async def test_every_file_is_either_granted_or_not(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    upload_file: UploadFile,
    condition: str,
    granted_file_names: set[str],
) -> None:
    """Filtering by granted and by not granted splits the files between them.

    `granted: false` negates the conditions of the rules, so a condition which is
    NULL, rather than false, for a file would drop it from both.
    """
    file_names = {"report.csv", "annual.csv", "monthly-report.csv"}
    # Uploaded as the admin, before the caller is switched
    for file_name in file_names:
        assert upload_file(file_name, b"data", file_store="INSIGHTS").errors is None

    await set_rules("policy_reader", Collection.File, {"file_name"}, condition)
    set_auth({"policy_reader"}, uuid4())

    def is_included(file_name: str, granted: bool) -> bool:
        # The fields of a file no rule grants are denied, so narrow the filter to
        # the file and tell whether it is included by whether it is denied
        response = graphapi_post(
            """
            query GrantedFiles($file_names: [String!], $granted: Boolean) {
              files(
                filter: {
                  file_store: INSIGHTS, file_names: $file_names, granted: $granted
                }
              ) {
                objects { file_name }
              }
            }
            """,
            variables={"file_names": [file_name], "granted": granted},
        )
        if response.errors is None:
            return response.data == {"files": {"objects": [{"file_name": file_name}]}}
        error = one(response.errors)
        assert error["message"] == "No policy approved the access"
        assert error["path"] == ["files", "objects", 0, "file_name"]
        return True

    included = {
        file_name: (is_included(file_name, True), is_included(file_name, False))
        for file_name in file_names
    }
    assert included == {
        file_name: (
            file_name in granted_file_names,
            file_name not in granted_file_names,
        )
        for file_name in file_names
    }
