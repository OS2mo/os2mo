---
title: Introduction
---

[OS2mo version 2.4.0](../../changelog.md#240-2021-09-23) introduced a new
endpoint; `/graphql`, which serves a [GraphQL](https://graphql.org/) API.

The goal of this API is to become the standard and only way to to interact with
OS2mo, completely eliminating the need for all the previous APIs of OS2mo.

This documentation serves as an introduction to guide integration writers to
how to write integrations for OS2mo. It does not aim to teach the reader about
GraphQL, but rather seeks to introduce and document OS2mo-specifics.

For a general introduction to GraphQL, please seek out other guides online.

## Quickstart

Data can be extracted from the API by running queries against the GraphQL
endpoint. For example, to query the name of all IT systems available in MO:

```bash
# bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer ..." \
     --data '{"query": "{itsystems {objects {name}}}"}' \
     https://example.com/mo/graphql/v6
```

```pwsh
# Powershell
(Invoke-Webrequest https://example.com/mo/graphql/v6 `
    -Body '{"query": "{itsystems {objects {name}}}"}' `
    -Method 'POST' -ContentType 'application/json' `
    -Headers @{ Authorization = "Bearer ..." } `
).Content
```

Both of which will return a JSON response similar to:

```json
{
  "data": {
    "itsystems": {
      "objects": [
        {
          "name": "SAP"
        },
        {
          "name": "Office365"
        }
      ]
    }
  }
}
```

Similarly data can be changed by running a mutation instead of a query on the
same GraphQL endpoint.

To get GraphQL calls executed the caller must include a sufficiently privileged
access token in the `Authorization` header. For details on how to acquire such
a token, please read the [Authentication documentation](../iam/auth.md).

## Versioning

The OS2mo GraphQL interface is versioned to handle future breaking changes,
without actually breaking any integration code. New versions are added as
needed and old versions are removed as they become obsolete.

New integrations should always use the newest version of the interface
available, and old integrations should continuously be updated to the newer
versions as they are introduced, by following the [Migration Guide](migration.md).

The `/graphql` endpoint redirects the browser to the GraphiQL interface for the
newest version, e.g. for local development: <http://localhost:5000/graphql>.
GraphiQL has a built-in documentation explorer which can be accessed by
ctrl-clicking most fields.

There is no way to use the newest version of the GraphQL interface
programmatically, e.g. from integrations. This is by design to avoid
integrations being broken automatically once a new version is introduced, as
such, all integrations should be hardcoding the GraphQL version that they are
utilising and should update this hardcoded URL as they upgrade to a newer
version following the migration guide.

The GraphQL schema for each version is available at
`/graphql/vXX/schema.graphql` in regular GraphQL Schema Definition Language
(SDL).

## Pagination

The OS2mo GraphQL interface is paginated to handle large data quantities.

All queries should utilize pagination by default, unless the integration
developer can somehow guarantee that the data quantity will never grow
large enough that a query may time.

In a future GraphQL version a strict timeout may be introduced, to ensure that
all queries execute and return in a reasonable amount of time, thus
necessitating proper use of pagination at that time.

## API documentation

As GraphQL is self-descriptive by nature, this documentation does not contain
any API documentation, rather such API documentation can retrieved over the
GraphQL protocol by using introspection queries, or by using a development tool,
which runs these queries on behalf of the user.

OS2mo ships with two such tools, namely the GraphQL Voyager model and GraphiQL
interactive development environment.

### GraphQL Voyager

The GraphQL Voyager is a tool used to interactively explore the OS2mo graph
model, visually seeing the entities that are available and their relations.

It is integrated with this documentation can be found here:
[OS2mo | GraphQL Voyager](voyager.html).

It is always updated to show the latest version of the GraphQL interface.

## GraphiQL

The GraphiQL interactive in-browser GraphQL IDE serves a different purpose than
the GraphQL Voyager, whereas the Voyager is useful in getting an overall feel
for the interface, the GraphiQL IDE is much more development focused, easing
integration developers in finding the right queries for their integrations.

It is automatically deployed on all OS2mo instances and can be found by going
to `https://{{mo_url_here}}/graphql`. When accessing this URL the browser will
redirect the user to login in Keycloak, to get the appropriate credentials for
which the developed queries will be run under.

The IDE features an interactive query window with autocompletion, a result
window where query responses are shown, a subwindow to input query variables
and custom headers, a schema and documentation explorer and a history of
previously run queries. It is the suggested development environment for GraphQL
queries in OS2mo, although a pletora of tools can be used, such as Postman.
