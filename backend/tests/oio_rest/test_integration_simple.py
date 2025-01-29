# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient

UUID_PATTERN = "{uuid}"
CONTENT_PATH_PATTERN = "{content_path}"


def test_site_map(raw_client: TestClient) -> None:
    response = raw_client.get("/lora/site-map")
    assert response.status_code == 200
    assert response.json() == {
        "site-map": [
            "/",
            "/klassifikation/classes",
            "/klassifikation/facet",
            "/klassifikation/facet/fields",
            "/klassifikation/facet/schema",
            "/klassifikation/facet/" + UUID_PATTERN,
            "/klassifikation/klasse",
            "/klassifikation/klasse/fields",
            "/klassifikation/klasse/schema",
            "/klassifikation/klasse/" + UUID_PATTERN,
            "/klassifikation/klassifikation",
            "/klassifikation/klassifikation/fields",
            "/klassifikation/klassifikation/schema",
            "/klassifikation/klassifikation/" + UUID_PATTERN,
            # "/metrics",
            "/organisation/bruger",
            "/organisation/bruger/fields",
            "/organisation/bruger/schema",
            "/organisation/bruger/" + UUID_PATTERN,
            "/organisation/classes",
            "/organisation/itsystem",
            "/organisation/itsystem/fields",
            "/organisation/itsystem/schema",
            "/organisation/itsystem/" + UUID_PATTERN,
            "/organisation/organisation",
            "/organisation/organisation/fields",
            "/organisation/organisation/schema",
            "/organisation/organisation/" + UUID_PATTERN,
            "/organisation/organisationenhed",
            "/organisation/organisationenhed/fields",
            "/organisation/organisationenhed/schema",
            "/organisation/organisationenhed/" + UUID_PATTERN,
            "/organisation/organisationfunktion",
            "/organisation/organisationfunktion/fields",
            "/organisation/organisationfunktion/schema",
            "/organisation/organisationfunktion/" + UUID_PATTERN,
            "/site-map",
        ]
    }


UUID_ENDPOINTS = [
    "/klassifikation/facet",
    "/klassifikation/klasse",
    "/klassifikation/klassifikation",
    "/organisation/bruger",
    "/organisation/itsystem",
    "/organisation/organisation",
    "/organisation/organisationenhed",
    "/organisation/organisationfunktion",
]


def test_uuid_endpoints(raw_client: TestClient) -> None:
    response = raw_client.get("/lora/site-map")
    assert response.status_code == 200
    site_map = response.json()["site-map"]

    endpoints = [
        endpoint.rsplit("/", 1)[0]
        for endpoint in site_map
        if endpoint.endswith(UUID_PATTERN)
    ]
    assert endpoints == UUID_ENDPOINTS


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("endpoint", UUID_ENDPOINTS)
def test_finding_nothing(raw_client: TestClient, endpoint: str) -> None:
    response = raw_client.get("/lora" + endpoint, params={"bvn": "%"})
    assert response.status_code == 200
    assert response.json() == {"results": [[]]}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "endpoint,params",
    [
        ("/lora/klassifikation/klasse", {"facet": "invalid"}),
        ("/lora/organisation/organisation", {"tilhoerer": "invalid"}),
        ("/lora/organisation/organisation", {"virkningfra": "xyz"}),
    ],
)
def test_on_value_errors(
    service_client_not_raising: TestClient, endpoint: str, params: dict[str, str]
) -> None:
    response = service_client_not_raising.get(endpoint, params=params)
    assert response.status_code in (400, 500)
