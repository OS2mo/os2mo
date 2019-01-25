.. automodule:: mora.service.address

Addresses
---------
.. _address:

Within the context of MO, we have two forms of addresses, `DAR`_ and
everything else. **DAR** is short for *Danmarks Adresseregister* or
the *Address Register of Denmark*, and constitutes a UUID representing a
DAWA address or access address. We represent other addresses merely
through their textual value.

.. tip::

  See also the `official documentation
  <http://dawa.aws.dk/dok/adresser>`_ — in Danish — on DAR addresses.

Before writing a DAR address, a UI or client should convert the
address string to a UUID using either their API or the
:http:get:`/service/o/(uuid:orgid)/address_autocomplete/` endpoint.

Each installation supports different types of addresses. To obtain
that list, query the :http:get:`/service/o/(uuid:orgid)/f/(facet)/`
endpoint::

   $ curl http://$SERVER_NAME:5000/service/o/$ORGID/f/employee_address_type

An example result:

.. sourcecode:: json

  {
    "data": {
      "items": [
        {
          "example": "20304060",
          "name": "Telefonnummer",
          "scope": "PHONE",
          "user_key": "Telefon",
          "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
        },
        {
          "example": "<UUID>",
          "name": "Adresse",
          "scope": "DAR",
          "user_key": "Adresse",
          "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
        },
        {
          "example": "test@example.com",
          "name": "Emailadresse",
          "scope": "EMAIL",
          "user_key": "Email",
          "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
        },
        {
          "example": "5712345000014",
          "name": "EAN",
          "scope": "EAN",
          "user_key": "EAN",
          "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
        }
      ],
      "offset": 0,
      "total": 4
    },
    "name": "employee_address_type",
    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/employee_address_type/",
    "user_key": "Medarbejderadressetype",
    "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1"
  }

The following scopes are available:

DAR
      UUID of a `DAR`_ address, as found through the API. Please
      note that this requires performing separate calls to convert
      this value to and from human-readable strings.

EMAIL
      An email address, as specified by :rfc:`5322#section-3.4`.

PHONE
      A phone number.

WWW
      An HTTP or HTTPS URL, as specified by :rfc:`1738`.

EAN
      Number for identification for accounting purposes.

PNUMBER
      A production unit number, as registered with the Danish CVR.


Reading
^^^^^^^

An example of reading addresses:

.. sourcecode:: json

  [
    {
      "address_type": {
        "example": "test@example.com",
        "name": "Email",
        "scope": "EMAIL",
        "user_key": "Email",
        "uuid": "10d315c3-34ef-4fca-b750-ec748fdd89f6"
      },
      "href": "mailto:test@test.dk",
      "name": "test@test.dk",
      "org_unit": {
        "name": "Hjørring",
        "user_key": "Hjørring 6305b76d-1b21-4cce-b9c4-4348b7c0c226",
        "uuid": "97337de5-6096-41f9-921e-5bed7a140d85",
        "validity": {
          "from": "1960-01-01",
          "to": null
        }
      },
      "person": null,
      "uuid": "03665c9e-fe04-409e-9f26-c7ebd051509b",
      "validity": {
        "from": "2019-01-01",
        "to": null
      },
      "value": "test@test.dk"
    },
    {
      "address_type": {
        "example": "20304060",
        "name": "Tlf",
        "scope": "PHONE",
        "user_key": "Telefon",
        "uuid": "055760a6-93b5-4b9b-b638-7d1b5bc6a4df"
      },
      "href": "tel:+4512341234",
      "name": "+4512341234",
      "org_unit": {
        "name": "Hjørring",
        "user_key": "Hjørring 6305b76d-1b21-4cce-b9c4-4348b7c0c226",
        "uuid": "97337de5-6096-41f9-921e-5bed7a140d85",
        "validity": {
          "from": "1960-01-01",
          "to": null
        }
      },
      "person": null,
      "uuid": "edd01c1a-ec14-4b90-947f-f6aa920bb01c",
      "validity": {
        "from": "2019-01-01",
        "to": null
      },
      "value": "12341234"
    },
    {
      "address_type": {
        "example": "<UUID>",
        "name": "Adresse",
        "scope": "DAR",
        "user_key": "AdressePost",
        "uuid": "580bc233-581a-45fa-bc94-f2b46075ae8e"
      },
      "href": "https://www.openstreetmap.org/?mlon=9.98710223&mlat=57.47802232&zoom=16",
      "name": "Enebærvej 1, 9800 Hjørring",
      "org_unit": {
        "name": "Hjørring",
        "user_key": "Hjørring 6305b76d-1b21-4cce-b9c4-4348b7c0c226",
        "uuid": "97337de5-6096-41f9-921e-5bed7a140d85",
        "validity": {
          "from": "1960-01-01",
          "to": null
        }
      },
      "person": null,
      "uuid": "f16c851c-012e-4b46-b916-c843486f85b5",
      "validity": {
        "from": "2019-01-01",
        "to": null
      },
      "value": "0a3f509a-6970-32b8-e044-0003ba298018"
    }
  ]


* ``name`` is a human-readable value for displaying the address
* ``href`` should be used as a hyperlink target, if applicable
* ``value`` is used for uniquely representing the address value for editing, which is detailed below.
* ``validity`` is a validity object.
* ``address_type`` is an address type object, equal to one of the types from one of the facet endpoints detailed above.

Writing
^^^^^^^

An example of objects for writing addresses:

.. sourcecode:: json

  [
    {
      "type": "address",
      "value": "0a3f509a-6970-32b8-e044-0003ba298018",
      "org": {
        "name": "Hjørring",
        "user_key": "Hjørring",
        "uuid": "293089ba-a1d7-4fff-a9d0-79bd8bab4e5b"
      },
      "address_type": {
        "example": "<UUID>",
        "name": "Adresse",
        "scope": "DAR",
        "user_key": "AdressePost",
        "uuid": "580bc233-581a-45fa-bc94-f2b46075ae8e"
      },
      "validity": {
        "from": "2019-01-01",
        "to": null
      },
      "org_unit": {
        "uuid": "97337de5-6096-41f9-921e-5bed7a140d85"
      }
    },
    {
      "type": "address",
      "value": "12341234",
      "org": {
        "name": "Hjørring",
        "user_key": "Hjørring",
        "uuid": "293089ba-a1d7-4fff-a9d0-79bd8bab4e5b"
      },
      "address_type": {
        "example": "20304060",
        "name": "Tlf",
        "scope": "PHONE",
        "user_key": "Telefon",
        "uuid": "055760a6-93b5-4b9b-b638-7d1b5bc6a4df"
      },
      "validity": {
        "from": "2019-01-01",
        "to": null
      },
      "org_unit": {
        "uuid": "97337de5-6096-41f9-921e-5bed7a140d85"
      }
    }
  ]

* ``value`` is the value of the address, or a UUID in the case of a DAR address.
  The backend takes care of processing and formatting the value correctly.
* ``address_type`` is an address type object, equal to one of the types from
  the facet endpoint detailed above.
* ``validity`` is a validity object.
* ``org`` is the organisation associated with the address.
* ``org_unit`` is the organisational unit associated to the address.
* ``person`` is the person associated to the address.
* ``manager`` is the manager role associated to the address.

Note that only one of ``org_unit``, ``person`` and ``manager`` can be supplied.

More information regarding creating and editing addresses can be found in the
sections on creating and editing relations for employees and organisational
units.

.. _DAR: https://dawa.aws.dk/dok/api/adresse


API
^^^

.. qrefflask:: mora.app:app
   :blueprints: address
   :order: path

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :order: path
   :blueprints: address

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
