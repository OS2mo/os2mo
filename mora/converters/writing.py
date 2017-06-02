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


def _create_virkning(req: dict) -> dict:
    return {
        'from': util.reparsedate(req.get('valid-from')),
        'to': util.reparsedate(req.get('valid-to')),
    }


def extend_current_virkning(lora_registrering_obj: dict, virkning: dict) -> dict:
    """
    Extend the elements in a given LoRa "registrering" object to also apply during the new "virkning" 
    :param lora_registrering_obj: a LoRa "registrering" object (pre-condition: must only contain data for present date)
    :param virkning: the new "virkning" to apply
    :return: a LoRa "registrering" object extended with the given "virkning"
    """

    # TODO: Quick and dirty to make things work...
    # TODO: refactor common functionality in this function and _add_virkning into separate function (or make class)
    # TODO: add (more) test cases!!!

    for k, v in lora_registrering_obj.items():
        if isinstance(v, dict):
            extend_current_virkning(v, virkning)
        elif isinstance(v, list):
            new_objs = []
            for d in v:
                d_copy = d.copy()
                d_copy['virkning'] = virkning
                new_objs.append(d_copy)
            v.extend(new_objs)
        else:
            pass
    return lora_registrering_obj


def create_org_unit(req: dict) -> dict:
    """
    Create org unit data to send to LoRa
    :param : Dictionary representation of JSON request from the frontend 
    :return: Dictionary representation of the org unit JSON object to send to LoRa
    """

    # Create virkning
    virkning = _create_virkning(req)

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
