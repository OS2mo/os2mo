#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import mora.lora as lora
import mora.util as util
from pprint import pprint

def _set_virkning(lora_obj: dict, virkning: dict) -> dict:
    """
    Adds virkning to the "leafs" of the given LoRa JSON (tree) object
    :param lora_obj: a LoRa object with or without virkning. All virknings that are already set will be changed
    :param virkning: the virkning to set in the LoRa object
    :return: the LoRa object with the new virkning
    """
    for k, v in lora_obj.items():
        if isinstance(v, dict):
            _set_virkning(v, virkning)
        elif isinstance(v, list):
            for d in v:
                d['virkning'] = virkning
        else:
            pass
    return lora_obj


def _create_virkning(From: str, to: str, from_included=True, to_included=False) -> dict:
    # TODO: fix doc string
    """
    Create virkning from frontend request
    :param req: the JSON request object provided by the frontend
    :param from_included: specify if the from-date should be included or not
    :param to_included: specify if the to-date should be included or not
    :return: the virkning object
    """
    return {
        'from': util.reparsedate(From),
        'to': util.reparsedate(to),
        'from_included': from_included,
        'to_included': to_included
    }


def _extend_current_virkning(lora_registrering_obj: dict, virkning: dict) -> dict:
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
            _extend_current_virkning(v, virkning)
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
    virkning = _create_virkning(req.get('valid-from', '-infinity'),
                                req.get('valid-to', 'infinity'))

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

    return _set_virkning(org_unit, virkning)


def rename_org_unit(req: dict) -> dict:
    """
    Rename an org unit.
    Pre-condition: all virknings in the given org unit must have 'to' set to infinity
    Pre-condition: the current time must be small than or equal to the date, where the renaming should take effect
    :param req: the JSON request sent from the frontend
    :return: the updated org unit with a new org unit name from the (in the req) given date
    """

    assert util.now() <= util.parsedate(req['valid-from'])
    # TODO: add more asserts (see pre-conditions above)

    # Get the current org unit and update this
    org_unit = lora.organisationenhed(uuid=req['uuid'])[0]['registreringer'][-1]

    assert len(org_unit['attributter']['organisationenhedegenskaber']) == 1
    organisationsegenskaber = org_unit['attributter']['organisationenhedegenskaber']

    # Create current end new virkning: [----- name1 -----)[----- name2 ----->
    # Time: |----------------------------now-------------------------------->

    current_virkning = _create_virkning(organisationsegenskaber[0]['virkning']['from'], req['valid-from'])
    new_virkning = _create_virkning(req['valid-from'], 'infinity')

    # Modify the old virkning
    organisationsegenskaber[0]['virkning'] = current_virkning

    # Set the new org unit name and the new virkning
    new_organisationsegenskab = organisationsegenskaber[0].copy()
    new_organisationsegenskab['enhedsnavn'] = req['name']
    new_organisationsegenskab['virkning'] = new_virkning
    organisationsegenskaber.append(new_organisationsegenskab)

    return org_unit
