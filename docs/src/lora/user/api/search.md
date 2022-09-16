---
title: Search operation
---

# Search operation

``` http 
GET /(service)/(object)
```

The Search operation returns a list of UUIDs of the objects that fit
the parameters. With the `list` parameter, you can fetch the objects
instead of a list of UUIDs.

!!! note
    `GET /(service)/(object)` can also be a
    [ListOperation](./list.md) depending on parameters.
    With only the `uuid`, `virking*` and `registeret*` parameters, it is a
    [ListOperation](./list.md) and will return one or
    more whole JSON objects. Given any other parameters the operation is a
    [SearchOperation](./search.md).

Default is to return the object(s) as currently seen but can
optionally be constrained by `virking*`
[valid time](../objects.md#valid-time) and/or
`registrering*` [transaction time](../objects.md#transaction-time) to give an older 
view.

**Search example request** for :<http:get>:\`!GET
/organisation/organisationenhed\`:

``` http
GET /organisation/organisationenhed?overordnet=66e8a55a-8c61-4d33-b244-574c09ef41f7 HTTP/1.1
Accept: */*
Host: example.com
```

**Search example response** for `GET /organisation/organisationenhed`:

``` http
HTTP/1.0 200 OK
Content-Length: 94
Content-Type: application/json
Date: Thu, 17 Jan 2019 15:02:39 GMT
Server: Werkzeug/0.14.1 Python/3.5.2

{"results": [[
    "74054d5b-54fc-4c9e-86ef-790fa6935afb",
    "ccfd6874-09f5-4dec-8d39-781f614bb8a7"
]]}
```

**Query Parameters:**

- **uuid** (*uuid*) - The UUID of the object to receive. Allowed once in 
[Search operation](./search.md). 

- **bvn** (*string brugerventnoegle* /) - Match text in the `brugervendtnoegle`-field. 

- **vilkaarligattr** (*string*) - Match text values of any `attributter`-field.

- **vilkaarligrel** (*uuid*) - Match values of any `relationer`. 

- **livscykluskode** (*enum*) - Matches the `livscykluskode`-field. Can be one of 
`Opstaaet`, `Importeret`, `Passiveret`, `Slettet` or `Rettet`.

- **brugerref** (*uuid*) - Match the `brugerref`-field. The (system) user who changed 
the object.

- **notestekst** (*string*) - Match the `notetekst`-field in `virkning`. (Not to be 
confused with the `note`-field.)

- **foersteresultat** (*int*) - The first result in a 
[Paged search](#paged-search). Sorts the result by `brugervendtnoegle`.

- **maximalantalresultater** (*int*) - The maximal number of results in a
[Paged search](#paged-search). Sorts the result by 
`brugervendtnoegle`.

- **list** (*bool*) - Fetch and return objects instead of just their uuids.

- **konsolider** (*bool*) - Return consolidated 'virkning' periods - periods that are
represented by the smallest amount of 'virkning' objects.

- **registreretFra** (datetime) - [Transaction time](../objects.md#transaction-time)
'from' timestamp.

- **registreretTil** (datetime) - Transaction time 'to' timestamp

- **registreringstid** (datetime) - Transaction time 'snapshot' timestamp.

- **virkningFra** (datetime) - [Valid time](../objects.md#valid-time) 'from' timestamp.

- **virkningTil** (datetime) - Valid time 'to' timestamp.

- **virkningstid** (datetime) - Valid time 'snapshot' timestamp.

All the `registeret*` and `virkning*` take a datetime. Input is
accepted in almost any reasonable format, including ISO 8601,
SQL-compatible, traditional POSTGRES, and others. The accepted values
are the [Date/Time Input from
PostgreSQL](https://www.postgresql.org/docs/11.7/datatype-datetime.html#DATATYPE-DATETIME-INPUT).

All *string* parameters match case insensitively. They support the
wildcard `%` (percent sign) to match zero or more characters.

If you want to match a litteral percentage-sign `%` you have to escape
it with backslash. E.g. `abc\%def` would match the value `abc%def`.

Contrary to typical SQL `LIKE` syntax, the character `_` (underscore)
matches only the underscore character (and not "any character").

!!! attention
    The URI should always be percent-encoded as defined in 
    [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986.html#section-2). Not 
    doing so can lead to unexpected results when you use the `%` wildcard.

    The percent-encoding of `%` is `%25`. E.g. a search query for a `bvn`
    with the string `abc%123` would look like `?bvn=abc%25123`.

    See [Wildcards](../../dev/wildcards.md) for an in depth
    explanation.


In addition to the above general query parameters, each object also
has specialized parameters based on its field. The endpoints
`GET /(service)/(object)/fields` lists the fields which can be used for parameters 
for a [Search operation](./search.md).

**Response Headers:**

- [Content-Type](https://datatracker.ietf.org/doc/html/rfc7231#section-3.1.1.5) - `application/json`

**Status Codes:**

- [Status 200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) - No error.

- [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) - Malformed JSON or other bad request.

- [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) - No object of a given class with that UUID.

- [410 Gone](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.11) - The object has been [deleted](./delete.md).

The Search operation is known as the `Søg` operation in [the
specification](https://www.digitaliser.dk/resource/1567464/artefact/Generelleegenskaberforservicesp%c3%a5sags-ogdokumentomr%c3%a5det-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1763377).

## Paged search

The search function supports paged searches by adding the parameters
`maximalantalresultater` (max number of results) and `foersteresultat`
(first result).

Since pagination only makes sense if the order of the results are
predictable the search will be sorted by `brugervendtnoegle` if
pagination is used.

!!! note
    If queries using pagination are becoming a performance bottleneck, you
    can try to optimise them by setting `enable_hashagg = False` and
    `enable_sort = False` in `postgres.conf`. This may decrease performance
    for other queries.


## Advanced search

It is possible to search for relations (links) as well by specifying the
value, which may be either an UUID or a URN. E.g., for finding all
instances of `organisationenhed` which belongs to `Direktion`:

``` http
GET /organisation/organisationenhed?tilknyttedeenheder=urn:Direktion HTTP/1.1
```

When searching on relations, one can limit the relation to a specific
object type by specifying a search parameter of the format:

``` http
&<relation:<objecttype>=<uuid|urn>
```

E.g. if you want to search on an `opgave` relation with
`"objekttype":"lederniveau"` you make a query like this:
`?opgave:lederniveau=5cc827ba-6939-4dee-85be-5c4ea7ffd76e`.

Note that the objecttype parameter is case-sensitive.

It is only possible to search on one `DokumentVariant` and `DokumentDel`
at a time. For example, if :

``` http
&deltekst=a&underredigeringaf=<UUID>
```

is specified, then the search will return documents which have a
`DokumentDel` with `deltekst="a"` and which has the relation
`underredigeringaf=<UUID>`. However, if the deltekst parameter is
omitted, e.g. :

``` http
&underredigeringaf=<UUID>
```

Then, all documents which have at least one `DokumentDel` which has the
given UUID will be returned.

The same logic applies to the `varianttekst` parameter. If it is not
specified, then all variants are searched across. Note that when
`varianttekst` is specified, then any `DokumentDel` parameters apply
only to that specific variant. If the `DokumentDel` parameters are
matched under a different variant, then they are not included in the
results.

## Searching on `Sag`-`JournalPost`-relations

To search on the sub-fields of the `JournalPost` relation in `Sag`,
requires a special dot-notation syntax, due to possible ambiguity with
other search parameters (for example, the `titel` parameter).

The following are some examples:

```
&journalpostkode=vedlagtdokument
&journalnotat.titel=Kommentarer
&journalnotat.notat=Læg+mærke+til
&journalnotat.format=internt
&journaldokument.dokumenttitel=Rapport+XYZ
&journaldokument.offentlighedundtaget.alternativtitel=Fortroligt
&journaldokument.offentlighedundtaget.hjemmel=nej
```

All of these parameters support wildcards (`%`) and use case-insensitive
matching, except `journalpostkode`, which is treated as-is.

Note that when these parameters are combined, it is not required that
the matches occur on the *same* `JournalPost` relation.

For example, the following query would match any `Sag` which has one or
more `JournalPost` relations which has a
`journalpostkode = "vedlagtdokument"` AND which has one or more
`JournalPost` relations which has a
`journaldokument.dokumenttitel = "Rapport XYZ"` :

```
&journalpostkode=vedlagtdokument&journaldokument.dokumenttitel=Rapport+XYZ
```