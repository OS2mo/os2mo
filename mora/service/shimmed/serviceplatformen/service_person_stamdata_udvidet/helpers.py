# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re
import requests
from jinja2 import Template

__author__ = "Heini Leander Ovason"


def construct_envelope_SF1520(template, service_uuids, cprnr):
    """The function returns an envelope for the service
    'SF1520 - Udvidet person stamdata (lokal)'."""

    with open(template, "r") as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids['service_agreement'],
        user_system=service_uuids['user_system'],
        user=service_uuids['user'],
        service=service_uuids['service']
    )

    # service platform requirement.
    latin_1_encoded_soap_envelope = populated_template.encode('latin-1')

    return latin_1_encoded_soap_envelope


def construct_envelope_SF6002(
    template,
    service_uuids,
    cprnr,
    operation,
    parameter_type
):
    """The function returns an envelope for the service
    'SF6002 - CPR Abonnement'."""

    with open(template, "r") as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids['service_agreement'],
        user_system=service_uuids['user_system'],
        user=service_uuids['user'],
        service=service_uuids['service'],
        operation=operation,
        parameter_type=parameter_type
    )

    # service platform requirement.
    latin_1_encoded_soap_envelope = populated_template.encode('latin-1')

    return latin_1_encoded_soap_envelope


def http_post(endpoint, soap_envelope, certificate):

    if not endpoint and not soap_envelope and not certificate:
        return None

    response = requests.post(
        url=endpoint,
        data=soap_envelope,
        cert=certificate
    )

    return response


def validate_cprnr(cprnr):

    if not cprnr:
        # Log e.g. 'Type error occured: input'
        return False

    check = re.match(r'^\d{10}$', cprnr)

    if not check:
        # Log e.g. 'Not a valid cprnr'
        return False

    return True

