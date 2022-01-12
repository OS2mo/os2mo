# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest.mock

from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_endpoints_depend_on_oidc_auth_function,
)
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_no_auth_endpoints_do_not_depend_on_auth_function,
)
from pydantic import MissingError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_401_UNAUTHORIZED

import tests.cases
from mora import main
from mora.auth.keycloak.models import KeycloakToken
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from tests import util


class TestEndpointAuthDependency(unittest.TestCase):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """

    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    def setUp(self) -> None:
        self.no_auth_endpoints = (
            "/health/amqp",
            "/health/oio_rest",
            "/health/configuration_database",
            "/health/dataset",
            "/health/dar",
            "/health/keycloak",
            "/health/live",
            "/health/ready",
            "/health/",
            "/version/",
            "/forespoergsler/",
            "/organisationssammenkobling/",
            "/medarbejder/{path:path}",
            "/medarbejder/",
            "/organisation/{path:path}",
            "/organisation/",
            "/",
            "/favicon.ico",
            "/indsigt",
            "/service/keycloak.json",
            "/service/token",
            "/service/{rest_of_path:path}",
            "/testing/testcafe-db-setup",
            "/testing/testcafe-db-teardown",
            "/metrics",
        )
        self.all_routes = main.app.routes
        self.auth_coroutine = auth

    def test_ensure_endpoints_depend_on_oidc_auth_function(self):
        ensure_endpoints_depend_on_oidc_auth_function(
            self.all_routes, self.no_auth_endpoints, self.auth_coroutine
        )

    def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(self):
        ensure_no_auth_endpoints_do_not_depend_on_auth_function(
            self.all_routes, self.no_auth_endpoints, self.auth_coroutine
        )


class TestAuthEndpointsReturn401(tests.cases.TestCase):

    app_settings_overrides = {
        "v1_api_enable": True,
        "graphql_enable": True,
    }

    def setUp(self):
        super().setUp()
        # Enable the real OIDC auth function
        self.app.dependency_overrides = dict()

    def test_auth_service_address(self):
        self.assertRequestFails(
            "/service/e/00000000-0000-0000-0000-000000000000/details/address",
            HTTP_401_UNAUTHORIZED,
        )

    def test_auth_service_cpr(self):
        self.assertRequestFails("/service/e/cpr_lookup/?q=1234", HTTP_401_UNAUTHORIZED)

    def test_auth_service_details_reading(self):
        self.assertRequestFails(
            "/service/e/00000000-0000-0000-0000-000000000000/details/",
            HTTP_401_UNAUTHORIZED,
        )

    def test_auth_service_details_writing(self):
        self.assertRequestResponse(
            "/service/details/create",
            "Not authenticated",
            status_code=HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    def test_auth_service_employee(self):
        self.assertRequestFails(
            "/service/o/00000000-0000-0000-0000-000000000000/e/", HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_exports(self):
        self.assertRequestFails("/service/exports/not-important", HTTP_401_UNAUTHORIZED)

    def test_auth_service_facets(self):
        self.assertRequestFails("/service/c/ancestor-tree", HTTP_401_UNAUTHORIZED)

    def test_auth_service_integration_data(self):
        self.assertRequestFails(
            "/service/ou" "/00000000-0000-0000-0000-000000000000/integration-data",
            HTTP_401_UNAUTHORIZED,
        )

    def test_auth_service_itsystem(self):
        self.assertRequestFails(
            "/service/o/00000000-0000-0000-0000-000000000000/it/", HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_kle(self):
        # KLE router not used anywhere?
        pass

    def test_auth_service_org(self):
        self.assertRequestFails("/service/o/", HTTP_401_UNAUTHORIZED)

    def test_auth_service_orgunit(self):
        self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/children",
            HTTP_401_UNAUTHORIZED,
        )

    def test_auth_service_related(self):
        self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/map",
            HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    def test_auth_service_configuration(self):
        self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/configuration",
            HTTP_401_UNAUTHORIZED,
        )

    def test_auth_service_validate(self):
        self.assertRequestFails(
            "/service/validate/org-unit/",
            HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    def test_auth_api_v1(self):
        self.assertRequestFails("/api/v1/it", HTTP_401_UNAUTHORIZED)

    def test_auth_graphql(self):
        self.assertRequestFails("/graphql", HTTP_401_UNAUTHORIZED)


class TestAuthEndpointsReturn2xx(tests.cases.LoRATestCase):
    """
    Keycloak integration tests of a few endpoints (one from /service endpoints
    and one from the /api/v1 endpoints)
    """

    app_settings_overrides = {"v1_api_enable": True}

    def setUp(self):
        super().setUp()
        # Enable the real Keycloak auth mechanism in order to perform Keycloak
        # integration tests
        self.app.dependency_overrides = dict()

    def test_auth_service_org(self):
        self.load_sample_structures(minimal=True)
        self.assertRequest("/service/o/", HTTP_200_OK, set_auth_header=True)

    def test_auth_api_v1(self):
        self.assertRequest("/api/v1/it", HTTP_200_OK, set_auth_header=True)

    def test_auth_graphql(self):
        self.assertRequest("/graphql", HTTP_200_OK, set_auth_header=True)

    def test_client_secret_token(self):
        # Verify that a token obtained from a client secret (e.g. via the
        # DIPEX client) is working

        token = self.get_token(use_client_secret=True)

        self.assertRequest(
            "/api/v1/it", HTTP_200_OK, headers={"Authorization": "Bearer " + token}
        )


class TestTokenModel(tests.cases.LoRATestCase):
    @util.override_config(Settings(keycloak_rbac_enabled=True, confdb_show_owner=True))
    def test_uuid_required_if_client_is_mo(self):
        with self.assertRaises(ValidationError) as err:
            KeycloakToken(azp="mo")
        errors = err.exception.errors()[0]

        self.assertEqual(
            "The uuid user attribute is missing in the token", errors["msg"]
        )
        self.assertEqual("value_error", errors["type"])


class TestUuidInvalidOrMissing(tests.cases.LoRATestCase):
    @unittest.mock.patch("mora.auth.keycloak.oidc.auth")
    def test_401_when_uuid_missing_in_token(self, mock_auth):
        self.load_sample_structures(minimal=True)

        validation_err = ValidationError(
            errors=[ErrorWrapper(MissingError(), loc="uuid")], model=Token
        )

        def fake_auth():
            raise AuthenticationError(exc=validation_err)

        self.app.dependency_overrides[auth] = fake_auth

        # Make call to random endpoint
        r = self.assertRequest(
            "/service/o/", status_code=HTTP_401_UNAUTHORIZED, set_auth_header=True
        )
        self.assertEqual({"status": "Unauthorized", "msg": str(validation_err)}, r)


# TODO: Find a way to test that endpoints works when auth is disabled
@unittest.skip("Not working...(?)")
class TestAuthDisabled(tests.cases.LoRATestCase):
    def setUp(self) -> None:
        super().setUp()
        self.load_sample_structures()
        self.app.dependency_overrides = []

    @util.override_config(Settings(os2mo_auth=False))
    def test_no_token_required_when_auth_disabled(self):
        self.assertRequest("/service/o/")
