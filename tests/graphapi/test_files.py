# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_file_name_contains_filter(
    upload_file: Callable[[str, bytes], None],
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure the `file_name_contains` filter returns case-insensitive substring matches."""
    for filename in ("report.csv", "Report.txt", "summary.csv"):
        upload_file(filename, b"data")

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
