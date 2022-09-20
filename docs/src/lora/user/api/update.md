---
title: Update operation
---

# Update operation

``` http
PATCH /(service)/(object)/(uuid)
```

The Update operation applies the JSON payload as a change to the
object. Returns the UUID of the object.

How the changes are applied are described in the following pages. For
the logic of merging see [Merging logic](./update/merging.md).
To delete part of an object see [Deleting attributes, states and relations](./update/deleting.md#example-of-deleting-attributes).

The data can be supplied directly in the request if [Content-Type](https://datatracker.ietf.org/doc/html/rfc7231#section-3.1.1.5): `application/json` is set.

Alternatively the the data can be supplied as form data in the
`json`-field with [Content-Type](https://datatracker.ietf.org/doc/html/rfc7231#section-3.1.1.5): `multipart/form-data`. This allows seperate file form data.

## Advanced Update

- [Merging logic](./update/merging.md)
    - [Exceptions to this rule](./update/merging.md#exceptions-to-this-rule)
    - [Example of updating attributes](./update/merging.md#example-of-updating-attributes)
    - [Example of updating states](./update/merging.md#example-of-updating-states)
    - [Example of updating relations](./update/merging.md#example-of-updating-relations)
        - [Relations of type `Sag`, `Indsats`, `Tilstand` and `Aktivitet`](./update/merging.md#relations-of-type-sag-indsats-tilstand-and-aktivitet)
- [Deleting attributes, states and relations](./update/deleting.md)
    - [Example of deleting attributes](./update/deleting.md#example-of-deleting-attributes)
    - [Example of deleting states](./update/deleting.md#example-of-deleting-states)
    - [Example of deleting relations](./update/deleting.md#example-of-deleting-relations)
