---
title: Events
---

OS2mo has a powerful event system. Combined with the GraphQL API, this allows
you to build integrations between OS2mo and any other system where changes take
an almost immediate effect. Additionally, OS2mo's event system can be used by
integrations themselves to emit events.

Integrations define what events they want to receive.

Each event has a namespace, routing key and subject. The namespace is used to
allow different integrations to emit events with overlapping routing keys. The
routing key defines the type of object of the event. For instance, an OS2mo
object could have the type "`engagement`". Lastly, the subject is an identifier
of the affected object.

TODO? docs for recommended integration architectures.

The details of the event system is documented in GraphQL.



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
`event_listener_create` mutator is idempotent. The `user_key` can be used to
create multiple listeners for the same namespace/routing key combination.

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

To get an event, you can use the following query. You should do this
repeatedly, forever, for all your listeners.

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
