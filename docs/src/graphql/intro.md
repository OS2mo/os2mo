---
title: OS2mo GraphAPI
---

OS2mo version 2.4.0 introduced a new endpoint, `/graphql`, that serves a [GraphQL](https://graphql.org/) based API. The documentation found in this section focuses on how to interact with this new endpoint.

Graph APIs differ from REST APIs in key areas. Most notably, they only operate on a single endpoint and data is obtained using `POST` requests to this endpoint with queries in the request body.


## Quickstart
Data from graph APIs is obtained by defining queries. For example, to query the name of all IT systems available in MO:

```bash
# bash
curl -X POST -H "Content-Type: application/json" \
     --data '{"query": "{itsystems{name}}"}' \
     https://example.com/mo/graphql
```
```pwsh
# Powershell
(Invoke-Webrequest https://example.com/mo/graphql `
    -Body '{"query": "{itsystems{name}}"}' `
    -Method 'POST' -ContentType 'application/json' `
).Content
```

Both of the above will return JSON data similar to

```json
{
  "data": {
    "itsystems": [
      {
        "name": "SAP"
      },
      {
        "name": "Office365"
      }
    ]
  }
}
```


## GraphQL Voyager
The OS2mo graph model can be interactively explored via our [OS2mo | GraphQL Voyager](voyager.html) instance. It is updated on every MO release, meaning it will always reflect the latest graph model.

## GraphiQL
It is possible to configure development and testing servers to expose [GraphiQL](https://github.com/graphql/graphiql/tree/main/packages/graphiql), an interactive in-browser GraphQL IDE. GraphiQL is useful for testing out queries and exploring the data model.

Per [GraphQL best practices](https://graphql.org/learn/serving-over-http/#graphiql) for serving over HTTP, GraphiQL will always be turned off in production.
