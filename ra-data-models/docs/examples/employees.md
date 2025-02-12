<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# Creating Employees

In order to create a new employee, we use the [Employee Model][ramodels.mo.employee.employee]. Per the model, it is very easy to create a new employee: simply post a JSON payload with given name and surname to `service/e/create`

```json
{
  "type": "employee",
  "givenname": "Name",
  "surname": "LastName"
}
```

Equivalent Employee model generation:

```python
new_empl = Employee(givenname="Name", surname="LastName")
print(new_empl.json(by_alias=True, indent=2))
# >>>
# {
#   "uuid": "12943aa8-9df7-4675-a688-32cc2c93457b",
#   "type": "employee",
#   "givenname": "Name",
#   "surname": "LastName",
#   "name": null,
#   "cpr_no": null,
#   "seniority": null,
#   "user_key": null,
#   "org": null,
#   "nickname_givenname": null,
#   "nickname_surname": null,
#   "nickname": null,
#   "details": null
# }
```

However, this employee will have no association to the organisation as a whole. Usually, it is of interest to specify [details](../mo/api.md#details) when creating a new employee.

For this example, suppose that we wish to create an employee that has an engagement as a Software Developer in Unit B and the initials EMPLO.

We need to create an [`Engagement`][ramodels.mo.details.engagement.engagement], and we can use the initials (if unique) as the employee's user key.
We need three klasses: the job function (i.e. Software Developer), the engagement type, and the primary type (denoting whether the engagement is primary, secondary, etc.). These can be looked up at the `service/f/engagement_job_function/`, `service/f/engagement_type/` and `service/f/primary_type/` endpoints, respectively.

Then, we can create a payload as follows.

```json
{
  "type": "engagement",
  "org_unit": {
    "uuid": "unitb_uuid"
  },
  "person": {
    "uuid": "emplo_uuid"
  },
  "user_key": "EMPLO",
  "job_function": {
    "uuid": "software_developer_uuid"
  },
  "engagement_type": {
    "uuid": "engagement_type_uuid"
  },
  "primary": {
    "uuid": "primary_type_uuid"
  },
  "validity": {
    "from": "2016-09-12",
    "to": "2019-12-04"
  }
}
```

This can then be posted to `service/e/create`.
In fact, we can include this payload directly in the Employee payload - if we do so, it is not necessary to specify the person reference:

```json
{
  "type": "employee",
  "givenname": "Name",
  "surname": "LastName",
  "details": [
    {
      "type": "engagement",
      "org_unit": {
        "uuid": "unitb_uuid"
      },
      "user_key": "EMPLO",
      "job_function": {
        "uuid": "software_developer_uuid"
      },
      "engagement_type": {
        "uuid": "engagement_type_uuid"
      },
      "primary": {
        "uuid": "primary_type_uuid"
      },
      "validity": {
        "from": "2016-09-12",
        "to": "2019-12-04"
      }
    }
  ]
}
```

The same logic can be applied for each detail type.
