# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from starlette.requests import Request
from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter

from mora.graphapi.custom_schema import get_version
from mora.graphapi.version import LATEST_VERSION

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
    /* Reduce the IDE height by approximately the height of the deprecation notice. */
    #graphiql,
    #embedded-sandbox {
        height: calc(100vh - 3rem);
    }
</style>
<div id="deprecation-notice">
    You are using a deprecated version of the GraphQL API.
    Click <a href='__LATEST_URL__'>here</a> to go to the latest version.
</div>
"""


# Shared by the GraphiQL and Apollo Sandbox pages. Expects `Keycloak` to be
# imported from keycloak-js, and defines `keycloak` and `keycloakReady`, which
# settles once the user is logged in (or Keycloak failed to initialise).
KEYCLOAK_SCRIPT = """
      const keycloak = new Keycloak({
        url: "__KEYCLOAK_URL__",
        realm: "__KEYCLOAK_REALM__",
        clientId: "__KEYCLOAK_CLIENT_ID__",
      });

      const keycloakReady = keycloak
        .init({
          onLoad: "login-required",
        })
        .then((authenticated) => {
          if (!authenticated) {
            console.error("Failed to authenticate");
            return;
          }
          // Every 5 seconds, check and refresh token if it expires within 15 seconds
          setInterval(() => {
            keycloak
              .updateToken(15)
              .then((refreshed) => {
                if (refreshed) {
                  console.log("Token was successfully refreshed");
                }
              })
              .catch(() => {
                console.error("Failed to refresh token");
              });
          }, 5000);
        })
        .catch(() => {
          console.error("Failed to initialise Keycloak");
        });
"""


# Based on
# https://github.com/graphql/graphiql/blob/aacdc8586fa4346a4681e73e29af7afda4718617/examples/graphiql-cdn/index.html
# https://github.com/strawberry-graphql/strawberry/blob/13caf46759c0db59a1b43565aba9772ce4f93e1d/strawberry/static/graphiql.html
GRAPHIQL_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MO GraphQL</title>
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
        margin: 0;
      }
      #graphiql {
        height: 100dvh;
      }
      .graphiql-logo {
        display: none;
      }
    </style>
    <link rel="stylesheet" href="https://esm.sh/graphiql@5.1.1/dist/style.css" />
    <link
      rel="stylesheet"
      href="https://esm.sh/@graphiql/plugin-explorer@5.1.1/dist/style.css"
    />
    <script type="importmap">
      {
        "imports": {
          "react": "https://esm.sh/react@19.1.0",
          "react/": "https://esm.sh/react@19.1.0/",

          "react-dom": "https://esm.sh/react-dom@19.1.0",
          "react-dom/": "https://esm.sh/react-dom@19.1.0/",

          "graphiql": "https://esm.sh/graphiql@5.1.1?standalone&external=react,react-dom,@graphiql/react,graphql",
          "graphiql/": "https://esm.sh/graphiql@5.1.1/",
          "@graphiql/plugin-explorer": "https://esm.sh/@graphiql/plugin-explorer@5.1.1?standalone&external=react,@graphiql/react,graphql",
          "@graphiql/react": "https://esm.sh/@graphiql/react@0.37.3?standalone&external=react,react-dom,graphql,@graphiql/toolkit,@emotion/is-prop-valid",

          "@graphiql/toolkit": "https://esm.sh/@graphiql/toolkit@0.11.3?standalone&external=graphql",
          "graphql": "https://esm.sh/graphql@16.11.0",
          "@emotion/is-prop-valid": "data:text/javascript,",

          "keycloak-js": "https://esm.sh/keycloak-js@26.2.1"
        }
      }
    </script>
    <script type="module">
      import React from "react";
      import ReactDOM from "react-dom/client";
      import { GraphiQL, HISTORY_PLUGIN } from "graphiql";
      import { createGraphiQLFetcher } from "@graphiql/toolkit";
      import { explorerPlugin } from "@graphiql/plugin-explorer";
      import "graphiql/setup-workers/esm.sh";
      import Keycloak from "keycloak-js";
__KEYCLOAK_SCRIPT__
      const authorizedFetch = async (resource, options) => {
        // Wait for Keycloak to authenticate before issuing any request, this ensures
        // that the introspection query GraphiQL fires on mount is sent with a token.
        await keycloakReady;
        return fetch(resource, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: keycloak.token ? `Bearer ${keycloak.token}` : "",
          },
        });
      };

      const fetcher = createGraphiQLFetcher({
        url: window.location.href,
        fetch: authorizedFetch,
      });
      const plugins = [HISTORY_PLUGIN, explorerPlugin()];

      function App() {
        return React.createElement(GraphiQL, {
          fetcher,
          plugins,
          defaultEditorToolsVisibility: true,
        });
      }

      const container = document.getElementById("graphiql");
      const root = ReactDOM.createRoot(container);
      root.render(React.createElement(App));
    </script>
  </head>
  <body>
    <div id="graphiql">
      <div class="loading">Loading…</div>
    </div>
  </body>
</html>
"""


# Based on
# https://github.com/strawberry-graphql/strawberry/blob/13caf46759c0db59a1b43565aba9772ce4f93e1d/strawberry/static/apollo-sandbox.html
# https://www.apollographql.com/docs/graphos/platform/sandbox#embedding-sandbox
APOLLO_SANDBOX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MO GraphQL</title>
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
        margin: 0;
        overflow: hidden;
      }
      #embedded-sandbox {
        width: 100vw;
        height: 100dvh;
      }
    </style>
    <script type="importmap">
      {
        "imports": {
          "@apollo/sandbox": "https://esm.sh/@apollo/sandbox@2.7.4?standalone&deps=graphql@16.11.0",

          "keycloak-js": "https://esm.sh/keycloak-js@26.2.1"
        }
      }
    </script>
    <script type="module">
      import { ApolloSandbox } from "@apollo/sandbox";
      import Keycloak from "keycloak-js";
__KEYCLOAK_SCRIPT__
      // The sandbox copies the endpoint into its iframe URL without encoding it,
      // so it must be an absolute URL without any query string or fragment.
      const endpoint = new URL("__GRAPHQL_ENDPOINT__", window.location.origin).href;

      // The sandbox calls this from this page, not from its iframe, for every
      // request, including the introspection query it fires on load.
      const handleRequest = async (_url, options) => {
        // Wait for Keycloak to authenticate before issuing any request, this ensures
        // that the introspection query is sent with a token.
        await keycloakReady;
        // Timers are throttled in background tabs, so refresh the token here too.
        await keycloak.updateToken(15).catch(() => {});
        // Replace, rather than add to, any Authorization header set in the UI.
        const headers = new Headers(options.headers);
        if (keycloak.token) {
          headers.set("Authorization", `Bearer ${keycloak.token}`);
        }
        // Ignore the URL passed by the sandbox so the token is only ever sent to
        // MO, and never send cookies, as MO only authenticates by token.
        return fetch(endpoint, { ...options, headers, credentials: "omit" });
      };

      // The sandbox sends the page URL to Apollo, so wait until Keycloak has
      // removed its login callback parameters from it.
      await keycloakReady;

      new ApolloSandbox({
        target: "#embedded-sandbox",
        initialEndpoint: endpoint,
        handleRequest,
        endpointIsEditable: false,
        hideCookieToggle: true,
        runTelemetry: false,
        initialState: {
          includeCookies: false,
          // The schema is large, so don't introspect it every 5 seconds.
          pollForSchemaUpdates: false,
        },
      });
    </script>
  </head>
  <body>
    <div id="embedded-sandbox"></div>
  </body>
</html>
"""


class CustomGraphQLRouter(GraphQLRouter):
    """Custom GraphQL router to serve the GraphiQL and Apollo Sandbox interfaces."""

    def render_ide(self, request: Request, html: str, latest_url: str) -> HTMLResponse:
        """Render an IDE page for this GraphQL version.

        Args:
            request: The request for the IDE page.
            html: The IDE page template.
            latest_url: URL of the same IDE for the latest GraphQL version.

        Returns:
            The rendered IDE page.
        """
        # Inject the Keycloak config directly, rather than having the browser
        # fetch it from the (now removed) /service/keycloak.json endpoint.
        settings = request.app.state.settings
        version = get_version(self.schema)
        html = (
            html.replace("__KEYCLOAK_SCRIPT__", KEYCLOAK_SCRIPT)
            .replace("__KEYCLOAK_URL__", str(settings.keycloak_auth_server_url))
            .replace("__KEYCLOAK_REALM__", settings.keycloak_realm)
            .replace("__KEYCLOAK_CLIENT_ID__", settings.keycloak_mo_client)
            .replace("__GRAPHQL_ENDPOINT__", f"/graphql/v{version.value}")
        )

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if version is not LATEST_VERSION:
            notice = DEPRECATION_NOTICE.replace("__LATEST_URL__", latest_url)
            html = html.replace("<body>", f"<body>{notice}")

        return HTMLResponse(html)

    async def render_graphql_ide(self, request: Request) -> HTMLResponse:
        return self.render_ide(request, GRAPHIQL_HTML, latest_url="/graphql")

    async def render_apollo_sandbox(self, request: Request) -> HTMLResponse:
        return self.render_ide(
            request, APOLLO_SANDBOX_HTML, latest_url="/graphql/apollo-sandbox"
        )
