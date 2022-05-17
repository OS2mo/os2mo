---
title: Search operation
---

Paged search {#PagedSearchOperation}
============

The search function supports paged searches by adding the parameters
`maximalantalresultater` (max number of results) and `foersteresultat`
(first result).

Since pagination only makes sense if the order of the results are
predictable the search will be sorted by `brugervendtnoegle` if
pagination is used.

::: {.note}
::: {.title}
Note
:::

If queries using pagination are becoming a performance bottleneck, you
can try to optimise them by setting `enable_hashagg = False` and
`enable_sort = False` in `postgres.conf`. This may decrease performance
for other queries.
:::

Advanced search
===============

It is possible to search for relations (links) as well by specifying the
value, which may be either an UUID or a URN. E.g., for finding all
instances of `organisationenhed` which belongs to `Direktion`:

``` {.http}
GET /organisation/organisationenhed?tilknyttedeenheder=urn:Direktion HTTP/1.1
```

When searching on relations, one can limit the relation to a specific
object type by specifying a search parameter of the format:

    &<relation>:<objecttype>=<uuid|urn>

E.g. if you want to search on an `opgave` relation with
`"objekttype":"lederniveau"` you make a query like this:
`?opgave:lederniveau=5cc827ba-6939-4dee-85be-5c4ea7ffd76e`.

Note that the objecttype parameter is case-sensitive.

It is only possible to search on one `DokumentVariant` and `DokumentDel`
at a time. For example, if :

    &deltekst=a&underredigeringaf=<UUID>

is specified, then the search will return documents which have a
`DokumentDel` with `deltekst="a"` and which has the relation
`underredigeringaf=<UUID>`. However, if the deltekst parameter is
omitted, e.g. :

    &underredigeringaf=<UUID>

Then, all documents which have at least one `DokumentDel` which has the
given UUID will be returned.

The same logic applies to the `varianttekst` parameter. If it is not
specified, then all variants are searched across. Note that when
`varianttekst` is specified, then any `DokumentDel` parameters apply
only to that specific variant. If the `DokumentDel` parameters are
matched under a different variant, then they are not included in the
results.

Searching on `Sag`-`JournalPost`-relations
==========================================

To search on the sub-fields of the `JournalPost` relation in `Sag`,
requires a special dot-notation syntax, due to possible ambiguity with
other search parameters (for example, the `titel` parameter).

The following are some examples:

    &journalpostkode=vedlagtdokument
    &journalnotat.titel=Kommentarer
    &journalnotat.notat=Læg+mærke+til
    &journalnotat.format=internt
    &journaldokument.dokumenttitel=Rapport+XYZ
    &journaldokument.offentlighedundtaget.alternativtitel=Fortroligt
    &journaldokument.offentlighedundtaget.hjemmel=nej

All of these parameters support wildcards (`%`) and use case-insensitive
matching, except `journalpostkode`, which is treated as-is.

Note that when these parameters are combined, it is not required that
the matches occur on the *same* `JournalPost` relation.

For example, the following query would match any `Sag` which has one or
more `JournalPost` relations which has a
`journalpostkode = "vedlagtdokument"` AND which has one or more
`JournalPost` relations which has a
`journaldokument.dokumenttitel = "Rapport XYZ"` :

    &journalpostkode=vedlagtdokument&journaldokument.dokumenttitel=Rapport+XYZ
