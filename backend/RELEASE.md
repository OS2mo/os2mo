Release type: minor

[#50647] Add versioning to the GraphQL API

Clients should always refer and pin themselves to a specific version of the
GraphQL API, which is available on /graphql/vX. Navigating to /graphql in a
browser will redirect to GraphiQL for the latest version.
POSTing to the legacy /graphql endpoint is still supported for compatibility,
but support will be dropped in the near future.
