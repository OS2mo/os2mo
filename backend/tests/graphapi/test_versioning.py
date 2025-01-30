# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.graphapi.main import graphql_versions
from mora.graphapi.main import latest_graphql_version
from starlette.testclient import TestClient


def test_unversioned_get_redirects_to_latest(raw_client: TestClient) -> None:
    response = raw_client.get("/graphql", follow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == f"/graphql/v{latest_graphql_version}"


def test_non_existent(raw_client: TestClient) -> None:
    # Non-existent versions are NOT FOUND
    assert raw_client.get("/graphql/v1").status_code == 404
    # Active versions are found
    for version in graphql_versions:
        assert raw_client.get(f"/graphql/v{version}").status_code == 200
