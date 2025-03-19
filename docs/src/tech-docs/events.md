---
title: Events
---

Whenever a MO object is registered or goes into or out of effect, an AMQP
message is sent to the MO message broker. The purpose of the message broker is
to make it easier to build software that integrates with MO.


## Topic

Events are sent on a topic exchange, where the topic is the type of the MO
object, e.g. `engagement`. The valid topics are:

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


## Body

The body of the event contains the UUID of the affected object.


## Configuration

Events are currently **disabled by default**. To enable this, set `ENABLE_AMQP`
and deploy a MO container with command `mora.cli amqp start`.
