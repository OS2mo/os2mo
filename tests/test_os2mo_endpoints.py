# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.app import create_app

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
service_api_endpoints = {
    "/service/details/create",
    "/service/details/edit",
    "/service/details/terminate",
    "/service/e/cpr_lookup/",
    "/service/e/create",
    "/service/e/{eid}/details/address",
    "/service/e/{id}/",
    "/service/e/{uuid}/terminate",
    "/service/f/{facet}/",
    "/service/o/",
    "/service/o/{orgid}/",
    "/service/o/{orgid}/e/",
    "/service/o/{orgid}/f/{facet}/",
    "/service/o/{orgid}/it/",
    "/service/o/{orgid}/ou/",
    "/service/o/{orgid}/ou/tree",
    "/service/o/{parentid}/children",
    "/service/ou/create",
    "/service/ou/{orgid}/details/address",
    "/service/ou/{origin}/map",
    "/service/ou/{parentid}/children",
    "/service/ou/{unitid}/",
    "/service/ou/{uuid}/terminate",
    "/service/{rest_of_path:path}",
    "/service/e/{id}/details/association",
    "/service/e/{id}/details/engagement",
    "/service/e/{id}/details/it",
    "/service/e/{id}/details/manager",
    "/service/ou/{id}/details/association",
    "/service/ou/{id}/details/engagement",
    "/service/ou/{id}/details/it",
    "/service/ou/{id}/details/kle",
    "/service/ou/{id}/details/manager",
    "/service/e/{id}/details/",
}
testing_endpoints = {
    "/testing/amqp/emit",
    "/testing/database/restore",
    "/testing/database/snapshot",
    "/testing/database/setup",
    "/testing/database/reset",
    "/testing/events/reset-last-tried",
}
graphql_endpoints = {
    "/graphql",
    "/graphql/",
    "/graphql/v21",
    "/graphql/v21/schema.graphql",
    "/graphql/v22",
    "/graphql/v22/schema.graphql",
    "/graphql/v23",
    "/graphql/v23/schema.graphql",
    "/graphql/v24",
    "/graphql/v24/schema.graphql",
    "/graphql/v25",
    "/graphql/v25/schema.graphql",
    "/graphql/v26",
    "/graphql/v26/schema.graphql",
    "/graphql/v27",
    "/graphql/v27/schema.graphql",
    "/graphql/v28",
    "/graphql/v28/schema.graphql",
    "/graphql/v29",
    "/graphql/v29/schema.graphql",
    "/graphql/v30",
    "/graphql/v30/schema.graphql",
}

all_endpoints = (
    {
        "",
        "/version/",
        "/saml/sso/",
    }
    | doc_endpoints
    | health_endpoints
    | service_api_endpoints
    | graphql_endpoints
)


def test_all_endpoints() -> None:
    app = create_app()
    routes = {r.path for r in app.routes} | {""}
    assert routes == all_endpoints


@pytest.mark.envvar({"INSECURE_ENABLE_TESTING_API": "true"})
def test_testing_endpoints() -> None:
    app = create_app()
    routes = {r.path for r in app.routes} | {""}
    assert routes == all_endpoints | testing_endpoints


@pytest.mark.envvar({"EXPOSE_SERVICE_API": "false"})
def test_service_api_endpoints_can_be_disabled() -> None:
    app = create_app()
    routes = {r.path for r in app.routes} | {""}
    assert routes == all_endpoints - service_api_endpoints
