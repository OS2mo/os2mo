# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Reading the fields of files."""

from base64 import b64encode
from uuid import uuid4

import pytest

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
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
