# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from starlette.requests import Request
from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter

from mora.config import get_settings
from mora.graphapi.custom_schema import get_version
from mora.graphapi.version import LATEST_VERSION

AUTH_SCRIPT = """
<script src="https://cdn.jsdelivr.net/npm/keycloak-js@20.0.2/dist/keycloak.min.js"></script>
<script>
  const keycloakJson = window.location.origin + "/service/keycloak.json"
  const keycloak = new Keycloak(keycloakJson);

  const setToken = function() {
    headers["Authorization"] = "Bearer " + keycloak.token;
  }

  keycloak.init({
    onLoad: "login-required",
  }).then(authenticated => {
    if (!authenticated) {
      console.error("Failed to authenticate");
      return
    }
    setToken();

    // Every 5 seconds, check and refresh token if it expires within 15 seconds
    setInterval(() => {
      keycloak.updateToken(15).then(refreshed => {
        if (refreshed) {
          console.log("Token was successfully refreshed");
          setToken();
        }
      }).catch(() => {
        console.error("Failed to refresh token");
      });
    }, 5000);
  }).catch(() => {
    console.error("Failed to initialise Keycloak");
  });
</script>
"""

DEPRECATION_NOTICE = """
<style>
    #deprecation-notice {
        color: #997404;
        background-color: #fff3cd;
        padding: 1rem;
        border-bottom: #ffe69c solid 1px;
    }
    #deprecation-notice a {
        color: #997404;
        font-weight: bold;
    }
    /* Reduce the GraphiQL interface height by approximately the height of the deprecation notice. */
    #graphiql {
        height: calc(100vh - 3rem);
    }
</style>
<div id="deprecation-notice">
    You are using a deprecated version of the GraphQL API.
    Click <a href='/graphql'>here</a> to go to the latest version.
</div>
"""

PRETTIER_SCRIPT = """
<script src="https://cdn.jsdelivr.net/npm/prettier@2/standalone.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prettier@2/parser-graphql.js"></script>
<script>
  // https://prettier.io/docs/en/browser#global
  // https://github.com/graphql/graphiql/blob/b52c39143a4269cd899b16d06de5c7fe024fae2d/packages/graphiql-react/src/editor/hooks.ts#L253-L260
  // setTimeout allows the React components to load
  setTimeout(() => {
    const queryEditor = document.querySelector('.CodeMirror').CodeMirror;
    const originalSetValue = queryEditor.setValue;
    queryEditor.setValue = function(value) {
      const prettyValue = prettier.format(value, {
        parser: "graphql",
        plugins: prettierPlugins,
      });
      return originalSetValue.call(this, prettyValue);
    };
  });
</script>
"""

# Snippet to optionally strip deprecated fields from GraphQL introspection queries
# GraphiQL uses the introspection query provided by graphql.js to do introspection
# The getIntrospectionQuery method is hardcoded to always return deprecated fields
# See: https://github.com/graphql/graphql-js/blob/v16.0.0/src/utilities/getIntrospectionQuery.ts#L88
# The below defines a custom GraphiQL fetcher, which strips deprecation from the
# introspection query based on the "show_deprecated" URL parameter
NO_DEPRECATION_FETCHER_SNIPPER = """
const DEFAULT_INTROSPECTION_OPERATION = 'IntrospectionQuery';
const query_string = window.location.search;
const url_parameters = new URLSearchParams(query_string);
const show_deprecated = url_parameters.get('show_deprecated');

const no_deprecation_fetcher = (graphQLParams, opts) => {
    // If configured to show deprecated fields use the default fetcher
    if (show_deprecated === "1") {
        return fetcher(graphQLParams, opts);
    }

    // At this point we are configured to hide deprecated fields
    // If we are not running an introspection query use the default fetcher
    if (graphQLParams.operationName !== DEFAULT_INTROSPECTION_OPERATION) {
        return fetcher(graphQLParams, opts);
    }

    // At this point we are running an introspection query
    console.log('Intercepted default introspection, removing deprecated fields.');
    // Strip all deprecation inclusion arguments from the query
    const deprecation_argument = "(includeDeprecated: true)";
    graphQLParams["query"] = graphQLParams["query"].replaceAll(deprecation_argument, "");
    return fetcher(graphQLParams, opts);
};
"""


class CustomGraphQLRouter(GraphQLRouter):
    """Custom GraphQL router to inject HTML into the GraphiQL interface."""

    async def render_graphql_ide(self, request: Request) -> HTMLResponse:
        assert self.graphql_ide == "graphiql"  # type: ignore[attr-defined]
        html = self.graphql_ide_html  # type: ignore[attr-defined]

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if get_version(self.schema) is not LATEST_VERSION:
            html = html.replace("<body>", f"<body>{DEPRECATION_NOTICE}")

        # Inject script for authentication if auth is enabled. The script is added just
        # before closing the <body> so it is executed after the normal GraphiQL
        # JavaScript, which is required to access the `headers` constant.
        if get_settings().os2mo_auth:
            html = html.replace("</body>", f"{AUTH_SCRIPT}</body>")

        # Overwrite query prettifier button with a good prettifier
        # https://github.com/graphql/graphiql/issues/1517
        html = html.replace("</body>", f"{PRETTIER_SCRIPT}</body>")

        # Use jsdelivr instead of unpkg CDN. We've had a bit of - completely
        # fair - reliability issues from unpkg.
        # https://github.com/unpkg/unpkg/issues/412
        # https://github.com/strawberry-graphql/strawberry/issues/3826
        html = html.replace("https://unpkg.com", "https://cdn.jsdelivr.net/npm")

        # Add our custom fetcher to GraphiQL, we use the "root.render" as an insertion
        # marker inserting our custom code just above the render call.
        RENDER_MARKER = "root.render("
        html = html.replace(
            RENDER_MARKER, NO_DEPRECATION_FETCHER_SNIPPER + "\n" + RENDER_MARKER
        )
        html = html.replace("fetcher: fetcher,", "fetcher: no_deprecation_fetcher,")

        return HTMLResponse(html)
