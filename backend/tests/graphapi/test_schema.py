# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from fastapi.testclient import TestClient


def test_no_void_scalar(raw_client: TestClient, latest_graphql_url: str) -> None:
    """
    Mutations with void-result go against GraphQL best-practices.

    `null` is not a GraphQL type. You need to specify a return value as a type
    (e.g. `String`, `Boolean` etc). Types can be _nullable_, i.e. the value can
    be `null`, and, in fact, they are nullable by default (unless you define
    them with `!`).

    Therefore, it is not possible in standard GraphQL to define a void/null return
    type. Some GraphQL servers, like Strawberry, add support by introducing a
    `Void` scalar, but it is poorly supported across the ecosystem.

    https://strawberry.rocks/docs/general/mutations#mutations-without-returned-data
    """
    schema = raw_client.get(f"{latest_graphql_url}/schema.graphql")
    assert "scalar Void" not in schema.text.splitlines()
