# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

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
    "/service/c/ancestor-tree",
    "/service/c/{classid}/",
    "/service/c/{classid}/children",
    "/service/details/create",
    "/service/details/edit",
    "/service/details/terminate",
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
    "/service/o/",
    "/service/o/{orgid}/",
    "/service/o/{orgid}/e/",
    "/service/o/{orgid}/f/",
    "/service/o/{orgid}/f/{facet}/",
    "/service/o/{orgid}/it/",
    "/service/o/{orgid}/ou/",
    "/service/o/{orgid}/ou/tree",
    "/service/o/{parentid}/children",
    "/service/ou/ancestor-tree",
    "/service/ou/create",
    "/service/ou/{orgid}/details/address",
    "/service/ou/{origin}/map",
    "/service/ou/{parentid}/children",
    "/service/ou/{unitid}/",
    "/service/ou/{unitid}/refresh",
    "/service/ou/{uuid}/terminate",
    "/service/token",
    "/service/validate/active-engagements/",
    "/service/validate/address/",
    "/service/validate/candidate-parent-org-unit/",
    "/service/validate/cpr/",
    "/service/validate/employee/",
    "/service/validate/existing-associations/",
    "/service/validate/org-unit/",
    "/service/{rest_of_path:path}",
    "/service/e/{id}/details/association",
    "/service/e/{id}/details/employee",
    "/service/e/{id}/details/engagement",
    "/service/e/{id}/details/it",
    "/service/e/{id}/details/kle",
    "/service/e/{id}/details/leave",
    "/service/e/{id}/details/manager",
    "/service/e/{id}/details/org_unit",
    "/service/e/{id}/details/owner",
    "/service/e/{id}/details/related_unit",
    "/service/ou/{id}/details/association",
    "/service/ou/{id}/details/employee",
    "/service/ou/{id}/details/engagement",
    "/service/ou/{id}/details/it",
    "/service/ou/{id}/details/kle",
    "/service/ou/{id}/details/leave",
    "/service/ou/{id}/details/manager",
    "/service/ou/{id}/details/org_unit",
    "/service/ou/{id}/details/owner",
    "/service/ou/{id}/details/related_unit",
    "/service/e/{id}/details/",
    "/service/ou/{id}/details/",
}
lora_endpoints = {
    "/lora/",
    "/lora/klassifikation/classes",
    "/lora/klassifikation/facet",
    "/lora/klassifikation/facet/fields",
    "/lora/klassifikation/facet/schema",
    "/lora/klassifikation/facet/{uuid}",
    "/lora/klassifikation/klasse",
    "/lora/klassifikation/klasse/fields",
    "/lora/klassifikation/klasse/schema",
    "/lora/klassifikation/klasse/{uuid}",
    "/lora/klassifikation/klassifikation",
    "/lora/klassifikation/klassifikation/fields",
    "/lora/klassifikation/klassifikation/schema",
    "/lora/klassifikation/klassifikation/{uuid}",
    "/lora/organisation/bruger",
    "/lora/organisation/bruger/fields",
    "/lora/organisation/bruger/schema",
    "/lora/organisation/bruger/{uuid}",
    "/lora/organisation/classes",
    "/lora/organisation/itsystem",
    "/lora/organisation/itsystem/fields",
    "/lora/organisation/itsystem/schema",
    "/lora/organisation/itsystem/{uuid}",
    "/lora/organisation/organisation",
    "/lora/organisation/organisation/fields",
    "/lora/organisation/organisation/schema",
    "/lora/organisation/organisation/{uuid}",
    "/lora/organisation/organisationenhed",
    "/lora/organisation/organisationenhed/fields",
    "/lora/organisation/organisationenhed/schema",
    "/lora/organisation/organisationenhed/{uuid}",
    "/lora/organisation/organisationfunktion",
    "/lora/organisation/organisationfunktion/fields",
    "/lora/organisation/organisationfunktion/schema",
    "/lora/organisation/organisationfunktion/{uuid}",
    "/lora/site-map",
}
testing_endpoints = {
    "/testing/amqp/emit",
    "/testing/database/restore",
    "/testing/database/snapshot",
    "/testing/events/reset-last-tried",
}
graphql_endpoints = {
    "/graphql",
    "/graphql/",
    "/graphql/v18",
    "/graphql/v18/schema.graphql",
    "/graphql/v19",
    "/graphql/v19/schema.graphql",
    "/graphql/v20",
    "/graphql/v20/schema.graphql",
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
}

all_endpoints = (
    {
        "",
        "/version/",
        "/saml/sso/",
    }
    | lora_endpoints
    | doc_endpoints
    | health_endpoints
    | service_api_endpoints
    | graphql_endpoints
)


def test_all_endpoints() -> None:
    app = create_app()
    routes = {r.path for r in app.routes} | {""}
    assert routes == all_endpoints


def test_testing_endpoints(set_settings: Callable[..., None]) -> None:
    set_settings(INSECURE_ENABLE_TESTING_API="true")
    app = create_app()
    routes = {r.path for r in app.routes} | {""}
    assert routes == all_endpoints | testing_endpoints
