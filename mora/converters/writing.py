#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import mora.util as util


def _add_virkning(lora_obj: dict, virkning: dict) -> dict:
    """
    Adds virkning to the "leafs" of the given LoRa JSON (tree) object
    :param lora_obj: a LoRa object without virkning
    :param virkning: the virkning to add to the LoRa object
    :return: the LoRa object with virkning
    """
    for k, v in lora_obj.items():
        if isinstance(v, dict):
            _add_virkning(v, virkning)
        else:
            assert isinstance(v, list)
            for d in v:
                d['virkning'] = virkning
    return lora_obj


def create_org_unit(req: dict) -> dict:
    """
    Create org unit data to send to LoRa
    :param : Dictionary representation of JSON request from the frontend 
    :return: Dictionary representation of the org unit JSON object to send to LoRa
    """

    # Create virkning
    virkning = {
        'from': util.reparsedate(req.get('valid-from')),
        'to': util.reparsedate(req.get('valid-to')),
    }

    nullrelation = [{
        'virkning': virkning,
    }]

    # Create the organisation unit object
    org_unit = {
        'attributter': {
            'organisationenhedegenskaber': [
                {
                    'enhedsnavn': req['name'],
                    'brugervendtnoegle': req['name'].replace(' ', ''),  # TODO: make a proper function to set the bvn
                },
            ],
        },
        'tilstande': {
            'organisationenhedgyldighed': [
                {
                    'gyldighed': 'Aktiv',
                },
            ],
        },
        'relationer': {
            'adresser': [
                            {
                                'uuid': location['location']['UUID_EnhedsAdresse'],
                            }
                            # TODO: will we ever have more than one location? (multiple locations not tested)
                            # TODO: (however, multible contact channels are tested)
                            for location in req.get('locations', [])
                        ] + [
                            {
                                'urn': 'urn:magenta.dk:telefon:{}'.format(
                                    channel['contact-info'],
                                ),
                            }
                            for location in req.get('locations', [])
                            for channel in location.get('contact-channels', [])
                        ] or nullrelation,  # TODO: will "... or nullrelation" ever happen? (no test for this yet...)
            'tilhoerer': [
                {
                    'uuid': req['org'],
                }
            ],
            'enhedstype': [
                {
                    'uuid': req['type']['uuid'],
                }
            ],
            'overordnet': [
                {
                    'uuid': req['parent'],
                }
            ],
        }
    }

    return _add_virkning(org_unit, virkning)
