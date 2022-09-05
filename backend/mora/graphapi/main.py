# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
def setup_graphql(enable_graphiql: bool = False) -> GraphQLRouter:
    schema = get_schema()

    gql_router = GraphQLRouter(
        schema, context_getter=get_context, graphiql=enable_graphiql
    )

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    return gql_router
