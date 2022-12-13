---
title: Creating, editing and listing "IT associations" using the service API
---

This document describes how to create, edit, list and terminate "IT associations" using the MO "service API". It also
describes how to terminate "IT users". And finally, it gives an example on how to find "IT associations" for a given
person, using the "autocomplete" endpoint in the "service API."

In the service API, IT associations are exposed using the same REST endpoints as "normal" associations. To create, edit,
terminate or list IT associations, clients must use the same endpoints as they would use for normal associations - but
with different payload elements or query parameters.

In the examples below, `curl` and PowerShell are used to demonstrate endpoint URLs, query parameters and payloads.
Every `curl` and PowerShell invocation uses a `$BEARER` token on the form `Authorization: Bearer <token>`.
It is assumed that the client has already retrieved such a bearer token, and that it is available in the shell variable
`BEARER`.

The JSON payload is expected to be encoded using UTF-8 encoding.

Calling the service API using `curl` follows a general pattern:
```bash
curl -s \
  'http://localhost:5000/service/<endpoint>' \
  -X <method> \
  -H "Content-Type: application/json;charset=utf-8" \
  -H "$BEARER"
  -d @payload.json
```
Alternatively, the service API can also be invoked using PowerShell, using this general pattern:
```pwsh
(Invoke-Webrequest http://localhost:5000/service/<endpoint> `
    -Body '<JSON payload>' `
    -Method '<method>'
    -ContentType 'application/json;charset=utf-8' `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```

## Creating an IT association

### Invocation:
```bash
curl -s \
  'http://localhost:5000/service/details/create' \
  -X POST \
  -H "Content-Type: application/json;charset=utf-8" \
  -H "$BEARER" \
  -d @payload.json
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/details/create `
    -Body '<JSON payload>' `
    -Method 'POST'
    -ContentType 'application/json;charset=utf-8' `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where the JSON payload contains:
```json
[
  {
    // 1. Mandatory fields for all associations ("normal" as well as "IT" associations)
    // MO detail type
    "type": "association",
    // UUID of an employee
    "person": { "uuid": "dbdd8a8d-662b-4134-99a5-19247644b6aa" },
    // UUID of an organisational unit
    "org_unit": { "uuid": "6453b4d3-ced6-4f0c-9720-0353081c94be" },
    // UUID of an organisation
    "org": { "uuid": "266a7532-40d2-8de3-cd0f-1a94de5ad1fb" },
    // Class UUID in "primary_type" facet
    "primary": { "uuid": "84d8c1a2-63aa-9fcb-fef9-ad71d2145951" },
    // Validity period
    "validity": { "from": "2022-10-25",  "to": null },

    // 2. Fields specific to IT associations
    // UUID of an "IT user" created beforehand
    "it": { "uuid": "a98103e8-08d1-489c-9b63-213f0861713b" },
    // Class UUID specifying the job function
    "job_function": { "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e" }
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
curl -s \
  'http://localhost:5000/service/details/edit' \
  -X POST \
  -H "Content-Type: application/json;charset=utf-8" \
  -H "$BEARER" \
  -d @payload.json
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/details/edit `
    -Body '<JSON payload>' `
    -Method 'POST'
    -ContentType 'application/json;charset=utf-8' `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where the JSON payload contains:
```json
{
  // 1. Mandatory fields for all associations
  // MO detail type
  "type": "association",
  // UUID of the IT association to edit
  "uuid": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",
  "data": {
    // UUID of an employee
    "person": { "uuid": "dbdd8a8d-662b-4134-99a5-19247644b6aa" },
    // UUID of an employee
    "org_unit": { "uuid": "6453b4d3-ced6-4f0c-9720-0353081c94be" },
    // Class UUID in "primary_type" facet
    "primary": { "uuid":"b871a5d2-e75b-596e-ee81-3e4e9609823c" },
    // Validity period
    "validity": { "from": "2022-10-25", "to": null },

    // 2. Fields specific to IT associations
    // UUID of "IT user"
    "it": { "uuid": "a98103e8-08d1-489c-9b63-213f0861713b" },
    // Class UUID specifying the job function
    "job_function": { "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e" }
  }
}
```

### Response:

```json
"f9cf14ef-2151-4f8e-b1da-20437376bbe5"
```
The response contains the UUID of the edited IT association. Notice that the UUID is not contained in a list,

## Listing all IT associations of an employee

### Invocation:
```bash
curl -s \
  'http://localhost:5000/service/e/dbdd8a8d-662b-4134-99a5-19247644b6aa/details/association?validity=present&it=1' \
  -H "$BEARER"
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/e/dbdd8a8d-662b-4134-99a5-19247644b6aa/details/association?validity=present&it=1 `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
The URL is an example - the UUID `dbdd8a8d-662b-4134-99a5-19247644b6aa` identifies an employee in the MO database, and
can be replaced with any other valid employee UUID.

Notice the `it=1` query parameter, which specifies that the client is only interested in listing IT associations, and
not a mix of both normal associations and IT associations.

### Response:

The response contains a list of one or more IT associations:

```json
[
  {
    // UUID of IT association
    "uuid": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",

    "user_key": "f9cf14ef-2151-4f8e-b1da-20437376bbe5",
    "validity": { "from": "2022-10-25", "to": null },

    "person": {
      "givenname": "Fornavn",
      "surname": "Efternavn",
      "name": "Fornavn Efternavn",
      "nickname_givenname": "",
      "nickname_surname": "",
      "nickname": "",
      "uuid": "4c3d9879-203e-52ec-b01c-74feba99816e",
      "seniority": null
    },
    "org_unit": {
      "name": "Afdeling 22",
      "user_key": "70000",
      "uuid": "047c4271-6750-47be-bd04-bf43f48c13cb",
      "validity": {
        "from": "2005-12-01",
        "to": null
      }
    },

    // Indicates whether the *IT association* is primary or not
    "primary": {
      "uuid": "b871a5d2-e75b-596e-ee81-3e4e9609823c",
      "name": "Ikke-primær",
      "user_key": "non-primary",
      "example": null,
      "scope": "3000",
      "owner": null,
      "full_name": "Primær",
      "top_level_facet": {
        "uuid": "d5c1a8a9-f45b-4f5d-9462-49ed756563b9",
        "user_key": "primary_type",
        "description": ""
      },
      "facet": {
        "uuid": "d5c1a8a9-f45b-4f5d-9462-49ed756563b9",
        "user_key": "primary_type",
        "description": ""
      }
    },

    // Contains data on the job function
    "job_function": {
      "uuid": "6c28d2e5-6885-411a-9a90-df8c5204dc9e",
      "name": "Afdelingsleder",
      "user_key": "Afdelingsleder", "example": null,
      "scope": "TEXT",
      "owner": null
    },

    // Contains data on the "IT user"
    "it": [
      {
        "uuid": "a98103e8-08d1-489c-9b63-213f0861713b",
        "user_key": "fff",
        "validity": {
          "from": "2022-10-25",
          "to": null
        },
        "itsystem": {
          // UUID of the IT user's IT system
          "uuid": "10c2f705-e2bf-4f0e-ba27-2bb32c3d12d2",
          // "Long name" of the IT system
          "name": "Microsoft Active Directory",
          "reference": null,
          "system_type": null,
          // "Short name" of the IT system
          "user_key": "AD",
          "validity": {
            "from": "1930-01-01",
            "to": null
          }
        },
        "person": {
          "givenname": "Fornavn",
          "surname": "Efternavn",
          "name": "Fornavn Efternavn",
          "nickname_givenname": "",
          "nickname_surname": "",
          "nickname": "",
          "uuid": "4c3d9879-203e-52ec-b01c-74feba99816e",
          "seniority": null
        },
        "org_unit": null,
        // Indicates whether the *IT user* is primary or not.
        "primary": {
          "uuid": "84d8c1a2-63aa-9fcb-fef9-ad71d2145951",
          "name": "Primær",
          "user_key": "primary",
          "example": null,
          "scope": "3000",
          "owner": null,
          "full_name": "Primær",
          "top_level_facet": {
            "uuid": "d5c1a8a9-f45b-4f5d-9462-49ed756563b9",
            "user_key": "primary_type",
            "description": ""
          },
          "facet": {
            "uuid": "d5c1a8a9-f45b-4f5d-9462-49ed756563b9",
            "user_key": "primary_type",
            "description": ""
          }
        }
      }
    ],

    // Not defined for "IT associations"
    "association_type": null,

    // Not defined for "IT associations"
    "substitute": null,

    // Not defined for "IT associations"
    "dynamic_classes": []
  }
]
```

## Terminating an "IT user"

### Invocation:
```bash
curl -s \
  'http://localhost:5000/service/details/terminate' \
  -X POST \
  -H "Content-Type: application/json;charset=utf-8" \
  -H "$BEARER" -d @payload.json
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/details/terminate `
    -Body '<JSON payload>' `
    -Method 'POST'
    -ContentType 'application/json;charset=utf-8' `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where the JSON payload contains:
```json
{
  // MO detail type
  "type": "it",
  // UUID of IT user
  "uuid": "51d55263-294e-499d-9693-e0e3f086f3b8",
  // Termination date
  "validity": {"to": "2022-12-31"}
}
```

## Terminating an "IT association"

### Invocation:
```bash
curl -s \
  'http://localhost:5000/service/details/terminate' \
  -X POST \
  -H "Content-Type: application/json;charset=utf-8" \
  -H "$BEARER" -d @payload.json
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/details/terminate `
    -Body '<JSON payload>' `
    -Method 'POST'
    -ContentType 'application/json;charset=utf-8' `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where the JSON payload contains:
```json
{
  // MO detail type
  "type": "association",
  // UUID of IT association
  "uuid": "45f8004a-c815-4f43-8815-f9b12232e65b",
  // Termination date
  "validity": {"to": "2022-12-31"}
}
```

## Terminating "IT associations" and "IT users" belonging to a given username

As seen above, terminating an "IT user" or an "IT association" requires the UUID of the "IT user" or "IT association".
But if we only know the username in a given IT system (e.g., Active Directory), how can we find the relevant UUID?

1. We can use the "autocomplete" endpoint in the "service API" to search by username, which will give us the relevant
*employee UUID*.
2. Once we have the employee UUID, we can make another API request to retrieve the "IT users" and/or "IT
associations" of the employee. This will give us the UUID of the "IT association" or "IT user".
3. When we have the "IT user" or "IT association", we can use this to make our termination API request.

### 1. Finding the employee UUID
```bash
curl -s \
  'http://localhost:5000/service/e/autocomplete/?query=abc123' \
  -H "$BEARER"
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/e/autocomplete/?query=abc123 `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where `abc123` is the username we are searching for.

If there are any matches, this produces a response on the form:
```json
{
  "items": [
    {
      // Employee UUID
      "uuid": "696310fe-54f6-8408-45d0-aed4bf0e53a6"
    }
  ]
}
```

### 2. Finding all IT users or IT associations for a given employee UUID:

#### a. IT users
```bash
curl -s \
  'http://localhost:5000/service/e/696310fe-54f6-8408-45d0-aed4bf0e53a6/details/it' \
  -H "$BEARER"
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/e/696310fe-54f6-8408-45d0-aed4bf0e53a6/details/it `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where `696310fe-54f6-8408-45d0-aed4bf0e53a6` is the employee UUID found in step 1.

#### b. IT associations
```bash
curl -s \
  'http://localhost:5000/service/e/696310fe-54f6-8408-45d0-aed4bf0e53a6/details/association?it=1' \
  -H "$BEARER"
```
or
```pwsh
(Invoke-Webrequest http://localhost:5000/service/e/696310fe-54f6-8408-45d0-aed4bf0e53a6/details/association?it=1 `
    -Headers @{Authorization="Bearer $BEARER"}
).Content
```
where `696310fe-54f6-8408-45d0-aed4bf0e53a6` is the employee UUID found in step 1.

### 3. Terminating the "IT user" or "IT associations"

The API requests in step 2a and 2b both produce a list of zero or more items. Each item in this list has an `uuid` key
containing the UUID of an "IT user" or an "IT association". This can be used to call the "terminate" API, as described
above.
