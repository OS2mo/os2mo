# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Any

from fastapi import Request
from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
from structlog import get_logger

from mora.auth.middleware import get_authenticated_user
from mora.config import get_settings


logger = get_logger()


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

    def __init__(self, version_difference: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.version_difference = version_difference

    async def process_result(
        self, request: Request, result: ExecutionResult
    ) -> GraphQLHTTPResponse:
        if self.version_difference != 0:
            actor = get_authenticated_user()
            sleep_time = 0.1 * self.version_difference
            logger.info("Deprecation sleep", amount=sleep_time, actor=actor)
            await asyncio.sleep(sleep_time)
        return await super().process_result(request, result)

    async def render_graphql_ide(self, request: Request) -> HTMLResponse:
        assert self.graphql_ide == "graphiql"  # type: ignore[attr-defined]
        html = self.graphql_ide_html  # type: ignore[attr-defined]

        # Show deprecation notice at the top of the page if accessing an old version
        # of GraphQL.
        if self.version_difference != 0:
            html = html.replace("<body>", f"<body>{DEPRECATION_NOTICE}")

        # Inject script for authentication if auth is enabled. The script is added just
        # before closing the <body> so it is executed after the normal GraphiQL
        # JavaScript, which is required to access the `headers` constant.
        if get_settings().os2mo_auth:
            html = html.replace("</body>", f"{AUTH_SCRIPT}</body>")

        return HTMLResponse(html)
