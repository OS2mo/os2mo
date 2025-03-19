---
title: Events
---

OS2mo has a powerful event system. Combined with the GraphQL API, this allows
you to build integrations between OS2mo and any other system where changes take
an almost immediate effect. Additionally, OS2mo's event system can be used by
integrations themselves to emit events.

The entire event system is exposed through [OS2mo's GraphQL
interface](./graphql/intro.md). GraphQL is self-documenting which means a lot
of the documentation can be found in the schema, for example by visiting
`/graphql` in a browser.


## Listeners and Events

The event system consists of _listeners_ and _events_. Integrations define what
events they want to receive by creating listeners.


### Listeners

A listener listens for events with a specific routing key in a namespace. Each
integration that emits events MUST use its own namespace. For instance, the
LDAP integration emits events in the namespace `"LDAP"`, but also listens for
events in the `"MO"` namespace.

Additionally, listeners have a `user_key` which allows integrations to create
multiple listeners for the same namespace/routing key combination.


### Events

An event represents that ✨ something ✨ might have happened. An event is
designated for a namespace and routing key and all matching listeners will
receive it. The routing key defines the type of the object of the event. For
instance, an OS2mo object could have the type "`engagement`".

Events have a subject and a priority.

The default priority is `10`, and most of the time there is no reason the
change that. A priority of `1` is for the highest priority events, such as
events requested by an end user action.

The subject is an identifier for of the object that might have changed.

All events MUST be acknowledged by the listening integration after they have
been processed.

Similar events are deduplicated.


## OS2mo events

Whenever an OS2mo object is registered or goes into or out of effect, an event
is emitted.

Events for native objects in OS2mo are always emitted in the `MO` namespace.

The routing key is always the type of the object.

When you are listening for OS2mo events, the subject is always the UUID of the
affected object.

OS2mo's routing keys are:

* `address`
* `association`
* `class`
* `engagement`
* `facet`
* `itsystem`
* `ituser`
* `kle`
* `leave`
* `manager`
* `org_unit`
* `owner`
* `person`
* `related_unit`
* `rolebinding`


## Getting started

### Setup

Your integration must create all its necessary listeners on startup. The
`event_listener_create` mutator is idempotent.

Here is the GraphQL query to create a listener:

```
mutation CreateListener {
  event_listener_create(
    input: {
      namespace: "MO"
      user_key: "engagement_listener_1"
      routing_key: "engagement"
    }
  ) {
    uuid
  }
}
```


### Fetching events

To get an event for processing, you MUST use the `event_fetch` query. You
MUST do this repeatedly, forever, for all your listeners.

```
query GetEvent($listener_uuid: UUID!) {
  event_fetch(filter: { listener: $listener_uuid }) {
    uuid
    subject
    token
  }
}

```

After successfully processing an event, you MUST acknowledge it. This is done
using the token from `event_fetch`:

```
mutation Ack($token: EventToken!) {
  event_acknowledge(input: $token)
}
```

If you do not receive an event, you SHOULD sleep to not cause excessive load on
OS2mo.


## Maintenance

These operations are not intended for programmatic use, but rather for
developers to debug and maintain the system.


### Inspection

You can inspect pending events using the `events` and `event_listeners`
collections in GraphQL.

Sometimes, events will show up even though they are not received in calls to
`event_fetch`. This is because OS2mo will wait a bit before retrying events
that go unacknowledged.


### Silencing & unsilencing

Events can be silenced and unsilenced with the `event_silence` and
`event_unsilence` mutators, respectively.

Integrations will never receive silenced events with `event_fetch`.

You are only expected to silence events temporarily. Integrations MUST be able
to handle all events - its fine to do nothing based on an event.

You should never acknowledge an event manually.


### Deleting listeners


## Monitoring

OS2mo exposes multiple metrics related to the event system at `/metrics`. It is
an expectation that all events should be processed by integrations and
acknowledged. Events should not be silenced for long.

Magenta will always monitor and alert on these metrics. Anyone is welcome to do
the same, but beware that we do not consider the exact metrics a stable
interface. As such, they may change in the future to improve monitoring and
keep the system healthy.
