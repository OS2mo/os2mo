# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.utils.graphiql import get_graphiql_html

from mora.config import get_settings


class CustomGraphQLRouter(GraphQLRouter):
    def get_graphiql_response(self) -> HTMLResponse:
        """Custom GraphiQL HTML to inject JavaScript for authentication."""
        if not get_settings().os2mo_auth:
            return super().get_graphiql_response()

        custom_script = """
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

        html = get_graphiql_html()
        html = html.replace("</body>", f"{custom_script}</body>")
        return HTMLResponse(html)
