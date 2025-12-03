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
        # TODO(#67779): enable prettier again
        # html = html.replace("</body>", f"{PRETTIER_SCRIPT}</body>")

        # Use jsdelivr instead of unpkg CDN. We've had a bit of - completely
        # fair - reliability issues from unpkg.
        # https://github.com/unpkg/unpkg/issues/412
        # https://github.com/strawberry-graphql/strawberry/issues/3826
        html = html.replace("https://unpkg.com", "https://cdn.jsdelivr.net/npm")

        return HTMLResponse(html)
