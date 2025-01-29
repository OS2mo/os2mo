# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.graphapi.main import newest
from starlette.testclient import TestClient


def test_unversioned_get_redirects_to_newest(raw_client: TestClient) -> None:
    response = raw_client.get("/graphql", follow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == f"/graphql/v{newest}"


def test_non_existent(raw_client: TestClient) -> None:
    # Previous (now non-existent) versions are GONE
    assert raw_client.get("/graphql/v1").status_code == 410
    # Active versions are found
    assert raw_client.get(f"/graphql/v{newest}").status_code == 200
    # Future versions are NOT FOUND
    assert raw_client.get(f"/graphql/v{newest + 1}").status_code == 404
