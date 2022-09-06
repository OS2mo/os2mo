# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest

import requests
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_endpoints_depend_on_oidc_auth_function,
)
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_no_auth_endpoints_do_not_depend_on_auth_function,
)
from parameterized import parameterized
from starlette.status import HTTP_401_UNAUTHORIZED

from oio_rest import config
from oio_rest.app import create_app
from oio_rest.auth.oidc import auth
from oio_rest.tests.util import DBTestCase


class TestEndpointAuthDependency(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        self.no_auth_endpoints = [
            "/",
            "/kubernetes/live",
            "/kubernetes/ready",
            "/metrics",
            "/site-map",
            "/version",
        ]
        self.all_routes = app.routes
        self.auth_coroutine = auth

    def test_ensure_endpoints_depend_on_oidc_auth_function(self):
        ensure_endpoints_depend_on_oidc_auth_function(
            self.all_routes, self.no_auth_endpoints, auth
        )

    def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(self):
        ensure_no_auth_endpoints_do_not_depend_on_auth_function(
            self.all_routes, self.no_auth_endpoints, auth
        )


class TestAuthEndpoints(DBTestCase):
    """
    Keycloak integration tests
    """

    def setUp(self) -> None:
        super().setUp()
        # Enable the real Keycloak auth mechanism in order to perform Keycloak
        # integration tests
        self.app.dependency_overrides = dict()

    @parameterized.expand(
        [
            "/autocomplete/bruger",
            "/autocomplete/organisationsenhed",
            "/klassifikation/facet",
            "/klassifikation/facet/fields",
            "/klassifikation/facet/schema",
            "/klassifikation/facet/{uuid}",
            "/klassifikation/klasse",
            "/klassifikation/klasse/fields",
            "/klassifikation/klasse/schema",
            "/klassifikation/klasse/{uuid}",
            "/klassifikation/klassifikation",
            "/klassifikation/klassifikation/fields",
            "/klassifikation/klassifikation/schema",
            "/klassifikation/klassifikation/{uuid}",
            "/klassifikation/classes",
            "/organisation/bruger",
            "/organisation/bruger/fields",
            "/organisation/bruger/schema",
            "/organisation/bruger/{uuid}",
            "/organisation/interessefaellesskab",
            "/organisation/interessefaellesskab/fields",
            "/organisation/interessefaellesskab/schema",
            "/organisation/interessefaellesskab/{uuid}",
            "/organisation/itsystem",
            "/organisation/itsystem/fields",
            "/organisation/itsystem/schema",
            "/organisation/itsystem/{uuid}",
            "/organisation/organisation",
            "/organisation/organisation/fields",
            "/organisation/organisation/schema",
            "/organisation/organisation/{uuid}",
            "/organisation/organisationenhed",
            "/organisation/organisationenhed/fields",
            "/organisation/organisationenhed/schema",
            "/organisation/organisationenhed/{uuid}",
            "/organisation/organisationfunktion",
            "/organisation/organisationfunktion/fields",
            "/organisation/organisationfunktion/schema",
            "/organisation/organisationfunktion/{uuid}",
            "/organisation/classes",
        ]
    )
    def test_401_for_endpoint_when_no_token(self, url_path: str):
        # Sufficient to test all the GET endpoints
        self.assertRequestFails(url_path, code=HTTP_401_UNAUTHORIZED)

    def test_200_for_valid_token(self):
        # Get token from Keycloak
        settings = config.get_settings()

        token_url = (
            f"{settings.keycloak_schema}://{settings.keycloak_host}"
            f":{settings.keycloak_port}/auth/realms/{settings.keycloak_realm}"
            f"/protocol/openid-connect/token"
        )

        r = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                # "mo" is no longer a client of the "lora" Keycloak realm:
                # "client_id": "mo",
                # "client_secret": "158a2075-aa8a-421c-94a4-2df35377014a",
                # ... but "dipex" still is:
                "client_id": "dipex",
                "client_secret": "a091ed82-6e82-4efc-a8f0-001e2b127853",
            },
        )

        token = r.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}

        # Send request with auth header to LoRa

        self.assertOK(
            self.perform_request(
                "/organisation/organisationenhed/fields", headers=headers
            )
        )
