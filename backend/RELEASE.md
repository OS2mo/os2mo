Release type: patch

[#51872] Fix GraphQL schema context extension

We need to store a reference counter, instead of a simple boolean, to
ensure we do not set is_graphql=False as soon as the first nested schema
execution exits.
