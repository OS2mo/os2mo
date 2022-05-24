---
title: REST API
---

# REST API

This page will give you a overview of the REST API.

- [Self-documentation](./api/self-documentation.md)
- [API tutorial](./api/tutorial.md)

## Time zones

The default timezone for LoRa is UTC. When reading and writing data
without a timezone \-- whether it be in the object payloads or as query
parameters to the REST API \-- we interpret the given timestamps as UTC
time.

!!! Note
    We recommend that timezones be added explicitly to every timestamp when
    reading and writing data, to avoid inconsistencies regarding daylight
    savings time.


## Operations

- [Read](./api/read.md)
- [List](./api/list.md)
- [Search](./api/search.md)
    - [Paged search](./api/search.md#paged-search)
    - [Advanced search](./api/search.md#advanced-search)
    - [Searching on `Sag`-`JournalPost`-relations](./api/search.md#searching-on-sag-journalpost-relations)
- [Create](./api/create.md)
- [Update](./api/update.md)
    - [Merging logic](./api/update/merging.md)
    - [Deleting attributes, states and relations](./api/update/deleting.md)
- [Passivate](./api/passivate.md)
- [Delete](./api/delete.md)
- [Import](./api/import.md)

## `Document` etc.

`Document` and related objects have some special considerations.

- [File operations](./api/advanced/file-operations.md)
- [Deleting Dokument and Dokument Variant](./api/advanced/deleting-document.md)
