# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import xmltodict
from .helpers import http_post
from .helpers import validate_cprnr
from .helpers import construct_envelope_SF1520

__author__ = "Heini Leander Ovason"


def get_citizen(service_uuids, certificate, cprnr, production=False, **kwargs):
    r"""
    The function returnes a citizen dict from the
    'SF1520 - Udvidet person stamdata (lokal)' service.
    It serves as a facade to simplify input validation, and interaction
    with the SOAP service, parsing and filtering the response.

    :param dict service_uuids: The required service uuids

    .. note::

        Here is sample of the service_uuid dictionary:
        
            {
                'service_agreement': '42571b5d-6371-4edb-8729-1343a3f4c9b9',
                'user_system': '99478e20-68e6-41ff-b822-681fb69b8ff2',
                'user': 'e3108916-8ed9-4482-8045-7b46c83904b0',
                'service': '9883c483-d42f-424a-9a2a-94d1d200d294'
            }

    :param str certificate: Path to the required certificate bundle

    :param str cprnr:  String of 10 digits -> r'^\d{10}$'
    
    :param bool production: Production/Test service mode toggle 

    .. note::

        Production and Test services are seperate systems hosted by
        serviceplatformen.

        Please note that it is NOT possible to use "real" cpr identifiers
        on the test platform and vice versa.


    :return: Dictionary representation of a citizen
    :rtype: dict
    """
    
    api_version = kwargs.get("api_version")
    if api_version:
        if api_version == 4 or api_version == 5:
            api_version = str(api_version)
        else:
            err_msg = "'{0}' is not a valid api version. If not perhaps input type was a str and not int(?)".format(api_version)
            raise ValueError(err_msg)

    service_url = "https://exttest.serviceplatformen.dk/service/CPR/PersonBaseDataExtended/{0}".format(api_version)
    if production:
        service_url = "https://prod.serviceplatformen.dk/service/CPR/PersonBaseDataExtended/{0}".format(api_version)

    is_cprnr_valid = validate_cprnr(cprnr)
    if is_cprnr_valid:

        template_directory = os.path.dirname(__file__)
        soap_envelope = "PersonBaseDataExtended_v{0}_envelope.xml".format(api_version)

        soap_envelope_template = os.path.join(
            template_directory, soap_envelope
        )

        soap_envelope = construct_envelope_SF1520(
            template=soap_envelope_template,
            service_uuids=service_uuids,
            cprnr=cprnr
        )
        response = call_cpr_person_lookup_request(
            soap_envelope=soap_envelope,
            certificate=certificate,
            service_url=service_url,
        )
        if response.status_code == 200:
            citizen_dict = parse_cpr_person_lookup_xml_to_dict(
                soap_response_xml=response.text,
                api_version=api_version
            )
            return citizen_dict
        else:
            response.raise_for_status()
            return {"Error": "Something went wrong"}


def call_cpr_person_lookup_request(soap_envelope, certificate, service_url):
    """Performs a web service call to 'Udvidet Person Stam Data(lokal)'.
    : param soap_envelope: SOAP envelope
    : param certificate: Path to certificate
    : param service_url: url endpoint for service
    : type soap_envelope: str
    : type certificate: str
    : type service_url: str
    :return: Complete serviceplatform xml representation of a citizen
    :rtype: str"""

    response = http_post(
        endpoint=service_url, soap_envelope=soap_envelope, certificate=certificate
    )

    return response


def parse_cpr_person_lookup_xml_to_dict(soap_response_xml, api_version):
    """Parses string xml to a dict
    : param soap_response_xml: xml
    : type soap_response_xml: str
    : return: Dictionary representation of a citizen
    : rtype: dict"""

    namespaces = {
        "http://serviceplatformen.dk/xml/schemas/cpr/PNR/1/": None,
        "http://serviceplatformen.dk/xml/schemas/InvocationContext/1/": None,
        "http://serviceplatformen.dk/xml/schemas/AuthorityContext/1/": None,
        "http://serviceplatformen.dk/xml/schemas/CallContext/1/": None,
        "http://serviceplatformen.dk/xml/wsdl/soap11/CPR/PersonBaseDataExtended/{0}/".format(api_version): None,
        "http://schemas.xmlsoap.org/soap/envelope/": None,
    }
    
    if api_version == "5": # Add additional namespace
        namespaces["http://serviceplatformen.dk/xml/schemas/ServiceplatformFault/1/"]: None

    # Use non-default namespace separator due to https://github.com/libexpat/libexpat/pull/577
    # until a new version of libexpat is stable.
    xml_to_dict = xmltodict.parse(
        soap_response_xml,
        process_namespaces=True,
        namespaces=namespaces,
        namespace_separator="|",
    )
    root = xml_to_dict["Envelope"]["Body"]["PersonLookupResponse"]

    citizen_dict = {}

    name = root["persondata"]["navn"]
    for k, v in name.items():
        citizen_dict[k] = v

    person_data = root["persondata"]
    person_data.pop("navn")
    for k, v in person_data.items():
        citizen_dict[k] = v

    address = root["adresse"]["aktuelAdresse"]
    if not address:
        address = {}
    for k, v in address.items():
        citizen_dict[k] = v

    try:
        not_living_in_dk = root["adresse"]["udrejseoplysninger"]  # noqa F841
        citizen_dict["udrejst"] = True
    except KeyError:
        citizen_dict["udrejst"] = False

    relations = root["relationer"]
    citizen_dict["relationer"] = []
    for k, v in relations.items():
        # NOTE: v is a dict if k is:
        # 'mor', 'far', or 'aegtefaelle'.
        if isinstance(v, dict):
            citizen_dict["relationer"].append(
                {"relation": k, "cprnr": v.get("personnummer")}
            )
        # NOTE: v is a list of dicts if k is 'barn'.
        if isinstance(v, list):
            for child in v:
                citizen_dict["relationer"].append(
                    {"relation": k, "cprnr": child.get("personnummer")}
                )

    return citizen_dict
