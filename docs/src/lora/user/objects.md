---
title: Objects
---

The database contains a large number of datatypes. To illustrate the
basic operations of the API we introduce a subset here. Specifically a
subset of `Organisation`.

The complete reference documentation for the fields can be found in
[Generelle egenskaber for services på sags- og
dokumentområdet](https://www.digitaliser.dk/resource/1567464/artefact/Generelleegenskaberforservicesp%c3%a5sags-ogdokumentomr%c3%a5det-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1763377)
with more info for those specifically for `Organisation` in :
[Specifikation af serviceinterface for
organisation](https://www.digitaliser.dk/resource/1569113/artefact/Specifikationafserviceinterfacefororganisation-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1569586).

::: {.note}
::: {.title}
Note
:::

As an example, the REST interface for Organisation is specified here:
<http://info.rammearkitektur.dk/index.php/LoRA_Organisationsservice>

Please note that in comparison with this official specification, our
system currently does not support the parameters `-miljø` and
`-version`.

As regards the parameter `-miljø` (which could be `-prod`, `-test`,
`-dev`, etc.) we have been trying to convince the customer that we do
not recommend running test, development and production on the same
systems, so we would prefer not to support that parameter.

As regards the parameter `-version`, we have deferred support for it
until we actually have more than one version of the protocol to support.
:::

Some `Organisation` objects
===========================

`organisation`
--------------

Located at the endpoint
:<http:get>:[!/organisation/organisation]{.title-ref}. An `organisation`
is a legal organisation. A good example of this a municipality.

``` {.json}
{
  "attributter": {
    "organisationegenskaber": [{
      "brugervendtnoegle": "magenta-aps",
      "organisationsnavn": "Magenta ApS",
      "virkning": {
        "from": "2017-01-01",
        "to": "2019-03-14"
      }
    }]
  },
  "tilstande": {
    "organisationgyldighed": [{
      "gyldighed": "Aktiv",
      "virkning": {
        "from": "2017-01-01",
        "to": "2019-03-14"
      }
    }
  ]}
}
```

The fields used in the example `organisation` are the following:

`organisationegenskaber→brugervendtnoegle`

:   An ID for the user. Semantically, this should be unique, but we
    don\'t enforce that. It is intended for the user to recognise the
    object. Required.

`organisationegenskaber→organisationsnavn`

:   The official name of the organisation.

`organisationegenskaber→virkning`

:   The period when the above attributes is valid. See
    `Valid time`{.interpreted-text role="ref"}. Required.

`organisationgyldighed→gyldighed`

:   Whether the organisation is active or not. Can take the values
    `Aktiv` and `Inaktiv`. Required.

`organisationgyldighed→virkning`

:   The period when the above `gyldighed` is valid. See
    `Valid time`{.interpreted-text role="ref"}. Required.

`organisationenhed`
-------------------

Located at the endpoint
:<http:get>:[!/organisation/organisationenhed]{.title-ref}. An
`organisationenhed` is an organisational unit. This could be a
department, section, office, committee, project group, class, team or
similar.

``` {.json}
```

The fields used in the example `organisationenhed` are the following:

`organisationenhedegenskaber→*` and `organisationenhedgyldighed→*`

:   Similar to `organisation`.

`relationer→tilhoerer`

:   This is the root `organisation` which the `organisationenhed` is
    part of. This is usally set on all `organisationenhed` to the single
    `organisation` in the mox instance.

`relationer→overordnet`

:   The parent `organisationenhed`.

Bitemporality
=============

The database is a [Bitemporal
Database](https://en.wikipedia.org/wiki/Temporal_database) with
`valid time<Valid
time>`{.interpreted-text role="ref"} and
`transaction time<transaction time>`{.interpreted-text role="ref"}.

Valid time {#Valid time}
----------

All attributes and relations have a valid time period associated as
`virkning`. It is the time period during which the fact is true in the
real world.

``` {.json}
```

The fields used in the example are the following:

`from`

:   The time when this fact starts to be true in the real world. Date
    and time input is accepted in almost any reasonable format,
    including ISO 8601. Required.

`from_included`

:   Whether the `from` timestamp is closed or open. Default `true`.

`to`

:   The time when this facts stop to be true in the real world. Date and
    time input is accepted in almost any reasonable format, including
    ISO 8601. Required.

`to_included`

:   Whether the `to` timestamp is closed or open. Default `false`.

Transaction time {#transaction time}
----------------

All transactions also have a transaction time as `registreret`. This
records the time period during which a given fact is stored in the
database. With the query parameters to a
`Read <ReadOperation>`{.interpreted-text role="ref"},
`List <ListOperation>`{.interpreted-text role="ref"} or
`SearchOperation`{.interpreted-text role="ref"} it can give you a view
of the state of the database at given time in the past or future.

Integrationdata
===============

The `integrationdata` field is different and its uniqueness is
documented here.

::: {.toctree maxdepth="1"}
objects/integrationdata.rst
:::
