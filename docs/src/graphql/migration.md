---
title: Migration Guide
---

This migration guide serves to help integration developers in migrating their
GraphQL queries from older versions of OS2mo's GraphQL interface to newer ones.

It is recommended that a systematic approach is token to migrating, upgrading
from the current version to the subsequent one over and over again until the
code is up-to-date with the latest version.

Below follows the migration guide for each version.

## Version 6

GraphQL version 6 introduces a breaking change to the `facet_create`-mutator.

In version 5 the `facet_create`-mutator is implemented atop the
`RADataModel`'s `LoraFacet` and calls LoRa through the intern ASGI app.
However in version 6 the mutator is instead implemented as a very thin
translation directly atop LoRas `create_or_import_object` function.

Although this change was planned to be a pure refactoring, several
issues were identified during the refactoring, eventually leading to
the refactoring becoming a breaking change motivating the new version of
the GraphQL interface.

These issues are listed below, from the following motivating mutation:
```graphql
mutation CreateFacet {
  facet_create(input: {
    type: "facet"
    uuid: "00000000-fee1-baad-fa11-dead2badc0de"
    user_key: "EmployeeAddressType"
    org_uuid: "3b866d97-0b1f-48e0-8078-686d96f430b3"
    parent_uuid: "182df2a8-2594-4a3f-9103-a9894d5e0c36"
  }) {
    uuid
  }
}
```
This mutation call is valid in version 5, but has several issues:

* `type` is an optional argument that shall *always* have its value
  set to: `facet`. Setting it to any other value will break invariants
  in the underlying code leading to undefined behavior.
  The argument has the default value of `facet` and as such the issue
  only arises if the caller explicitly sends a different value.
  The argument has however been removed entirely in version 6, as it
  is leaking implementation-specific details and should never have been
  exposed.
* `uuid` is an optional argument used for explicitly setting the UUID
  to be assigned to the newly created facet.
  We generally prefer entities to have randomly generated UUIDs instead
  of predetermined ones to avoid issues such as UUID conflicts.
  The argument has the default of using randomly generated UUIDs.
  The argument has been been removed entirely in version 6, opting to
  instead always generate random UUIDs for newly created facets.
* `org_uuid` is a required argument that shall *always* have its value
  set to the root organisation's UUID. Setting it to any other value
  will break invariants in the underlying code leading to undefined
  behavior.
  The argument does not have a default value, and as such the caller
  has to look up the UUID of the root organisation whenever they want to
  create a new facet.
  The argument has been removed entirely in version 6, as it is leaking
  implementation-specific details and should never have been exposed.
* `parent_uuid` is an optional argument, which was supposed to set the
  facet's parent relation to the UUID provided, however in version 5 it
  does nothing whatsoever, and is a completely ignored.
  The argument has been removed entirely in version 6, as having dead
  code exposed in the interface is an anti-pattern. The argument may be
  reintroduced in the future, but in a functional way.

Thus in version 6 the above motivation mutation would now look like the
following instead:
```graphql
mutation CreateFacet {
  facet_create(input: {
    user_key: "EmployeeAddressType"
  }) {
    uuid
  }
}
```
Vastly simplifying the interface and avoiding the predetermined,
non-random UUID anti-pattern.

To migrate from GraphQL version 6, simply stop sending `type`, `uuid`
`org_uuid` and `facet_parent` with your queries. If you happen to "need"
to set the `uuid` please get in contact so we can discuss potential
solutions.


## Version 5

GraphQL version 5 introduces a major breaking change to the entire reading
schema, following from a restructuring to introduce pagination for all
multi-element data-types.

The pagination is implemented via cursor-based pagination, for more
details check: https://strawberry.rocks/docs/guides/pagination/cursor-based

The old non-paginated reading schema is still available in version 4 and
all other previous versions.

In version 4 and previous versions querying high element count data-types
had a tendency to timeout due to the sheer number of elements which had
to be fetched and transformed from the database. The timeout issue could
even occur on low element count data-types given sufficiently complex
queries.

Various workarounds and hacks was being employed to work around this
issue, such as implementing pagination for complex queries client side,
by initially only requesting the UUIDs of elements in the first query,
and then sending a sequence of complex queries each with a subset of the
UUIDs returned by the initial query.

It is our hope that the new paginated version of the reading schema will
eliminate the need for such workarounds, thus allowing the caller to
specify their query with exactly the data that they need and desire,
choosing a pagination limit that allows the query to return within the
timeout limit.

To migrate to the new paginated schema, without actually utilizing the
pagination simply change all current GraphQL calls from version 4
(`/graphql/v4`) to version 5 (`/graphql/v5`), and modify your call from:
```graphql
{
  employees {
    uuid
    objects {
      givenname
    }
  }
}
```
to:
```graphql
{
  employees {
    objects {
      uuid
      objects {
        givenname
      }
    }
  }
}
```
And modify the code that extracts the data from:
```python
result = client.execute(query)
employees = result["employees"]
```
to:
```
result = client.execute(query)
employees = result["employees"]["objects"]
```

To actually utilize the pagination a little more work must be put in.
First the above query must be parameterized, as such:
```graphql
query PaginatedEmployees($cursor: Cursor) {
  employees(limit: 2, cursor: $cursor) {
    objects {
      uuid
      objects {
        user_key
      }
    }
    page_info {
      next_cursor
    }
  }
}
```
Requesting 2 employees in the response via the `limit` parameter,
yielding a response alike this:
```
{
  "data": {
    "employees": {
      "objects": [
        ...  # 2 employee objects here
      ],
      "page_info": {
        "next_cursor": "Mg=="
      }
    }
  }
}
```
Now as the implementation is cursor-based, to fetch the next two
employees we must provide the value from `next_cursor` (`"Mg=="`) in the
`cursor` argument of our query in the next iteration, repeating for each
iteration until the `next_cursor` becomes `null` at which point the data
has been exhausted and all data entries have been iterated through.

It is very much recommended to put in the extra work and ensure that
pagination is actually used, rather than just relying on everything being
delivered as a single big page. Relying on this behavior is very likely to
break the integration in the future as data quantities grow.

## Version 4

GraphQL version 4 introduces a breaking change to the `class_create`-mutator.

In version 3 the `class_create`-mutator is implemented atop the
`ClassRequestHandler` and thus atop the entire Service API to LoRa
translation layer.
However in version 4 the mutator is instead implemented as a very thin
translation directly atop LoRas `create_or_import_object` function.

Although this change was planned to be a pure refactoring, several
issues were identified during the refactoring, eventually leading to
the refactoring becoming a breaking change motivating the new version of
the GraphQL interface.

These issues are listed below, from the following motivating mutation:
```graphql
mutation CreateClass {
  class_create(input: {
    type: "class"
    uuid: "00000000-fee1-baad-fa11-dead2badc0de"
    name: "Office Number"
    user_key: "EmployeeOfficeNumber"
    scope:"TEXT"
    facet_uuid: "5b3a55b1-958c-416e-9054-606b2c9e4fcd"
    org_uuid: "3b866d97-0b1f-48e0-8078-686d96f430b3"
  }) {
    uuid
  }
}
```
This mutation call is valid in version 3, but has several issues:

* `type` is an optional argument that shall *always* have its value
  set to: `class`. Setting it to any other value will break invariants
  in the underlying code leading to undefined behavior.
  The argument has the default value of `class` and as such the issue
  only arises if the caller explicitly sends a different value.
  The argument has however been removed entirely in version 4, as it
  is leaking implementation-specific details and should never have been
  exposed.
* `uuid` is an optional argument used for explicitly setting the UUID
  to be assigned to the newly created class.
  We generally prefer entities to have randomly generated UUIDs instead
  of predetermined ones to avoid issues such as UUID conflicts.
  The argument has the default of using randomly generated UUIDs.
  The argument has been been removed entirely in version 4, opting to
  instead always generate random UUIDs for newly created classes.
* `org_uuid` is a required argument that shall *always* have its value
  set to the root organisation's UUID. Setting it to any other value
  will break invariants in the underlying code leading to undefined
  behavior.
  The argument does not have a default value, and as such the caller
  has to look up the UUID of the root organisation whenever they want to
  create a new class.
  The argument has been removed entirely in version 4, as it is leaking
  implementation-specific details and should never have been exposed.

Thus in version 4 the above motivation mutation would now look like the
following instead:
```graphql
mutation CreateClass {
  class_create(input: {
    name: "Office Number"
    user_key: "EmployeeOfficeNumber"
    scope:"TEXT"
    facet_uuid: "5b3a55b1-958c-416e-9054-606b2c9e4fcd"
  }) {
    uuid
  }
}
```
Vastly simplifying the interface and avoiding the predetermined,
non-random UUID anti-pattern.

To migrate from GraphQL version 3, simply stop sending `type`, `uuid`
and `org_uuid` with your queries. If you happen to "need" to set the
`uuid` please get in contact so we can discuss potential solutions.


## Version 3

GraphQL version 3 introduced a breaking change to the healths top-level type
by introducing pagination to the endpoint.

To query all healthchecks from OS2mo in GraphQL Version 2, run:
```graphql
query {
  healths {
    identifier
    status
  }
}
```
Which will result in a result similar to:
```
{
  "data": {
    "healths": [
      {
        "identifier": "amqp",
        "status": true
      }
    ]
  }
}
```

While to fetch the same data under GraphQL Version 3, one must run:
```graphql
query {
  healths {
    objects {
      identifier
      status
    }
  }
}
```
Which will result in a result similar to:
```
{
  "data": {
    "healths": {
      "objects": [
        {
          "identifier": "amqp",
          "status": true
        }
      ]
    }
  }
}
```

As can be seen Version 3 introduces an extra layer to the query and
correspondingly to the response. Migrating thus simply requires expanding the
queries with one extra layer, and similarly stripping one extra layer when
processing the result.

Doing this bypasses the pagination by fetching everything as a single big page,
and while this is generally discouraged, healths is one of the few data types
for which it may make sense, as we do not expect a huge list of healthpoints to
be introduced. That being said, this is no guarantee and not implementing the
pagination means risking potential breakage in the future.


## Version 2

GraphQL version 2 introduced a breaking change to the parent relation on
organisation units.

Assuming a query alike:
```graphql
query OrganisationUnitParentQuery {
  org_units(uuids: [$uuid]) {
    current {
      parent {
        uuid
      }
    }
  }
}
```
The result on version 1 of GraphQL would be:
```json
{
  "data": {
    "org_units": [
      {
        "current": {
          "parent": [
            {
              "uuid": "2665d8e0-435b-5bb6-a550-f275692984ef"
            }
          ]
        }
      }
    ]
  }
}
```
While on version 2 of GraphQL the result would be:
```
{
  "data": {
    "org_units": [
      {
        "current": {
          "parent": {
            "uuid": "2665d8e0-435b-5bb6-a550-f275692984ef"
          }
        }
      }
    ]
  }
}
```
The difference is subtle, namely that parent used to return a single element
list containing the parent object, while it now returns an optional parent
object instead.

Thus to migrate from version 1 to version 2, simply remove whatever code that
extracts the element from within the list, and use the element directly.
