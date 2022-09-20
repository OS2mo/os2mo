---
title: Delete operation
---

# Delete operation

``` http
DELETE /(service)/(object)/(uuid)
```

The Delete operation deletes the object and return its UUID.

After an object is deleted, it cannot be retrieved by
[Read](./read.md),
[List](./list.md) and
[Search Operations](./search.md)
unless the `registreretTil` and/or `registreretFra` indicate a period where it did
exist.

The Delete operation deletes the whole object. To delete part of an
object see `DeleteAttr`{.interpreted-text role="ref"}.

**Example request** for `DELETE /organisation/organisationenhed/(uuid)`:

``` http
DELETE /organisation/organisationenhed/5fc97a7c-70df-4e97-82eb-64dc0a0f5746 HTTP/1.1
Host: example.com
```

**Example response** for `DELETE /organisation/organisationenhed/(uuid)`:

``` http
HTTP/1.0 202 ACCEPTED
Content-Length: 48
Content-Type: application/json
Date: Mon, 21 Jan 2019 16:47:00 GMT
Server: Werkzeug/0.14.1 Python/3.5.2

{
    "uuid": "5fc97a7c-70df-4e97-82eb-64dc0a0f5746"
}
```
**Status Codes:**

- [202 Accepted](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.3) - Object was deleted.

- [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) - Malformed JSON or other bad request.

- [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) - No object of a given class with that UUID.

The Delete operation is known as the `Slet` operation in [the
specification](https://www.digitaliser.dk/resource/1567464/artefact/Generelleegenskaberforservicesp%c3%a5sags-ogdokumentomr%c3%a5det-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1763377).
