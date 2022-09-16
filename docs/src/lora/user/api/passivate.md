---
title: Passivate operation
---

# Passivate operation

``` http
PATCH /(service)/(object)/(uuid)
```

The Passivate operation is a special
[Update operation](./update.md) with a JSON payload
containing `livscyklus: "Passiv"`. When an object is passive, it is no
longer maintained and may not be updated. The object will afterwards
not show up in searches and listings. The operation returns the UUID
of the object.

The payload may contain an optional `note` field.

**Example request** for `PATCH /organisation/organisationenhed/(uuid)`:

``` http
PATCH /organisation/organisationenhed/862bb783-696d-4345-9f63-cb72ad1736a3 HTTP/1.1
Content-Type: application/json
Host: example.com

{
  "note": "Passivate this object!",
  "livscyklus": "Passiv"
}
```

**Example response** for `PATCH /organisation/organisationenhed/(uuid)`:

``` http
HTTP/1.0 200 OK
Content-Length: 48
Content-Type: application/json
Date: Mon, 21 Jan 2019 12:40:36 GMT
Server: Werkzeug/0.14.1 Python/3.5.2

{
    "uuid": "862bb783-696d-4345-9f63-cb72ad1736a3 HTTP/1.1"
}
```

**Response Headers:**

- [Content-Type](https://datatracker.ietf.org/doc/html/rfc7231#section-3.1.1.5) - `application/json`

**Status Codes:**

- [Status 200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) - No error.

- [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) - Malformed JSON or other bad request.

- [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) - No object of a given class with that UUID.

The Passivate operation is known as the `Passiver` operation in [the
specification](https://www.digitaliser.dk/resource/1567464/artefact/Generelleegenskaberforservicesp%c3%a5sags-ogdokumentomr%c3%a5det-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1763377).
