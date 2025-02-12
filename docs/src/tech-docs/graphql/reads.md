# Tutorial: reading data

As touched upon briefly in the [introduction](intro.md#quickstart), reading data from a graph API is done through queries. In the following, several example queries in JSON format are presented and compared to the REST API queries needed to obtain the same result.

## Manager data

This example shows the difference between the service API and the graph API when obtaining manager data for organisation units.
Suppose you are interested in listing managers, manager types, and job functions for three different organisation units with UUIDs `uuid1`, `uuid2`, and `uuid3`, respectively.

In order to obtain this data using the service API, you would have to do the following.

1. Get manager details for the specified organisation unit.

```
GET https://example.com/mo/service/ou/uuid1/details/manager
```

2. Parse the result to obtain `employee_uuid` for the manager and the manager type
3. Get employee engagement details

```
GET https://example.com/mo/service/e/employee_uuid/details/engagement
```

4. Parse the results and merge them with results from step 2.
5. Repeat for the remaining organisation units

All in all, 6 requests would be made to MO for this relatively simple example, and we suffer from both over- and under-fetching. In other words, we both get much more data than we need when querying managers, and at the same time, not enough to satisfy our requirements: we have to send a separate request in order to obtain job function information.

In the graph API, however, you can do all this with a single query

```graphql
query Managers {
  org_units(filter: {uuids: ["uuid1", "uuid2", "uuid3"]}) {
    objects [
      name
      managers {
        manager_type {
          user_key
        }
        employee {
          name
          engagements {
            job_function {
              user_key
            }
          }
        }
      }
    ]
  }
}
```

which will output data similar to

```json
{
  "data": {
    "org_units": [
      {
        "objects": [
          {
            "name": "Organisation Unit 1",
            "managers": [
              {
                "manager_type": {
                  "user_key": "Director"
                },
                "employee": [
                  {
                    "name": "Fred Smith",
                    "engagements": [
                      {
                        "job_function": {
                          "user_key": "CEO"
                        }
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "objects": [
          {
            "name": "Organisation Unit 2",
            "managers": [
              {
                "manager_type": {
                  "user_key": "Team Lead"
                },
                "employee": [
                  {
                    "name": "Elsa Støcken Andersen",
                    "engagements": [
                      {
                        "job_function": {
                          "user_key": "Senior Software Developer"
                        }
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "objects": [
          {
            "name": "Organisation Unit 3",
            "managers": [
              {
                "manager_type": {
                  "user_key": "Regional Manager"
                },
                "employee": [
                  {
                    "name": "Anna Larsen",
                    "engagements": [
                      {
                        "job_function": {
                          "user_key": "HR Consultant"
                        }
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

As is evident, our query yields a list of exactly the data we have asked for - no more, no less. The only post-processing necessary in this case would be flattening. It will also outperform the service API approach since fewer calls to the database are made.
