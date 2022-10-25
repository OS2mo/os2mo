---
title: Creating, editing and listing "IT associations" using the service API
---

This document describes how to create, edit and list "IT associations" using the MO "service API".

In the service API, IT associations are exposed using the same REST endpoints as "normal" associations. To create, edit
or list IT associations, clients must use the same endpoints as they would use for normal associations - but with
different payload elements or query parameters.

In the examples below, `curl` is used to demonstrate endpoint URLs, query parameters and payloads. Every `curl`
invocation uses a `$BEARER` token on the form `Authorization: Bearer <token>`. It is assumed that the client invoking
`curl` has already retrieved such a bearer token, and that it is available in the shell variable `BEARER`.

## Creating an IT association

### Invocation:
```bash
curl -s 'http://localhost:5000/service/details/create' -X POST -H "Content-Type: application/json" -H "$BEARER" -d @create_it_association.json
```

where `create_it_association.json` contains:

```json
[
  {
    // Mandatory fields for all associations ("normal" as well as "IT" associations)
    "type": "association",
    "person": { "uuid": "dbdd8a8d-662b-4134-99a5-19247644b6aa" },           // UUID of an employee
    "org_unit": { "uuid": "6453b4d3-ced6-4f0c-9720-0353081c94be" },         // UUID of an organisational unit
    "org": { "uuid": "266a7532-40d2-8de3-cd0f-1a94de5ad1fb" },              // UUID of an organisation
    "primary": { "uuid": "84d8c1a2-63aa-9fcb-fef9-ad71d2145951" },          // Class UUID in "primary_type" facet
    "validity": { "from": "2022-10-25",  "to": null },                      // Validity period

    // Fields specific to IT associations
    "it": { "uuid": "a98103e8-08d1-489c-9b63-213f0861713b" },               // UUID of an "IT user" created beforehand
    "job_function": { "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e" }      // Class UUID specifying the job function
  }
]
```

### Response:

```json
["4617d0ff-2c0f-4f96-96cb-0e177fce3c79"]
```

The response contains a list of UUIDs of the IT associations created (in this example a single UUID.)

## Editing an IT association

### Invocation:
```bash
curl -s 'http://localhost:5001/service/details/edit' -X POST -H "Content-Type: application/json" -H "$BEARER" -d @edit_it_association.json
```

where `edit_it_association.json` contains:

```json
{
  // Mandatory fields for all associations
  "type": "association",
  "uuid": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",                           // UUID of the IT association to edit
  "data": {
    "person": { "uuid": "dbdd8a8d-662b-4134-99a5-19247644b6aa" },           // UUID of an employee
    "org_unit": { "uuid": "6453b4d3-ced6-4f0c-9720-0353081c94be" },         // UUID of an organisational unit
    "primary": { "uuid":"b871a5d2-e75b-596e-ee81-3e4e9609823c" }            // Class UUID in "primary_type" facet
    "validity": { "from": "2022-10-25", "to": null },                       // Validity period

    // Fields specific to IT associations
    "it": { "uuid": "a98103e8-08d1-489c-9b63-213f0861713b" },               // UUID of "IT user"
    "job_function": { "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e" }      // Class UUID specifying the job function
  }
}
```

### Response:

```json
"f9cf14ef-2151-4f8e-b1da-20437376bbe5"
```

The response contains the UUID of the edited IT association. Notice that the UUID is not contained in a list,

## List all IT associations of an employee

### Invocation:
```bash
curl -s 'http://localhost:5000/service/e/dbdd8a8d-662b-4134-99a5-19247644b6aa/details/association?validity=present&it=1' -H "$BEARER"
```

Notice the `it=1` query parameter, which specifies that the client is only interested in listing IT associations, and
not a mix of both normal associations and IT associations.

### Response:

The response contains a list of one or more IT associations. In the response example, some of the response elements have
been elided (`...`) to highlight the more interesting parts of the response.

```json
[
  {
    "uuid": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",                         // UUID of IT association
    "user_key": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",
    "validity": { "from": "2022-10-25", "to": null },
    "person": { ... },
    "org_unit": { ... },
    "association_type": null,                                               // Not defined for "IT associations"
    "primary": {                                                            // Indicates whether the *IT association*
      "uuid": "b871a5d2-e75b-596e-ee81-3e4e9609823c",                       // is primary or not.
      "name": "Ikke-primær",
      "user_key": "non-primary",
      ...
    },
    "substitute": null,                                                     // Not defined for "IT associations"
    "job_function": {                                                       // Contains data on the job function
      "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e",
      "name": "Afdelingsleder",
      "user_key": "Afdelingsleder",
      ...
    },
    "it": [                                                                 // Contains data on the "IT user"
      {
        "uuid": "a98103e8-08d1-489c-9b63-213f0861713b",
        "user_key": "fff",
        "validity": { "from": "2022-10-25",  "to": null },
        "itsystem": {
          "uuid": "10c2f705-e2bf-4f0e-ba27-2bb32c3d12d2",                   // UUID of the IT user's IT system
          "name": "Microsoft Active Directory",                             // "Long name" of the IT system
          "reference": null,
          "system_type": null,
          "user_key": "AD",                                                 // "Short name" of the IT system
          "validity": { "from": "1930-01-01",  "to": null }
        },
        "person": { ... },
        "org_unit": null,
        "primary": {                                                        // Indicates whether the *IT user* is
          "uuid": "84d8c1a2-63aa-9fcb-fef9-ad71d2145951",                   // primary or not.
          "name": "Primær",
          "user_key": "primary",
          ...
        }
      }
    ]
  }
]
```
