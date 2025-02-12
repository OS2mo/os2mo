---
title: Legacy AMQP Messages
---

!!! warning
This system is deprecated for [the new AMQP subsystem](../events.md).

When a MO object is created, modified or deleted, an AMQP message is
sent to the MO broker. The purpose of the message exchange is to make it
easier to build software that integrates with MO. If you are writing
such software, you are probably interested in the [Delayed
queue](#delayed-queue).

## Format

Messages are valid json with a `uuid` key and a `time` key. Here is an
example of a message body:

```json
{
  "uuid": "c390b9a2-7202-48e6-972b-ce36a90065c4",
  "time": "2019-03-24T13:02:15.132025"
}
```

Where `uuid` is the uuid of the affected `employee` or `org_unit` and
`time` is a ISO timestamp of when the change is effective.

## Topic

The exchange is a topic exchange and all messages are pushed with three
topics. Here is an example of a topic:

`employee.it.create`

The three topics can be described as:

1.  The service: `employee` or `org_unit`.
2.  Name of affected object type: `address`, `association`,
    `employee`, `engagement`, `it`, `leave`, `manager`, `org_unit`,
    `related_unit`, `role`.
3.  The action performed: `create`, `update` or `delete`.

Or put more abstractly:

> `<service>.<object-type>.<action>`

## Delayed queue

A separate project, the
[mo-delay-agent](https://gitlab.magenta.dk/lora/mo-delay-agent/),
maintains a queue for identical messages which are only sent once the
`time` field is due.

### Example

This is an example of a Python script that exhausts the queue:

```python
import pika

host = "localhost"
exchange = "moq"
topic = "#.#.#"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()

channel.exchange_declare(exchange=exchange, exchange_type="topic")
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

print(" [*] Waiting for messages. To exit press CTRL+C")

def callback(ch, method, properties, body):
    print(" [%s] %r" % (method.routing_key, body))

channel.basic_consume(callback, queue=queue_name, no_ack=True)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()
```

## Configuration

Messages are **disabled by default**.

To enable AMQP, set `ENABLE_AMQP` to `True`.

The default exchange, `os2mo`, can be configured by changing `AMQP__EXCHANGE`.

Host and port are set to `localhost:5672` and can be configured with
`AMQP__HOST` and `AMQP__PORT` respectively. Alternatively, `AMQP__URL` can be
used.
