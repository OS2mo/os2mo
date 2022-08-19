# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest.mock

import pytest
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

import mora.auth.keycloak.oidc
import tests.cases
from mora.auth.keycloak.models import KeycloakToken
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from tests import util
from tests.util import sample_structures_cls_fixture
from tests.util import sample_structures_minimal_cls_fixture


def test_ensure_endpoints_depend_on_oidc_auth_function(all_routes, no_auth_endpoints):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """
    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    ensure_endpoints_depend_on_oidc_auth_function(
        all_routes, no_auth_endpoints, mora.auth.keycloak.oidc.auth
    )


def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(
    all_routes, no_auth_endpoints
):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """
    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    ensure_no_auth_endpoints_do_not_depend_on_auth_function(
        all_routes, no_auth_endpoints, mora.auth.keycloak.oidc.auth
    )


class AsyncTestAuthEndpointsReturn401(tests.cases.AsyncTestCase):
    app_settings_overrides = {
        "graphql_enable": True,
        "graphiql_enable": True,
    }

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # Enable the real OIDC auth function
        self.app.dependency_overrides = dict()

    async def test_auth_service_address(self):
        await self.assertRequestFails(
            "/service/e/00000000-0000-0000-0000-000000000000/details/address",
            HTTP_401_UNAUTHORIZED,
        )

    async def test_auth_service_cpr(self):
        await self.assertRequestFails(
            "/service/e/cpr_lookup/?q=1234", HTTP_401_UNAUTHORIZED
        )

    async def test_auth_service_details_reading(self):
        await self.assertRequestFails(
            "/service/e/00000000-0000-0000-0000-000000000000/details/",
            HTTP_401_UNAUTHORIZED,
        )

    async def test_auth_service_details_writing(self):
        await self.assertRequestResponse(
            "/service/details/create",
            "Not authenticated",
            status_code=HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    async def test_auth_service_employee(self):
        await self.assertRequestFails(
            "/service/o/00000000-0000-0000-0000-000000000000/e/", HTTP_401_UNAUTHORIZED
        )

    async def test_auth_service_exports(self):
        await self.assertRequestFails(
            "/service/exports/not-important", HTTP_401_UNAUTHORIZED
        )

    async def test_auth_service_facets(self):
        await self.assertRequestFails("/service/c/ancestor-tree", HTTP_401_UNAUTHORIZED)

    async def test_auth_service_itsystem(self):
        await self.assertRequestFails(
            "/service/o/00000000-0000-0000-0000-000000000000/it/", HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_kle(self):
        # KLE router not used anywhere?
        pass

    async def test_auth_service_org(self):
        await self.assertRequestFails("/service/o/", HTTP_401_UNAUTHORIZED)

    async def test_auth_service_orgunit(self):
        await self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/children",
            HTTP_401_UNAUTHORIZED,
        )

    async def test_auth_service_related(self):
        await self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/map",
            HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    async def test_auth_service_configuration(self):
        await self.assertRequestFails(
            "/service/ou/00000000-0000-0000-0000-000000000000/configuration",
            HTTP_401_UNAUTHORIZED,
        )

    async def test_auth_service_validate(self):
        await self.assertRequestFails(
            "/service/validate/org-unit/",
            HTTP_401_UNAUTHORIZED,
            json=[{"not": "important"}],
        )

    async def test_auth_graphql(self):
        # GET (only works with GraphiQL enabled)
        await self.assertRequestFails("/graphql", HTTP_401_UNAUTHORIZED)

        # POST (usual communication, always enabled)
        await self.assertRequestFails(
            "/graphql",
            HTTP_401_UNAUTHORIZED,
            json={"query": "{ __typename }"},  # always implemented
        )


class TestAuthEndpointsReturn2xx(tests.cases.AsyncLoRATestCase):
    """
    Keycloak integration tests of a few endpoints (one from /service endpoints
    and one from the /graphql endpoints)
    """

    app_settings_overrides = {
        "graphql_enable": True,
        "graphiql_enable": True,
    }

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # Enable the real Keycloak auth mechanism in order to perform Keycloak
        # integration tests
        self.app.dependency_overrides = dict()

    @pytest.mark.usefixtures("sample_structures_minimal")
    async def test_auth_service_org(self):
        await self.assertRequest("/service/o/", HTTP_200_OK, set_auth_header=True)

    async def test_auth_graphql(self):
        # GET (only works with GraphiQL enabled)
        await self.assertRequest("/graphql", HTTP_200_OK, set_auth_header=True)

        # POST (usual communication, always enabled)
        await self.assertRequest(
            "/graphql",
            HTTP_200_OK,
            set_auth_header=True,
            json={"query": "{ __typename }"},  # always implemented
        )


class TestTokenModel(tests.cases.TestCase):
    @util.override_config(Settings(keycloak_rbac_enabled=True, confdb_show_owner=True))
    def test_uuid_required_if_client_is_mo(self):
        with self.assertRaises(ValidationError) as err:
            KeycloakToken(azp="mo-frontend")
        errors = err.exception.errors()[0]

        self.assertEqual(
            "The uuid user attribute is missing in the token", errors["msg"]
        )
        self.assertEqual("value_error", errors["type"])

    @util.override_config(Settings(keycloak_rbac_enabled=True, confdb_show_owner=True))
    def test_uuid_parsed_correctly_uuid(self):
        token = KeycloakToken(
            azp="mo-frontend", uuid="30c89ad2-e0bb-42ae-82a8-1ae36943cb9e"
        )

        self.assertEqual("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e", str(token.uuid))

    @util.override_config(Settings(keycloak_rbac_enabled=True, confdb_show_owner=True))
    def test_uuid_parsed_correctly_base64(self):
        token = KeycloakToken(azp="mo-frontend", uuid="0prIMLvgrkKCqBrjaUPLng==")

        self.assertEqual("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e", str(token.uuid))

    @util.override_config(Settings(keycloak_rbac_enabled=True, confdb_show_owner=True))
    def test_uuid_parse_fails_on_garbage(self):
        with self.assertRaises(ValidationError) as err:
            KeycloakToken(azp="mo-frontend", uuid="garbageasdasd")
        errors = err.exception.errors()[0]

        self.assertEqual("value is not a valid uuid", errors["msg"])
        self.assertEqual("type_error.uuid", errors["type"])


@sample_structures_minimal_cls_fixture
class TestUuidInvalidOrMissing(tests.cases.LoRATestCase):
    @unittest.mock.patch("mora.auth.keycloak.oidc.auth")
    def test_401_when_uuid_missing_in_token(self, mock_auth):
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
@sample_structures_cls_fixture
class TestAuthDisabled(tests.cases.LoRATestCase):
    def setUp(self) -> None:
        super().setUp()
        self.app.dependency_overrides = []

    @util.override_config(Settings(os2mo_auth=False))
    def test_no_token_required_when_auth_disabled(self):
        self.assertRequest("/service/o/")
