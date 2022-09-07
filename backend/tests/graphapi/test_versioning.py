# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import itertools
from datetime import date
from typing import Type

import freezegun
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from mora.auth.keycloak.oidc import auth
from mora.graphapi.main import graphql_versions
from mora.graphapi.main import setup_graphql
from mora.graphapi.versions.base import BaseGraphQLVersion
from mora.graphapi.versions.latest.version import LatestGraphQLVersion
from tests.cases import fake_auth


def get_test_client(
    versions: list[Type[BaseGraphQLVersion]] | None = None,
) -> TestClient:
    app = FastAPI()
    app.dependency_overrides[auth] = fake_auth
    setup_graphql(app, enable_graphiql=True, versions=versions)
    return TestClient(app)


@pytest.fixture()
def test_client() -> TestClient:
    yield get_test_client()


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


def test_all_previous_versions_have_deprecation_date():
    """All but the last should have a deprecation date."""
    *previous_versions, last_version = graphql_versions

    for version in previous_versions:
        assert version.deprecation_date is not None
    assert last_version.deprecation_date is None


def test_increasing_deprecation_date():
    for a, b in itertools.pairwise(graphql_versions[:-1]):
        assert b.deprecation_date > a.deprecation_date


def test_unversioned_get_redirects_to_newest(test_client: TestClient):
    newest = graphql_versions[-1]
    response = test_client.get("/graphql", allow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == f"/graphql/v{newest.version}"


@freezegun.freeze_time("2022-02-02")
def test_deprecated_version_not_routed():
    class DeprecatedGraphQLVersion(LatestGraphQLVersion):
        version = 1
        deprecation_date = date(2021, 1, 1)  # in the past

    test_client = get_test_client(
        versions=[
            DeprecatedGraphQLVersion,
        ]
    )
    response = test_client.get("/graphql/v1")
    assert response.status_code == 410


def test_non_existent():
    class ActiveGraphQLVersion(LatestGraphQLVersion):
        version = 2

    test_client = get_test_client(
        versions=[
            ActiveGraphQLVersion,
        ]
    )
    # Previous (now non-existent) versions are GONE
    assert test_client.get("/graphql/v1").status_code == 410
    # Active versions resolve
    assert test_client.get("/graphql/v2").status_code == 200
    # Future versions are NOT FOUND
    assert test_client.get("/graphql/v3").status_code == 404


def test_legacy_endpoint_works(test_client: TestClient):
    """TODO: This should be removed ASAP when everything is migrated."""
    response = test_client.post("/graphql", json={"query": "Query {}"})
    assert response
