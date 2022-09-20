Release type: minor

[#50861] Make GraphQL org unit parent return an optional single object.
The old behaviour -- returning an optional _list_, which always contained
exactly one element -- has been deprecated, but will continue to work in the v1
GraphQL API until 2023-03-01. Consumers should upgrade to /graphql/v2 as soon as
possible.
