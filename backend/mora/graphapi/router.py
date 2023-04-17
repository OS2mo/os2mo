# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter

from mora.config import get_settings

AUTH_SCRIPT = """
<script src="https://unpkg.com/keycloak-js@20.0.2/dist/keycloak.min.js"></script>
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

GRAPHIQL_HTML = r"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Strawberry GraphiQL</title>
        <link
          rel="icon"
          href="data:image/svg+xml,
            <svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22>
                <!-- Strawberry Emoji as a HTML Entity (hex)  -->
                <text y=%22.9em%22 font-size=%2280%22>&#x1f353;</text>
            </svg>"
        />
        <style>
          body {
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
          }

          #graphiql {
            height: 100vh;
            display: flex;
          }

          .docExplorerHide {
            display: none;
          }

          .doc-explorer-contents {
            overflow-y: hidden !important;
          }

          .docExplorerWrap {
            width: unset !important;
            min-width: unset !important;
          }

          .graphiql-explorer-actions select {
            margin-left: 4px;
          }
        </style>

        <script
          crossorigin
          src="https://unpkg.com/react@17.0.2/umd/react.development.js"
          integrity="sha384-xQwCoNcK/7P3Lpv50IZSEbJdpqbToWEODAUyI/RECaRXmOE2apWt7htari8kvKa/"
        ></script>
        <script
          crossorigin
          src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.development.js"
          integrity="sha384-E9IgxDsnjKgh0777N3lXen7NwXeTsOpLLJhI01SW7idG046SRqJpsW2rJwsOYk0L"
        ></script>

        <script
          crossorigin
          src="https://unpkg.com/js-cookie@3.0.1/dist/js.cookie.min.js"
          integrity="sha384-ETDm/j6COkRSUfVFsGNM5WYE4WjyRgfDhy4Pf4Fsc8eNw/eYEMqYZWuxTzMX6FBa"
        ></script>

        <link
          crossorigin
          rel="stylesheet"
          href="https://unpkg.com/graphiql@2.2.0/graphiql.min.css"
          integrity="sha384-4a2fCKkum7OnFcO9Qae5NAO7bYHTeolCix2FOnzhz8L42NP6+2Q1cTH7p/xr4Pfg"
        />
      </head>

      <body>
        <div id="graphiql" class="graphiql-container">Loading...</div>
        <script
          crossorigin
          src="https://unpkg.com/graphiql@2.2.0/graphiql.min.js"
          integrity="sha384-JHFGCFTH/jUGV6uL38eHuw/3kb0aUiF0EzWPP68NQxvz7ldZXEoCv9RBGtsFHM86"
        ></script>
        <script
          crossorigin
          src="https://unpkg.com/@graphiql/plugin-explorer@0.1.0/dist/graphiql-plugin-explorer.umd.js"
          integrity="sha384-XyAmNqmxnLsRHkMhQYTqC0ub7uXpNbwdkhjn70ZF3J3XSb7bouSdRVfzDojimcMd"
        ></script>
        <script>
          const EXAMPLE_QUERY = `# Welcome to GraphiQL 🍓
    #
    # GraphiQL is an in-browser tool for writing, validating, and
    # testing GraphQL queries.
    #
    # Type queries into this side of the screen, and you will see intelligent
    # typeaheads aware of the current GraphQL type schema and live syntax and
    # validation errors highlighted within the text.
    #
    # GraphQL queries typically start with a "{" character. Lines that starts
    # with a # are ignored.
    #
    # An example GraphQL query might look like:
    #
    #     {
    #       field(arg: "value") {
    #         subField
    #       }
    #     }
    #
    # Keyboard shortcuts:
    #
    #       Run Query:  Ctrl-Enter (or press the play button above)
    #
    #   Auto Complete:  Ctrl-Space (or just start typing)
    #
    `;

          const fetchURL = window.location.href;

          function httpUrlToWebSockeUrl(url) {
            const parsedURL = new URL(url);
            const protocol = parsedURL.protocol === "http:" ? "ws:" : "wss:";
            parsedURL.protocol = protocol;
            parsedURL.hash = "";
            return parsedURL.toString();
          }

          const headers = {};
          const csrfToken = Cookies.get("csrftoken");

          if (csrfToken) {
            headers["x-csrftoken"] = csrfToken;
          }

          const subscriptionsEnabled = JSON.parse("{{ SUBSCRIPTION_ENABLED }}");
          const subscriptionUrl = subscriptionsEnabled
            ? httpUrlToWebSockeUrl(fetchURL)
            : null;

          const fetcher = GraphiQL.createFetcher({
            url: fetchURL,
            headers: headers,
            subscriptionUrl,
          });

          function GraphiQLWithExplorer() {
            const [query, setQuery] = React.useState(EXAMPLE_QUERY);
            const explorerPlugin = GraphiQLPluginExplorer.useExplorerPlugin({
              query: query,
              onEdit: setQuery,
            });
            return React.createElement(GraphiQL, {
              fetcher: fetcher,
              defaultEditorToolsVisibility: true,
              plugins: [explorerPlugin],
              query: query,
              onEditQuery: setQuery,
              inputValueDeprecation: true,
            });
          }

          ReactDOM.render(
            React.createElement(GraphiQLWithExplorer),
            document.getElementById("graphiql")
          );
        </script>
      </body>
    </html>
"""


class CustomGraphQLRouter(GraphQLRouter):
    """Custom GraphQL router to inject HTML into the GraphiQL interface."""

    def __init__(self, is_latest: bool, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.is_latest = is_latest

    def get_graphiql_response(self) -> HTMLResponse:
        html = GRAPHIQL_HTML
        html = html.replace("{{ SUBSCRIPTION_ENABLED }}", "true")

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if not self.is_latest:
            html = html.replace("<body>", f"<body>{DEPRECATION_NOTICE}")

        # Inject script for authentication if auth is enabled. The script is added just
        # before closing the <body> so it is executed after the normal GraphiQL
        # JavaScript, which is required to access the `headers` constant.
        if get_settings().os2mo_auth:
            html = html.replace("</body>", f"{AUTH_SCRIPT}</body>")

        html = html.replace(
           "subscriptionUrl,",
           "subscriptionUrl,\nwsConnectionParams: { foo: \"bar\" }",
        )

        return HTMLResponse(html)
