# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from operator import attrgetter

from mora.app import create_app
from mora.config import Environment


doc_endpoints = {
    "/docs",
    "/docs/oauth2-redirect",
    "/openapi.json",
    "/redoc",
}
health_endpoints = {
    "/health/",
    "/health/live",
    "/health/ready",
    "/health/{identifier}",
}
service_api = {
    "/service/c/ancestor-tree",
    "/service/c/{classid}/",
    "/service/c/{classid}/children",
    "/service/configuration",
    "/service/details/create",
    "/service/details/edit",
    "/service/details/terminate",
    "/service/e/autocomplete/",
    "/service/e/cpr_lookup/",
    "/service/e/create",
    "/service/e/{eid}/details/address",
    "/service/e/{id}/",
    "/service/e/{uuid}/terminate",
    "/service/exports/",
    "/service/exports/{file_name}",
    "/service/f/{facet}/",
    "/service/f/{facet}/children",
    "/service/insight",
    "/service/insight/download",
    "/service/insight/files",
    "/service/keycloak.json",
    "/service/navlinks",
    "/service/o/",
    "/service/o/{orgid}/",
    "/service/o/{orgid}/address_autocomplete/",
    "/service/o/{orgid}/e/",
    "/service/o/{orgid}/f/",
    "/service/o/{orgid}/f/{facet}/",
    "/service/o/{orgid}/it/",
    "/service/o/{orgid}/ou/",
    "/service/o/{orgid}/ou/tree",
    "/service/o/{parentid}/children",
    "/service/ou/ancestor-tree",
    "/service/ou/autocomplete/",
    "/service/ou/create",
    "/service/ou/{orgid}/details/address",
    "/service/ou/{origin}/map",
    "/service/ou/{parentid}/children",
    "/service/ou/{unitid}/",
    "/service/ou/{unitid}/configuration",
    "/service/ou/{unitid}/refresh",
    "/service/ou/{uuid}/terminate",
    "/service/token",
    "/service/validate/active-engagements/",
    "/service/validate/address/",
    "/service/validate/candidate-parent-org-unit/",
    "/service/validate/cpr/",
    "/service/validate/employee/",
    "/service/validate/existing-associations/",
    "/service/validate/existing-primary-it-associations/",
    "/service/validate/movable-org-unit/",
    "/service/validate/org-unit/",
    "/service/{rest_of_path:path}",
    "/service/{type}/{id}/details/",
    "/service/{type}/{id}/details/{function}",
}

all_endpoints = (
    {
        "",
        "/graphql",
        "/version/",
        "/saml/sso/",
    }
    | doc_endpoints
    | health_endpoints
    | service_api
)

testcafe_endpoints = {"/testing/testcafe-db-setup", "/testing/testcafe-db-teardown"}

statics_endpoints = {
    "/",
    "/organisation/",
    "/organisation/{path:path}",
    "/medarbejder/",
    "/medarbejder/{path:path}",
    "/organisationssammenkobling",
    "/forespoergsler",
    "/indsigt",
    "/favicon.ico",
}


def test_all_endpoints():
    app = create_app({"testcafe_enable": False})
    routes = set(map(attrgetter("path"), app.routes)) | {""}
    assert routes == all_endpoints


def test_testcafe_enabled():
    app = create_app({"testcafe_enable": True, "environment": Environment.TESTING})
    routes = set(map(attrgetter("path"), app.routes)) | {""}
    assert routes == all_endpoints | testcafe_endpoints


def test_static_enabled():
    app = create_app({"testcafe_enable": False, "statics_enable": True})
    routes = set(map(attrgetter("path"), app.routes)) | {""}
    assert routes == all_endpoints | statics_endpoints
