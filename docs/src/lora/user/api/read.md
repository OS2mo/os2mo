---
title: Read operation
---

# Read operation

``` http 
GET /(service)/(object)/(uuid)
```
The Read operation obtains an entire object as JSON.
    
Default is to return the object as it is currently seen but can
optionally be constrained by `virking*`
[valid time](../objects.md#valid-time) and/or `registrering*` 
[transaction time](../objects.md#transaction-time) to give an older view.

**Example request** for `GET /organisation/organisation/(uuid)`:
    ``` http
    GET /organisation/organisation/5729e3f9-2993-4492-a56f-0ef7efc83111 HTTP/1.1
    Accept: */*
    Host: example.com
    ```

    
**Example response** for :<http:get>:\`!GET
/organisation/organisation/(uuid)\`:

``` http
HTTP/1.0 200 OK
Content-Length: 744
Content-Type: application/json
Date: Tue, 15 Jan 2019 12:27:16 GMT
Server: Werkzeug/0.14.1 Python/3.5.2

{"5729e3f9-2993-4492-a56f-0ef7efc83111": [{
        "id": "5729e3f9-2993-4492-a56f-0ef7efc83111",
        "registreringer": [{
                "attributter": {
                    "organisationegenskaber": [{
                            "brugervendtnoegle": "magenta-aps",
                            "organisationsnavn": "Magenta ApS",
                            "virkning": {
                                "from": "2017-01-01 00:00:00+00",
                                "from_included": true,
                                "to": "2019-03-14 00:00:00+00",
                                "to_included": false
                            }}]},
                "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
                "fratidspunkt": {
                    "graenseindikator": true,
                    "tidsstempeldatotid": "2019-01-15T10:43:58.122764+00:00"
                },
                "livscykluskode": "Importeret",
                "tilstande": {
                    "organisationgyldighed": [{
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from": "2017-01-01 00:00:00+00",
                                "from_included": true,
                                "to": "2019-03-14 00:00:00+00",
                                "to_included": false
                            }}]},
                "tiltidspunkt": {
                    "tidsstempeldatotid": "infinity"
                }}]}]}
```

**Query Parameters:**

-  **registreretFra**(datetime) - [Transaction time](../objects.md#transaction-time)
'from' timestamp.

- **registreretTil**(datetime) - Transaction time 'to' timestamp.

- **registreringstid**(datetime) - Transaction time 'snapshot' timestamp.

- **virkningFra**(datetime) - [Valid time](../objects.md#valid-time) 'from' timestamp.

- **virkningTil**(datetime) - Valid time 'to' timestamp.

- **virkningstid**(datetime) - Valid time 'snapshot' timestamp.

- **konsolider**(bool) - Return consolidated 'virkning' periods - periods that are
represented by the smallest amount of 'virkning' objects.


All the `registeret*` and `virkning*` accept a value representing a
specific date and time. Input is accepted in almost any reasonable
format, including ISO 8601, SQL-compatible, traditional POSTGRES, and
others. The accepted values are the [Date/Time Input from
PostgreSQL](https://www.postgresql.org/docs/11.7/datatype-datetime.html#DATATYPE-DATETIME-INPUT).

**Response Headers:**

- [Content-Type](https://datatracker.ietf.org/doc/html/rfc7231#section-3.1.1.5) - `application/json`

**Status Codes:**

- [Status 200 OK](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.2.1) - No error.

- [400 Bad Request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1) - Malformed JSON or other bad request.

- [404 Not Found](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5) - No object of a given class with that UUID.

- [410 Gone](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.11) - The object has been [deleted](./delete.md).

The Read operation is known as the `Læs` operation in [the
specification](https://www.digitaliser.dk/resource/1567464/artefact/Generelleegenskaberforservicesp%c3%a5sags-ogdokumentomr%c3%a5det-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1763377).
