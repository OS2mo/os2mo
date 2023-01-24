# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.utils.graphiql import get_graphiql_html

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


class CustomGraphQLRouter(GraphQLRouter):
    """Custom GraphQL router to inject HTML into the GraphiQL interface."""

    def __init__(self, is_latest: bool, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.is_latest = is_latest

    def get_graphiql_response(self) -> HTMLResponse:
        html = get_graphiql_html()

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if not self.is_latest:
            html = html.replace("<body>", f"{DEPRECATION_NOTICE}<body>")

        # Inject script for authentication if auth is enabled. The script is added just
        # before closing the <body> so it is executed after the normal GraphiQL
        # JavaScript, which is required to access the `headers` constant.
        if get_settings().os2mo_auth:
            html = html.replace("</body>", f"{AUTH_SCRIPT}</body>")

        return HTMLResponse(html)
