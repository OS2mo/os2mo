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


# Based on
# https://github.com/graphql/graphiql/blob/aacdc8586fa4346a4681e73e29af7afda4718617/examples/graphiql-cdn/index.html
# https://github.com/strawberry-graphql/strawberry/blob/13caf46759c0db59a1b43565aba9772ce4f93e1d/strawberry/static/graphiql.html
HTML = """
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
    <link rel="stylesheet" href="https://esm.sh/graphiql/dist/style.css" />
    <link
      rel="stylesheet"
      href="https://esm.sh/@graphiql/plugin-explorer/dist/style.css"
    />
    <script type="importmap">
      {
        "imports": {
          "react": "https://esm.sh/react@19.1.0",
          "react/": "https://esm.sh/react@19.1.0/",

          "react-dom": "https://esm.sh/react-dom@19.1.0",
          "react-dom/": "https://esm.sh/react-dom@19.1.0/",

          "graphiql": "https://esm.sh/graphiql?standalone&external=react,react-dom,@graphiql/react,graphql",
          "graphiql/": "https://esm.sh/graphiql/",
          "@graphiql/plugin-explorer": "https://esm.sh/@graphiql/plugin-explorer?standalone&external=react,@graphiql/react,graphql",
          "@graphiql/react": "https://esm.sh/@graphiql/react?standalone&external=react,react-dom,graphql,@graphiql/toolkit,@emotion/is-prop-valid",

          "@graphiql/toolkit": "https://esm.sh/@graphiql/toolkit?standalone&external=graphql",
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

      const keycloakJson = window.location.origin + "/service/keycloak.json";
      const keycloak = new Keycloak(keycloakJson);

      keycloak
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

      const authorizedFetch = (resource, options) => {
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


class CustomGraphQLRouter(GraphQLRouter):
    """Custom GraphQL router to inject HTML into the GraphiQL interface."""

    async def render_graphql_ide(self, request: Request) -> HTMLResponse:
        html = HTML

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if get_version(self.schema) is not LATEST_VERSION:
            html = html.replace("<body>", f"<body>{DEPRECATION_NOTICE}")

        return HTMLResponse(html)
