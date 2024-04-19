# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from more_itertools import first
from starlette.testclient import TestClient

from mora.app import create_app
from mora.graphapi.main import graphql_versions
from mora.graphapi.main import newest


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
    assert raw_client.get(f"/graphql/v{newest+1}").status_code == 404


def test_min_graphql_version() -> None:
    oldest = first(graphql_versions)
    minimum = 4  # chosen by fair dice roll, guaranteed to be random

    app = create_app(settings_overrides={"min_graphql_version": minimum})
    with TestClient(app) as raw_client:
        # Previous (now non-existent) versions are GONE
        assert raw_client.get("/graphql/v1").status_code == 410
        # All versions above oldest, below minimum are GONE
        for version in range(oldest, minimum):
            assert raw_client.get(f"/graphql/v{version}").status_code == 410
        # All versions above minimum, below newest are found
        for version in range(minimum, newest):
            assert raw_client.get(f"/graphql/v{version}").status_code == 200
        # Newest version is found
        assert raw_client.get(f"/graphql/v{newest}").status_code == 200
        # Future versions are NOT FOUND
        assert raw_client.get(f"/graphql/v{newest+1}").status_code == 404
