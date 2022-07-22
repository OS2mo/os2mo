from strawberry.fastapi import GraphQLRouter


def get_router() -> GraphQLRouter:
    router = GraphQLRouter(
        schema_v1, context_getter=get_context, graphiql=enable_graphiql
    )
    return router
