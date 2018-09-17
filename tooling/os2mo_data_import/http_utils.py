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
