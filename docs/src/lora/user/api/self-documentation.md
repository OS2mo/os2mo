---
title: Self-documentation
---

# Self-documentation

The API serves some documentation for the services, objects and fields
it contains. The following urls are available:


``` {.http title="GET /site-map"}
    Returns a site map over all valid urls.

        Status Codes: • 200 OK - No error.
```

``` {.http title="GET /(service)/classes"}
    Returns a JSON representation of the hierarchy's classes and their fields

        Status Codes: • 200 OK - No error.
```

``` {.http title="GET /(service)/(object)/fields"}
    Returns a list of all fields a given object have.

        Status Codes: • 200 OK - No error.
```

``` {.http title="GET /(service)/(object)/schema"}
    Returns the JSON schema of an object.
        
        Status Codes: • 200 OK - No error.
```

``` {.http title="GET /version"}
    Returns the current version of LoRa

        Status Codes: • 200 OK - No error.
```

``` {.http title="GET /db/truncate"}
    Requires a configuration setting, in order to be enabled. 
    Truncates the database.

        Status Codes: • 200 OK - No error.
```

!!! warning
    The structure of each class is not completely analogous to the 
    structure of the input JSON as it uses the concept of *"overrides"*.
    This should also be fixed.
