from mora.graphapi.shim import execute_graphql


async def test_query_context():

    query = "query ($uuids: [UUID!]!) {org_units (uuids: $uuids) {uuid}}"
    variables = {"uuids": "f06ee470-9f17-566f-acbe-e938112d46d9"}
    response = await execute_graphql(query=query, variable_values=variables)
    assert response.errors is None
