# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient


UUID_PATTERN = "{uuid}"
CONTENT_PATH_PATTERN = "{content_path}"


def test_site_map(lora_client: TestClient) -> None:
    response = lora_client.get("/site-map")
    assert response.status_code == 200
    assert response.json() == {
        "site-map": [
            "/",
            "/autocomplete/bruger",
            "/autocomplete/organisationsenhed",
            "/docs",
            "/docs/oauth2-redirect",
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
            "/kubernetes/live",
            "/kubernetes/ready",
            # "/metrics",
            "/openapi.json",
            "/organisation/bruger",
            "/organisation/bruger/fields",
            "/organisation/bruger/schema",
            "/organisation/bruger/" + UUID_PATTERN,
            "/organisation/classes",
            "/organisation/interessefaellesskab",
            "/organisation/interessefaellesskab/fields",
            "/organisation/interessefaellesskab/schema",
            "/organisation/interessefaellesskab/" + UUID_PATTERN,
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
            "/redoc",
            "/site-map",
            "/version",
        ]
    }


UUID_ENDPOINTS = [
    "/klassifikation/facet",
    "/klassifikation/klasse",
    "/klassifikation/klassifikation",
    "/organisation/bruger",
    "/organisation/interessefaellesskab",
    "/organisation/itsystem",
    "/organisation/organisation",
    "/organisation/organisationenhed",
    "/organisation/organisationfunktion",
]


def test_uuid_endpoints(lora_client: TestClient) -> None:
    response = lora_client.get("/site-map")
    assert response.status_code == 200
    site_map = response.json()["site-map"]

    endpoints = [
        endpoint.rsplit("/", 1)[0]
        for endpoint in site_map
        if endpoint.endswith(UUID_PATTERN)
    ]
    assert endpoints == UUID_ENDPOINTS


@pytest.mark.integration_test
@pytest.mark.usefixtures("testing_db")
@pytest.mark.parametrize("endpoint", UUID_ENDPOINTS)
def test_finding_nothing(lora_client: TestClient, endpoint: str) -> None:
    response = lora_client.get(endpoint, params={"bvn": "%"})
    assert response.status_code == 200
    assert response.json() == {"results": [[]]}


@pytest.mark.integration_test
@pytest.mark.usefixtures("testing_db")
@pytest.mark.parametrize(
    "endpoint,params",
    [
        ("/klassifikation/klasse", {"facet": "invalid"}),
        ("/organisation/organisation", {"tilhoerer": "invalid"}),
        ("/organisation/organisation", {"virkningfra": "xyz"}),
    ],
)
def test_return_400_on_value_errors(
    lora_client: TestClient, endpoint: str, params: dict[str, str]
) -> None:
    response = lora_client.get(endpoint, params=params)
    assert response.status_code == 400
