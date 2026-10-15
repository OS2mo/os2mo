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

CONTENT = b"Year,Model,Make\n1997,Ford,E350\n"


@pytest.fixture
def exported_file(upload_file: UploadFile) -> None:
    """A file in the exports, uploaded by an admin."""
    assert upload_file("report.csv", CONTENT).errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "exported_file")
async def test_a_reader_reads_the_fields_of_a_file(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    """The seeded Reader policy grants a reader what the role used to."""
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
                    "text_contents": CONTENT.decode(),
                    "base64_contents": b64encode(CONTENT).decode(),
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "exported_file")
async def test_a_file_field_no_rule_grants_is_denied(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_rules: SetRules
) -> None:
    """A field of a file no rule grants is denied where it is read."""
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
@pytest.mark.usefixtures("empty_db", "exported_file")
async def test_a_rule_naming_one_file_grants_nothing_on_another(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    upload_file: UploadFile,
) -> None:
    """A rule naming one file grants nothing on another listed beside it.

    The file uploaded last is listed first, so files keyed by their place in the
    listing, rather than by themselves, would trade their grants.
    """
    # Uploaded as the admin, before the caller is switched
    assert upload_file("annual.csv", CONTENT).errors is None
    await set_rules(
        "policy_reader",
        Collection.File,
        {"text_contents"},
        condition='{"file_store": "EXPORTS", "file_names": ["report.csv"]}',
    )
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(
        """
        query {
          files(filter: { file_store: EXPORTS }) { objects { text_contents } }
        }
        """
    )

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["files", "objects", 0, "text_contents"]
