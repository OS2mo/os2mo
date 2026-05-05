# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from starlette.testclient import TestClient


def test_version_enum_incomparable_to_int() -> None:
    with pytest.raises(
        TypeError,
        match="'>' not supported between instances of 'Version' and 'int'",
    ):
        assert LATEST_VERSION > 1


def test_unversioned_get_redirects_to_latest(raw_client: TestClient) -> None:
    response = raw_client.get("/graphql", follow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == f"/graphql/v{LATEST_VERSION.value}"


def test_non_existent(raw_client: TestClient) -> None:
    # Non-existent versions are not found
    assert raw_client.get("/graphql/v1").status_code == 404
    # Active versions are found
    for version in Version:
        assert raw_client.get(f"/graphql/v{version.value}").status_code == 200
