<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# Creating Organisation Units

In order to create a new organisation unit, we use the [Organisation Unit Model][ramodels.mo.organisation_unit.organisationunit].
Suppose we already have the following organisation structure.

- Top Unit 1: `UUID=topunit1_uuid`
  - Unit A: `UUID=unita_uuid`
  - Unit B: `UUID=unitb_uuid` - Sub Unit 1: `UUID=subunit1_uuid`
- Top Unit 2: `UUID=topunit2_uuid`
  - Unit C: `UUID=unitc_uuid`
    - Sub Unit 2: `UUID=subunit2_uuid`
    - Sub Unit 3: `UUID=subunit3_uuid`
  - Unit D: `UUID=unitd_uuid`
  - Unit E: `UUID=unite_uuid`
    - Sub Unit 4: `UUID=subunit4_uuid`

We now wish to create Sub Unit 5 under Unit D. Thus, we need to know the `UUID` for Unit D, and the `UUID`s of the relevant organisation unit type and level klasses from LoRa. These can be obtained from the `service/f/org_unit_type/` and `service/f/org_unit_level/` endpoints, respectively.

A reply from `/service/f/org_unit_type/` could look like this

```json
{
  "uuid": "xxx",
  "user_key": "org_unit_type",
  "description": "",
  "data": {
    "total": 2,
    "offset": 0,
    "items": [
      {
        "uuid": "bu_uuid",
        "name": "Business Unit",
        "user_key": "Business Unit",
        "example": null,
        "scope": null,
        "owner": null
      },
      {
        "uuid": "cc_uuid",
        "name": "Cost Center",
        "user_key": "Cost Center",
        "example": null,
        "scope": null,
        "owner": null
      }
    ]
  }
}
```

and a reply from `/service/f/org_unit_level/` could look like this

```json
{
  "uuid": "yyy",
  "user_key": "org_unit_level",
  "description": "",
  "data": {
    "total": 2,
    "offset": 0,
    "items": [
      {
        "uuid": "l0_uuid",
        "name": "L0",
        "user_key": "L0",
        "example": null,
        "scope": null,
        "owner": null
      },
      {
        "uuid": "l1_uuid",
        "name": "L1",
        "user_key": "L1",
        "example": null,
        "scope": null,
        "owner": null
      }
    ]
  }
}
```

So, in order to create a new organisation unit valid from June 22, 2021 onwards with type `Business Unit` at level `L1` under Unit D, we need the following payload.

```json
{
  "type": "org_unit",
  "user_key": "Business Unit 225",
  "name": "New Org Unit",
  "parent": {
    "uuid": "unitd_uuid"
  },
  "org_unit_type": {
    "uuid": "bu_uuid"
  },
  "org_unit_level": {
    "uuid": "l1_uuid"
  },
  "validity": {
    "from": "2021-06-22T00:00:00+02:00",
    "to": null
  }
}
```

It is possible to achieve this via the Python model as well. This will automatically generate the UUID for the new organisation unit, in addition to performing validation of the values given to the model.

```python
from ramodels.mo import OrganisationUnit

new_ou = OrganisationUnit(
    user_key="Business Unit 225",
    name="New Org Unit",
    parent={"uuid": "unitd_uuid"},
    org_unit_type={"uuid": "bu_uuid"},
    org_unit_level={"uuid": "l1_uuid"},
    validity={"from": "2021-06-22"},
)
print(new_ou.json(by_alias=True, indent=2))
# >>>
# {
#   "uuid": "f4937c3b-1b88-4182-a77d-a57bafdce347",
#   "type": "org_unit",
#   "user_key": "Business Unit 225",
#   "validity": {
#     "from_date": "2021-06-22T00:00:00+02:00",
#     "to_date": null
#   },
#   "name": "New Org Unit",
#   "parent": {
#     "uuid": "unitd_uuid"
#   },
#   "org_unit_hierarchy": null,
#   "org_unit_type": {
#     "uuid": "bu_uuid"
#   },
#   "org_unit_level": {
#     "uuid": "l1_uuid"
#   }
# }
```

<sup><sub>**Note: in the above, the referenced UUIDs have to be actual UUIDs following the spec, otherwise validation fails.**</sub></sup>

The resulting payload can now be posted to `service/ou/create`.
