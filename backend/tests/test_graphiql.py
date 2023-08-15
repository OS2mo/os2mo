# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient

from mora.graphapi.router import AUTH_SCRIPT
from mora.graphapi.router import DEPRECATION_NOTICE


@pytest.mark.parametrize(
    "url,deprecated",
    [
        ("/graphql", False),
        ("/graphql/v2", True),
        ("/graphql/v3", True),
        ("/graphql/v4", True),
        ("/graphql/v5", True),
        ("/graphql/v6", True),
        ("/graphql/v7", True),
        ("/graphql/v8", True),
        ("/graphql/v9", True),
        ("/graphql/v10", False),
    ],
)
def test_graphiql_overrides(
    service_client: TestClient, url: str, deprecated: bool
) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == 200
    html_response = response.text
    assert AUTH_SCRIPT in html_response
    if deprecated:
        assert DEPRECATION_NOTICE in html_response
    else:
        assert DEPRECATION_NOTICE not in html_response
