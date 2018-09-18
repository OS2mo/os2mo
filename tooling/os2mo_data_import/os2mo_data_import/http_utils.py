# -- coding: utf-8 --

import json
from requests import Session


# Temporary settings
MOX_BASE_URI = "http://localhost:8080"
MORA_BASE_URI = "http://localhost:5000"


def get_request(url, **params):

    request = Session()

    response = request.get(url, params=params)

    if response.status_code != 200:
        print(response.text)
        raise ConnectionError("Get request failed")

    return response


def post_request(url, payload):

    request = Session()

    response = request.post(
        url=url,
        json=payload
    )

    if not response.status_code == 200:
        print("POST REQUEST: {}".format(url))
        output = json.dumps(response.json(), indent=2)

        print("============ RESPONSE =============")
        print(output)

        print("============ PAYLOAD =============")
        print(payload)

    return response.json()


def put_request(url, payload):

    request = Session()

    try:

        response = request.put(
            url=url,
            json=payload
        )
    except Exception as error:
        print(error)
        return
    #
    # if response.status_code != 200:
    #     print(response.text)
    #     raise ConnectionError("PUT request failed")



    return response.json()


def import_mox_data(resource, identifier, payload):

    # TODO: add resolve functionality
    service_endpoint = "{base}/{resource}/{uuid}".format(
        base=MOX_BASE_URI,
        resource=resource,
        uuid=identifier
    )

    return put_request(service_endpoint, payload)


def import_mora_data(resource, payload):

    # TODO: add resolve functionality
    service_endpoint = "{base}/{resource}".format(
        base=MORA_BASE_URI,
        resource=resource
    )

    return post_request(service_endpoint, payload)


def import_org_unit(payload):

    processed_payload = payload

    return import_mora_data("service/ou/create", processed_payload)


def import_relationship(unit_name, metadata):
    print("METADATA for {}:".format(unit_name))
    print(metadata)

    return True


def import_all_org_units(org_unit_object):

    inserted = []

    for unit_name in org_unit_object.get_available():
        unit_uuid = org_unit_object.get_uuid(unit_name)
        unit_data = org_unit_object.get_data(unit_name)
        unit_metadata = org_unit_object.get_metadata(unit_name)

        print(unit_name, unit_data, unit_metadata)

        unit_import_uuid = {
            "uuid": unit_uuid
        }

        unit_data.update(unit_import_uuid)

        store = import_org_unit(unit_data)

        if store:
            inserted.append(unit_uuid)

        create_rel = import_relationship(unit_name, unit_metadata)


    return inserted

def import_all_employees():

    data = {
        "name": "Jean-Luc And",
        "cpr_no": "0101501234",
        "user_key": "1234",
        "org": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f"
    }
