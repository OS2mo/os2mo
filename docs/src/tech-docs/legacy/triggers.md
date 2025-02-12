---
title: Customization and Triggers
---

In order to keep customizations out of the main code base OS2mo makes
use of a 'customer' directory meant to be used as a mount point for
importing customer specific code into the os2mo runtime.

The intended way of customizing code is through the use of triggers.

A Trigger is a function decorated using `mora.triggers.Trigger.on`. This
decorator ensures that the decorated function is called on a certain
stage of the lifecycle of a certin kind of request for a certain role
type. There are currently two such stages:

> - `ON_BEFORE`: this is typically fired after the request\'s prepare
>   phase
> - `ON_AFTER`: this is typically fired after the request\'s commit
>   phase

Currently all Role Types (Organizational unit, Employee, Address to name
a few) and Request Types (Create, Edit, Terminate) can be decorated, so
it is possible to have functions triggered for example:

- After creating an organizational unit
- Before creating an employee
- After editing an address

## Triggers deployed in OS2mo

OS2mo itself uses triggers for internal purposes. They reside in
`mora.triggers.internal` module. See the `amqp_trigger.py` and
`http_trigger.py` for examples.

## Trigger configuration

Inclusion of Triggers in OS2mo are handled through a single
configuration value called `TRIGGER_MODULES` which is a list of fully
qualified names for trigger modules. The AMQP and HTTP Trigger modules
are loaded directly, and thus do not need to be in `TRIGGER_MODULES`.

In order to convey settings directly to triggers we suggest using the
fully qualified path as a prefix for configuration values which address
that trigger, for example:

lets say `TRIGGER_MODULES` is `["customer.triggers.andeby"]` and we want
to supply a `FACTOR` value to the `duck_function` inside that module, we
could specify it in the configuration like:

`customer.trigger.andeby.duck_function.FACTOR`

Trigger modules must have a function called register which does the
actual decoration of the trigger functions. It may also access the
supplied app\'s configuration to determine if specific triggers have
been disabled through the use of above mentioned prefixed configuration
values as well as obtain other configuration directly meant for the
trigger/module.

## The customer module

A directory placed on the host machine (outside the container / module
path) is mounted inside the container (when running in a container) and
a symlink called `customer` points to that directory.

In case of running os2mo directly on the host machine the symlink is
just pointed directly at the location of the customer directory on the
host machine

This directory will typically contain the contents of the
`os2mo-data-import-and-export` repository because some proposed triggers
share code with other integrations.

Once positioned this way triggers included from this module has access
to any and all code inside OS2mo\'s python environment as well as any
code inside the customer directory

## The Trigger function

A trigger function will receive only one argument, the trigger_dict,
which is a dictionary with information about the event

### ON_BEFORE

An `ON_BEFORE` trigger_dict will typically contain at least these
items: :

    {
        'event_type': EventType.ON_BEFORE,
        'request': {}, # the object that was received by the handler
        'request_type': RequestType.EDIT,
        'role_type': '' # role_type of the request
        'uuid': '' # the uuid of the object being edited

    }

### ON_AFTER

For an `ON_AFTER` trigger_dict an additional key is added - the result:
:

    {
        'event_type': EventType.ON_AFTER,
        'request': {}, # the object that was received by the handler
        'request_type': RequestType.EDIT,
        'result': '' # the result that is to be sent back to the client
        'role_type': '' # role_type of the request
        'uuid': '' # the uuid of the object being manipulated
    }

## Triggerless mode

It can be reasonable to turn off trigger-functionality when for example
loading a complete data-set into OS2mo. In case You want that, specify
the flag: `triggerless` in the request like:
`http://example.com?triggerless=1`

Using triggerless requests also disables amqp-messages.

<!-- ::: {.danger}
::: {.title}
Danger
::: -->

using `triggerless mode` is discouraged if you are not fully aware of
all implications. It is meant to be used solely for purposes like
initial data load or for integrations that prefer to do all heavy
lifting by themselves.
:::

## HTTP Trigger module

The HTTP Trigger module is loaded, but not enabled by default.

To enable the module add the following to MO's configuration:

    [triggers.http_trigger]
    enabled = true
    http_endpoints = [
        "endpoint_to_trigger:9037"
    ]

Then restart MO, on startup MO will now send a request to `/triggers` on
each of the configured endpoints.

The `/triggers` endpoint is expected to return JSON list of
`MOTriggerRegister` payloads. The JSON Schema for the
`MOTriggerRegister` can be generated with:

    pip install os2mo-http-trigger-protocol
    python3 -c "from os2mo_http_trigger_protocol import MOTriggerRegister; print(MOTriggerRegister.schema_json())"

An example of the return value is:

    [{
        "event_type": "ON_BEFORE",
        "request_type": "CREATE",
        "role_type": "org_unit",
        "url": "/triggers/ou/create",
        "timeout": 60,
    }]

Which instructs MO to send a HTTP POST request to `/triggers/ou/create`
before an organizational unit is created. The request will timeout after
`60` seconds, and expects a status-code `200` return if no issues were
encountered. If the request is answered with an erroneous status code,
it will block the creation in MO.

For an example implementation of a compliant endpoint receiver, please
see: \* <https://github.com/OS2mo/OS2mo-http-trigger-example>
