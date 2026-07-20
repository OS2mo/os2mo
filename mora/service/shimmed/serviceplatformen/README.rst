service_person_stamdata_udvidet
*******************************
Package that integrates with the SF1520 API's PersonBaseDataExtendedService at serviceplatformen.dk

:Author:
    Heini Leander Ovason <heini@magenta.dk>


Quick notes regarding use of the test and production service webapi
===================================================================
Please note that access to the service webapi depends on the level of service agreement in place. 

The service agreement may only grant access to either the test or the production service. 
(It may also be possible to have an agreement which grants access to both systems)

**Thus access to the production service does not automatically
constitue access to the test service.**

The api exposes a toggle to access either the production or the test system (production by default):

.. code-block:: python


    get_citizen(..., production=<True|False>)


Additionally it is also important to note that it is not possible
to use "real" cpr identifiers on the test system and vice versa. 



API (with examples)
===================

*In order for this package to interact with Serviceplatformen you need valid 'Invocation context' UUIDs and a certificate.*

get_citizen()
-------------
*The function serves as a facade to ease interaction with the SF1520 API's PersonBaseDataExtendedService at serviceplatformen.dk*

.. code-block:: python

    # -- coding: utf-8 --
    import json

    from service_person_stamdata_udvidet import  get_citizen

    uuids = {
        'service_agreement': '42571b5d-6371-4edb-8729-1343a3f4c9b9',
        'user_system': '99478e20-68e6-41ff-b822-681fb69b8ff2',
        'user': 'e3108916-8ed9-4482-8045-7b46c83904b0',
        'service': '9883c483-d42f-424a-9a2a-94d1d200d294'
    }

    certificate = '/path/to/certificate.crt'

    cprnr = '0123456789'

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr,
        production=True,  # By default set to `False` in get_citizen(). Specify `True` target production environment.
        api_version=<int> # Type: Integer. Options: 4 or 5
    )

    print(json.dumps(result))

`Example Output <https://pastebin.com/MSmk3YaB>`_

test can be run from this directory by issuing 

    python -m unittest discover


