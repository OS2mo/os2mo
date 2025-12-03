# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from mora.graphapi.custom_router import DEPRECATION_NOTICE


@pytest.mark.parametrize(
    "url,deprecated",
    [
        ("/graphql", False),
        ("/graphql/v18", True),
        ("/graphql/v19", True),
        ("/graphql/v20", True),
        ("/graphql/v21", True),
        ("/graphql/v22", True),
        ("/graphql/v23", True),
        ("/graphql/v24", True),
        ("/graphql/v25", False),
    ],
)
def test_graphiql_overrides(
    service_client: TestClient, url: str, deprecated: bool
) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == 200
    html_response = response.text
    if deprecated:
        assert DEPRECATION_NOTICE in html_response
    else:
        assert DEPRECATION_NOTICE not in html_response
