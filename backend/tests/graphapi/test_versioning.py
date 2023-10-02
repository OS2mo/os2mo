# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import itertools

from starlette.testclient import TestClient

from mora.graphapi.main import graphql_versions
from mora.graphapi.versions.latest.version import LatestGraphQLVersion


def test_latest_not_exposed_directly():
    """The latest version should never be exposed directly, as we want clients to pin to
    a specific one."""
    assert LatestGraphQLVersion not in graphql_versions


def test_all_versions_have_version_number():
    for version in graphql_versions:
        assert isinstance(version.version, int)


def test_increasing_version_numbers():
    for a, b in itertools.pairwise(graphql_versions):
        assert b.version == a.version + 1


def test_unversioned_get_redirects_to_newest(raw_client: TestClient):
    newest = graphql_versions[-1]
    response = raw_client.get("/graphql", follow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == f"/graphql/v{newest.version}"


def test_non_existent(raw_client: TestClient):
    # Previous (now non-existent) versions are GONE
    assert raw_client.get("/graphql/v1").status_code == 410
    # Active versions resolve
    newest = graphql_versions[-1]
    assert raw_client.get(f"/graphql/v{newest.version}").status_code == 200
    # Future versions are NOT FOUND
    assert raw_client.get(f"/graphql/v{newest.version+1}").status_code == 404
