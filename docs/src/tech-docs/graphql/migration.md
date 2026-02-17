# Migration Guide

This migration guide serves to help integration developers in migrating their
GraphQL queries from older versions of OS2mo's GraphQL interface to newer ones.

It is recommended that a systematic approach is token to migrating, upgrading
from the current version to the subsequent one over and over again until the
code is up-to-date with the latest version.

Below follows the migration guide for each version.

## Version 29

Prior to this version, dates in the GraphQL API would often be off-by-one. This
is no longer the case. For example:

```graphql
mutation CreateOrgUnit {
  org_unit_create(
    input: {
      name: "create"
      validity: {
        from: "2021-01-01T00:00:00+01:00"
        to: "2023-03-03T00:00:00+01:00"
      }
    }
  ) {
    uuid
  }
}

mutation UpdateOrgUnit {
  org_unit_update(
    input: {
      name: "update"
      validity: {
        from: "2022-02-02T00:00:00+01:00"
        to: "2024-04-04T00:00:00+01:00"
      }
    }
  ) {
    uuid
  }
}

query ReadOrgUnit {
  org_units(filter: { uuids: [$uuid], from_date: null, to_date: null }) {
    objects {
      validities(start: null, end: null) {
        name
        validity {
          from
          to
        }
      }
    }
  }
}
```

**GraphQL v28** returns the wrong `to` date on the first validity, but it seems
like the `to` date on the second validity is correct:

```json
{
  "validities": [
    {
      "name": "create",
      "validity": {
        "from": "2021-01-01T00:00:00+01:00",
        "to": "2022-02-01T00:00:00+01:00"
      }
    },
    {
      "name": "update",
      "validity": {
        "from": "2022-02-02T00:00:00+01:00",
        "to": "2024-04-04T00:00:00+02:00"
      }
    }
  ]
}
```

_This is not the case, however_. This does not correspond to the data in the
database! The object will actually be valid until `2024-04-05 00:00:00`, _a day
later_ than indicated by the GraphQL response and requested in the mutators.

```text
 id  |                             virkning                             | gyldighed | organisationenhed_registrering_id
-----+------------------------------------------------------------------+-----------+-----------------------------------
   1 | ("[""2021-01-01 00:00:00+01"",""2023-03-04 00:00:00+01"")",,,"") | Aktiv     |                                 1
   2 | ("[""2021-01-01 00:00:00+01"",""2022-02-02 00:00:00+01"")",,,"") | Aktiv     |                                 2
   3 | ("[""2022-02-02 00:00:00+01"",""2024-04-05 00:00:00+02"")",,,"") | Aktiv     |                                 2
```

**GraphQL v29** returns and saves the correct data:

```json
{
  "validities": [
    {
      "name": "create",
      "validity": {
        "from": "2021-01-01T00:00:00+01:00",
        "to": "2022-02-02T00:00:00+01:00"
      }
    },
    {
      "name": "update",
      "validity": {
        "from": "2022-02-02T00:00:00+01:00",
        "to": "2024-04-04T00:00:00+02:00"
      }
    }
  ]
}
```

```text
 id  |                             virkning                             | gyldighed | organisationenhed_registrering_id
-----+------------------------------------------------------------------+-----------+-----------------------------------
   1 | ("[""2021-01-01 00:00:00+01"",""2023-03-03 00:00:00+01"")",,,"") | Aktiv     |                                 1
   2 | ("[""2021-01-01 00:00:00+01"",""2022-02-02 00:00:00+01"")",,,"") | Aktiv     |                                 2
   3 | ("[""2022-02-02 00:00:00+01"",""2024-04-04 00:00:00+02"")",,,"") | Aktiv     |                                 2
```

Worse, when terminating:

```graphql
mutation TerminateOrgUnit {
  org_unit_terminate(
    input: {
      ...
      from: "2021-12-12T00:00:00+01:00"
      to: "2022-12-12T00:00:00+01:00"
    }
  ) {
    uuid
  }
}
```

**GraphQL v28** _seems_ to terminate the validity from `2021-12-11 00:00:00`, a
day _earlier_ than we requested, and until `2022-12-13 00:00:00`, a day _later_
than we requested.

```json
{
  "validities": [
    {
      "name": "create",
      "validity": {
        "from": "2021-01-01T00:00:00+01:00",
        "to": "2021-12-11T00:00:00+01:00"
      }
    },
    {
      "name": "update",
      "validity": {
        "from": "2022-12-13T00:00:00+01:00",
        "to": "2024-04-04T00:00:00+02:00"
      }
    }
  ]
}
```

Looking in the database, however, we see that, actually, the object is
terminated from `2021-12-12 00:00:00` - `2022-12-13 00:00:00`, so only a day
too long.

```text
 id  |                             virkning                             | gyldighed | organisationenhed_registrering_id
-----+------------------------------------------------------------------+-----------+-----------------------------------
   1 | ("[""2021-01-01 00:00:00+01"",""2023-03-04 00:00:00+01"")",,,"") | Aktiv     |                                 1
   2 | ("[""2021-01-01 00:00:00+01"",""2022-02-02 00:00:00+01"")",,,"") | Aktiv     |                                 2
   3 | ("[""2022-02-02 00:00:00+01"",""2024-04-05 00:00:00+02"")",,,"") | Aktiv     |                                 2
   4 | ("[""2021-01-01 00:00:00+01"",""2021-12-12 00:00:00+01"")",,,"") | Aktiv     |                                 3
   5 | ("[""2021-12-12 00:00:00+01"",""2022-12-13 00:00:00+01"")",,,"") | Inaktiv   |                                 3
   6 | ("[""2022-12-13 00:00:00+01"",""2024-04-05 00:00:00+02"")",,,"") | Aktiv     |                                 3
```

**GraphQL v29** again returns and saves the expected data:

```json
{
  "validities": [
    {
      "name": "create",
      "validity": {
        "from": "2021-01-01T00:00:00+01:00",
        "to": "2021-12-12T00:00:00+01:00"
      }
    },
    {
      "name": "update",
      "validity": {
        "from": "2022-12-12T00:00:00+01:00",
        "to": "2024-04-04T00:00:00+02:00"
      }
    }
  ]
}
```

```text
 id  |                             virkning                             | gyldighed | organisationenhed_registrering_id
-----+------------------------------------------------------------------+-----------+-----------------------------------
   1 | ("[""2021-01-01 00:00:00+01"",""2023-03-03 00:00:00+01"")",,,"") | Aktiv     |                                 1
   2 | ("[""2021-01-01 00:00:00+01"",""2022-02-02 00:00:00+01"")",,,"") | Aktiv     |                                 2
   3 | ("[""2022-02-02 00:00:00+01"",""2024-04-04 00:00:00+02"")",,,"") | Aktiv     |                                 2
   4 | ("[""2021-01-01 00:00:00+01"",""2021-12-12 00:00:00+01"")",,,"") | Aktiv     |                                 3
   5 | ("[""2021-12-12 00:00:00+01"",""2022-12-12 00:00:00+01"")",,,"") | Inaktiv   |                                 3
   6 | ("[""2022-12-12 00:00:00+01"",""2024-04-04 00:00:00+02"")",,,"") | Aktiv     |                                 3
```

**So, to migrate:** If you previously accounted for these discrepancies by
adding or subtracting a day, or if you assumed behaviour such as "the 'to' date
implicitly includes until `23:59:59` that day", **simply remove all of these
workarounds when upgrading**. The date**time** of all validities is now
accurate to the second, so if an object is valid until `2020-02-02 00:00:00`
that _actually_ means `2020-02-02` at midnight (between `2020-02-01 23:59:59`
and `2020-02-02 00:00:01`).

All intervals follow the commonly accepted standard that the lower bound is
inclusive and the upper bound is exclusive (`[)`).

## Version 28

This version fixes `OrganisationUnit` returning inconsistent
`parent_uuid`/`parent`/`parent_response` for organisation units without a
parent:

```json
{
  "data": {
    "org_units": {
      "objects": [
        {
          "current": {
            "parent_uuid": "<root org uuid>",
            "parent": null,
            "parent_response": {
              "uuid": "<root org uuid"
            }
          }
        }
      ]
    }
  }
}
```

The root org concept is deprecated in OS2mo, and it should not leak to
organisation units. GraphQL v28 correctly returns `null` for top-level units:

```json
{
  "data": {
    "org_units": {
      "objects": [
        {
          "current": {
            "parent_uuid": null,
            "parent": null,
            "parent_response": null
          }
        }
      ]
    }
  }
}
```

You can use the `org` field in GraphQL if you still need to UUID of the
organisation.

## Version 27

GraphQL version 27 introduces a very minor breaking change to the `registrations`
field on the various `Response` objects (i.e. `FacetResponse`), changing its
return-type from `Registration` to the generic `ResponseRegistration`
(i.e. `FacetResponseRegistration`) ensuring that each concrete `Response` type
has a corresponding concrete `ResponseRegistration` type.

We believe very few users should be affected by this change, but if needed,
the migration path is very simple, simply update any references in for instance
`FacetResponse`'s `registrations` field from `Registration` to its now collection
specific concrete implementation `FacetResponseRegistration` or similar.


## Version 26

GraphQL version 26 introduces a very minor breaking change to the `registrations`
top-level collection, changing its return-type from `Registration` to
`IRegistration`, i.e. from a concrete type to an interface with a plethora of
concrete implementations, for instance `FacetRegistration`.

We believe very few users should be affected by this change, but if needed,
the migration path is very simple, simply update any references from
`Registration` to `IRegistration`.


## Version 25

GraphQL version 25 introduces a very minor breaking change to the `managers`
`employee` filter, specifically the behavior when this filter is set to `null`.

Prior to GraphQL version 25 setting `employee: null` inside `managers` was
equivalent to not providing the `employee` filter whatsoever, as `null` and
`UNSET` was treated identically.

However in GraphQL version 25, `null` means where the `employee` reference is
empty, aka. vacant manager positions, whereas `UNSET` aka. not supplying the
filter does not do any filtering whatsoever similar to `None` in prior versions.

We believe very few users should be affected by this change, but if needed,
the migration path is very simple, simply stop passing `employee: null` as a
filter and instead omit the filter entirely.


## Version 24

GraphQL version 24 introduces a very minor breaking change to the `managers`
filter type when accessed from within the `org_units` top-level collection.

The change is best explained with an example:
```graphql
query {
  org_units {
    objects {
      current {
        managers(
          filter: {}  # <-- The type of this filter is changed
        ) {
          uuid
        }
      }
    }
  }
}
```
Here the type of the filter is changed from `ManagerFilter` to
`OrgUnitsboundmanagerfilter`, while the type of the filter remains
unchanged (as `ManagerFilter`) in the following case:
```graphql
{
  managers(
    filter: {}  # <-- The type of this filter is NOT changed
	) {
    objects {
      current {
        uuid
      }
    }
  }
}
```

The change to `OrgUnitsboundmanagerfilter` serves to indicate that it is no
longer possible to pass `org_units` to the `managers` field in the first example.
While this was possible prior to the change, it would have no effect as the code
would simply override the given filter value with the contextual value.
Thus the only real breaking change is the type of the filter.

As such to migrate from GraphQL v22, simply update the type of the filter, and
if you were sending org_units in simply remove it, as it had no effect.


## Version 23

This version changes the type of the `kle_number` field on `KLE` from `Class!`
to `[Class!]!`. It is now the same type as its sibling `kle_aspects` field.

The previous typing incorrectly assumed that KLE-number classes were static;
valid from -infinity to infinity and never changing. Attempting to read a `KLE`
with a `kle_number` in the past or future would therefore lead to an error,
since the promise of always returning a single KLE class could not be
fulfilled. The field now returns a -- potentially empty -- list of classes
valid in the given time period.


## Version 22

GraphQL version 22 introduces breaking changes to the `org_unit_update`
mutator, specifically with regards to the way `UNSET` (arguments not send)
and `null` / `None` (arguments explicitly to clear the value) are handled.

Prior to the change most fields on the mutator were required, with some
fields allowing `null`s, however sending `null`s did not clear the fields,
rather `null`s where simply ignored similar to unset fields.

In the new version most fields are optional, with unset fields retaining
the prior behavior of not clearing the fields, but rather doing nothing,
while sending `null`s now specifically request clearing the value of the
field (if possible).

Thus this commit enables HTTP PATCH semantics, where a single field can
be updated and cleared without affecting the remaining fields on the
object. This is the first mutator to undergo this treatment, but the
plan is for all update mutators to exhibit this behavior.

As such to migrate from GraphQL v21, simply send the query as normal:
```graphql
mutation OrgUnitUpdate($input: OrganisationUnitUpdateInput!) {
    org_unit_update(input: $input) {
        uuid
    }
}
```
But ensure that the provided `input` payload has undergone a
transformation, where all `null` values are stripped from the payload:
```json
{
  "uuid": "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
  "validity": {"from": "2020-01-01"},
  "name": "new_org_name",
  "parent": null
}
```
to:
```
```json
{
  "uuid": "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
  "validity": {"from": "2020-01-01"},
  "name": "new_org_name"
}
```

## Version 21

Prior to this version, the first `from_date` or `to_date` filter parameters were
automatically, implicitly, and forcefully inherited in all the following levels of the
query. For example, a query such as:
```graphql
query GetOrgUnitEngagements {
  org_units(filter: {from_date: null, to_date: null}) {
    objects {
      objects {
        engagements(filter: {from_date: "1760-01-01", to_date: "1840-01-01"}) {
          uuid
        }
      }
    }
  }
}
```
could, confusingly, return engagements from today, instead of only those from the
industrial revolution, as requested. This is no longer the case, and as such date
filtering is correctly applied at each level of the query. This also means that for a
query such as
```graphql
query GetOrgUnitEngagements {
  org_units(filter: {from_date: null, to_date: null}) {
    objects {
      objects {
        engagements {
          uuid
        }
      }
    }
  }
}
```
`engagements` will no longer implicitly inherit the `{from_date: null, to_date: null}`
filter from `org_units`.

Users who wish to maintain the old behaviour should explicitly pass the same date
filters at each level of their query:
```graphql
query GetOrgUnitEngagements {
  org_units(filter: {from_date: null, to_date: null}) {
    objects {
      objects {
        engagements(filter: {from_date: null, to_date: null}) {
          uuid
        }
      }
    }
  }
}
```


## Version 20

Prior to this version, `facets` ignored `start_date` and `end_date` filtering.
For this reason, a query like
```graphql
query GetFacet {
  facets {
    objects {
      current {
        user_key
      }
    }
  }
}
```
would, confusingly, return empty `current` objects:
```json
{
  "facets": {
    "objects": [
      {
        "current": None,
      }
    ]
  }
}
```

This is no longer the case. Users who wish to retrieve the full facet history
should utilise a query such as:
```graphql
query GetFacet {
  facets(filter: {from_date: null, to_date: null}) {
    objects {
      objects {
        user_key
      }
    }
  }
}
```


## Version 19

GraphQL version 19 introduces breaking changes to a few terminate endpoints.
Specifically the `class_terminate`, `facet_terminate` and `itsystem_terminate`
mutators.

The breaking changes are similar for all the endpoints, namely that the
`validity` argument has been inlined, such that these mutators are now aligned
with the rest of the terminate mutators.

As such to migrate from GraphQL v18, simply send the input as normal:
```graphql
mutation FacetTerminate($input: FacetTerminateInput!){
    facet_terminate(input: $input) {
        uuid
    }
}
```
But ensure that the provided `input` payload has undergone the following transformation:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "validty": {
    "to": "2023-01-01"
  }
}
```
to:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "to": "2023-01-01"
}
```
With a similar transformation for all calls to the other two mutators.

## Version 18

GraphQL version 18 introduces breaking changes to the `auditlog`'s `models` filter.
Specifically it changes the type from an unconstrained string to a structured enum.

To migrate to GraphQL v18, simply send queries as you do now, but modify the
`models` filter value according to the below table:

| v17                    | v18                     |
|------------------------|-------------------------|
| `AuditLog`             | `AUDIT_LOG`             |
| `Bruger`               | `PERSON`                |
| `Facet`                | `FACET`                 |
| `ItSystem`             | `IT_SYSTEM`             |
| `Klasse`               | `CLASS`                 |
| `Organisation`         | `ORGANISATION`          |
| `OrganisationEnhed`    | `ORGANISATION_UNIT`     |
| `OrganisationFunktion` | `ORGANISATION_FUNCTION` |

Additionally you should translate the `model` field in responses according to the
above table as well.

## Version 17

GraphQL version 17 introduces breaking changes to a few class related endpoints.
Specifically the `class_create` and the `class_update` mutators.

The breaking changes to the `class_create` and `class_update` mutators are that
both now require a `validity` argument in their input types. Allowing for bitemporal
changes to the underlying data-entity.

As such to migrate from GraphQL v16, simply send the input as normal:
```graphql
mutation ClassUpdate($input: ClassUpdateInput!){
    class_update(input: $input) {
        uuid
    }
}
```
But ensure that the provided `input` payload has undergone the following transformation:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "name": "TestClass",
  "user_key": "testclass",
}
```
to:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "name": "TestClass",
  "user_key": "testclass",
  "validity": {
      "from": null,
      "to": null
  }
}
```

## Version 16

GraphQL version 16 introduces breaking changes to a few facet related endpoints.
Specifically the `facet_create` and the `facet_update` mutators.

The breaking changes to the `facet_create` and `facet_update` mutators are that
both now require a `validity` argument in their input types. Allowing for bitemporal
changes to the underlying data-entity.

As such to migrate from GraphQL v15, simply send the input as normal:
```graphql
mutation FacetUpdate($input: FacetUpdateInput!){
    facet_update(input: $input) {
        uuid
    }
}
```
But ensure that the provided `input` payload has undergone the following transformation:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "user_key": "Test",
}
```
to:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "user_key": "Test",
  "validity": {
      "from": null,
      "to": null
  }
}
```

## Version 15

GraphQL version 15 introduces breaking changes to a few itsystem related
endpoint. Specifically the `itsystem` query endpoint, and the `itsystem_create`
and the `itsystem_update` mutators.

The breaking changes to the `itsystem` query endpoint as it is simply a filter that
has been given a new type, as such it only affects users that explicitly typed the filter
in their query, to migrate from GraphQL v14 in such case, simply rename the filter
type:
```graphql
query ITSystemsRead($filter: BaseFilter){
    itsystems(filter: $filter) {
        ...
    }
}
```
to:
```graphql
query ITSystemsRead($filter: ITSystemFilter){
    itsystems(filter: $filter) {
        ...
    }
}
```

The breaking changes to the `itsystem_create` and `itsystem_update` mutators are
a little more involved. First up the `itsystem_update` mutator now takes the
`ITSystemUpdateInput` input-type, whereas GraphQL v14 unintentionally took the
`ITSystemCreateInput` input-type. The newly introduced `ITSystemUpdateInput`
input-type is still identical to its create counterpart, but keeping them separate
allows for future non-breaking changes.
The `ITSystemCreateInput` input-type itself has changed however as date arguments
are now given inside a nested `validity` container, rather than on the input type
itself. As such to migrate from GraphQL v15, simply fix the input type:
```graphql
mutation ITSystemUpdate($input: ITSystemCreateInput!){
    itsystem_update(input: $input) {
        uuid
    }
}
```
to:
```graphql
mutation ITSystemUpdate($input: ITSystemUpdateInput!){
    itsystem_update(input: $input) {
        uuid
    }
}
```
And ensure that the provided `input` payload has undergone the following transformation:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "user_key": "Test",
  "name": "Test",
  "from": "1990-01-01T00:00:00+01:00",
  "to": null
}
```
to:
```json
{
  "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
  "user_key": "Test",
  "name": "Test",
  "validity": {
      "from": "1990-01-01T00:00:00+01:00",
      "to": null
  }
}
```

## Version 14

GraphQL version 14 introduces a breaking change to the filter variables
taken by the resolvers. Specifically, it moves them from the top-level
to a `Filter` object.

To migrate from GraphQL v13, nest your filtering parameters in the
`filter` object, e.g. from:
```graphql
query AddressQuery {
  addresses(
    from_date: "2023-09-01",
    address_type_user_keys: "EmailEmployee",
  ) {
    objects {
      uuid
    }
  }
}
```
to
```graphql
query AddressQuery {
  addresses(
    filter: {
      from_date: "2023-09-01",
      address_type_user_keys: "EmailEmployee",
    },
  ) {
    objects {
      uuid
    }
  }
}
```

## Version 13

GraphQL version 13 introduces a breaking change to the input variables taken
by the `employee_create` and `employee_update`-mutators. Specifically it
removes the `name`, `nickname`, `cpr_no`, `givenname`, `from` and `to` input
variable, which were previously optional arguments.

As such `name` now has to be given using the structured form, using
`given_name` and `surname`, and correspondingly `nickname` has to be
given using `nickname_given_name` and `nickname_surname`. `cpr_no`
should be given using `cpr_number` while `from` and `to` should be given
via the `validity` argument. All of these arguments have been made
required and the mutually exclusivity validators have been removed.

To migrate from GraphQL version 12, make the following changes to your code:
* rename `givenname` to `given_name`
* rename `cpr_no` to `cpr_number`
* restructure `from` and `to` to `validity: {from: ..., to: ...}`
* recode `name` to `given_name` / `surname` as:
```
given_name, surname = name.rsplit(" ", 1)
```
* recode `nickname` similarly to `name`

## Version 12

GraphQL version 12 introduces a breaking change to the input variables taken
by the `ituser_create`-mutator. Specifically it removes the `type` input
variable, which was previously an optional argument that should *always* have
its value set to: `it`. Setting it to any other value will break
invariants in the underlying code leading to undefined behavior.

The argument had the default value of `it` and as such the issue
only arises if the caller explicitly sends a different value.
The argument has however been removed entirely in version 12, as it
is leaking implementation-specific details and should never have been
exposed.

To migrate from GraphQL version 11, simply stop sending `type` with your queries.

## Version 11

GraphQL version 11 introduces a breaking change to the input variables taken
by the `manager_create`-mutator. Specifically it removes the `type` input
variable, which was previously an optional argument that should *always* have
its value set to: `manager`. Setting it to any other value will break
invariants in the underlying code leading to undefined behavior.

The argument had the default value of `manager` and as such the issue
only arises if the caller explicitly sends a different value.
The argument has however been removed entirely in version 11, as it
is leaking implementation-specific details and should never have been
exposed.

To migrate from GraphQL version 10, simply stop sending `type` with your queries.

## Version 10

GraphQL version 10 introduces a breaking change to the input variables taken
by the `class_update`, `facet_update` and `itsystem_update` mutators.
These mutators took a separate `uuid` input variable besides the one contained
within the `input` object itself, leading to potential inconsistencies besides
the fact that it was not aligned with the other mutators.

In the future all mutators may get a `uuid` selector (and have `uuid` removed
from within the `input`), but this change, should it occur, will be introduced
in a new version, and will make the change consistently across all mutators.

This change simply aims to ensure consistency across our existing mutators.

To migrate from version 9 to version 10, remove the `uuid` parameter from
`class_update` (or `facet_update` / `itsystem_update`) and provide the `uuid`
inside the `input` object instead.

Version 9:
```graphql
mutation TestClassUpdate($input: ClassUpdateInput!, $uuid: UUID!) {
    class_update(input: $input, uuid: $uuid) {
        uuid
    }
}
```

Version 10:
```graphql
mutation TestClassUpdate($input: ClassUpdateInput!) {
    class_update(input: $input) {
        uuid
    }
}
```
Where `uuid` is now within `input`.


## Version 9

GraphQL version 9 introduces a breaking change to the input variable
name of the org_unit_terminate-mutator's input-variable, which did
not align with the other mutators.

To migrate from version 8 to version 9, change the name of
`org_unit_terminate`'s input-variable from `unit` to `input`.

Version 8:
```graphql
mutation TestTerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
    org_unit_terminate(unit: $input) {
        uuid
    }
}
```

Version 9:
```graphql
mutation TestTerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
    org_unit_terminate(input: $input) {
        uuid
    }
}
```


## Version 8

GraphQL version 8 introduces a breaking change to the name of the
`address_terminate`-mutator's input-variable, which didn't align with the other mutators.

To migrate from version 7 to version 8, change the name of
`address_terminate`'s input-variable from `at` to `input`.

Version 7:
```graphql
mutation TestTerminateAddress($input: AddressTerminateInput!) {
    address_terminate(at: $input) {
        uuid
    }
}
```

Version 8:
```graphql
mutation TestTerminateAddress($input: AddressTerminateInput!) {
    address_terminate(input: $input) {
        uuid
    }
}
```

## Version 7

GraphQL version 7 introduces a breaking change to the response formats for
the `facet`, `class` and `itsystems` data-types, ensuring that these
top-level types now return formats akin to the rest of the data types
in the interface ensuring uniformity across (bi-)temporal data-types.

Please note that this change does not in fact implement (bi-)temporality
for the mentioned data-types, but rather just adapt the interface in
preparation of the future implementation of (bi-)temporality.

To migrate to the new schema, change all current GraphQL calls from
version 6 (`/graphql/v6`) to version 7 (`/graphql/v7`) and modify
queries for the mentioned data-types, from:
```graphql
{
  facets {
    objects {
      user_key
    }
  }
}
```
to:
```
{
  facets {
    objects {
      current {
        user_key
      }
    }
  }
}
```
And modify the corresponding code that extract the data to strip the
extra `current` wrapper object layer.

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
