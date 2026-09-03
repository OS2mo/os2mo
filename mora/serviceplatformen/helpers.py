# SPDX-FileCopyrightText: 2017 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import httpx
from jinja2 import Template


def construct_envelope_SF1520(template, service_uuids, cprnr):  # pragma: no cover
    """The function returns an envelope for the service
    'SF1520 - Udvidet person stamdata (lokal)'."""

    with open(template) as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids["service_agreement"],
        user_system=service_uuids["user_system"],
        user=service_uuids["user"],
        service=service_uuids["service"],
    )

    # service platform requirement.
    latin_1_encoded_soap_envelope = populated_template.encode("latin-1")

    return latin_1_encoded_soap_envelope


def http_post(endpoint, soap_envelope, certificate):  # pragma: no cover
    if not endpoint and not soap_envelope and not certificate:
        return None

    response = httpx.post(endpoint, content=soap_envelope, cert=certificate)

    return response
