#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .. import lora
from .. import util
from .. import exceptions


def _set_virkning(lora_obj: dict, virkning: dict) -> dict:
    """Adds virkning to the "leafs" of the given LoRa JSON (tree) object

    :param lora_obj: a LoRa object with or without virkning. All
                     virknings that are already set will be changed
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


def _create_virkning(From: str, to: str, from_included=True,
                     to_included=False) -> dict:
    """
    Create virkning from frontend request
    :param From: the "from" date
    :param to: the "to" date
    :param from_included: specify if the from-date should be included or not
    :param to_included: specify if the to-date should be included or not
    :return: the virkning object
    """
    return {
        'from': util.reparsedatetime(From),
        'to': util.reparsedatetime(to),
        'from_included': from_included,
        'to_included': to_included
    }


def create_org_unit(req: dict) -> dict:
    """Create org unit data to send to LoRa

    :param : Dictionary representation of JSON request from the frontend
    :return: Dictionary representation of the org unit JSON object to send to
             LoRa

    """

    # Create virkning
    # NOTE: 'to' date is always infinity here but if the 'valid-to' is set in
    # the frontend request, the org unit end-date will be changed elsewhere
    virkning = _create_virkning(req.get('valid-from', '-infinity'), 'infinity')

    # Create the organisation unit object
    org_unit = {
        'attributter': {
            'organisationenhedegenskaber': [
                {
                    'enhedsnavn': req['name'],
                    'brugervendtnoegle': req['name'].replace(' ', ''),
                    # TODO: make a proper function to set the bvn
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
                                'uuid': location['location'][
                                    'UUID_EnhedsAdresse'],
                            }

                            # TODO: will we ever have more than one location?
                            # (multiple locations not tested) (however,
                            # multiple contact channels are tested)

                            for location in req.get('locations', [])
                        ] + [
                            {
                                'urn': 'urn:magenta.dk:telefon:{}'.format(
                                    channel['contact-info'],
                                ),
                            }
                            for location in req.get('locations', [])
                            for channel in location.get('contact-channels', [])
                        ] or nullrelation,
            # TODO: will "... or nullrelation" ever happen?
            # (no test for this yet...)
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


def inactivate_org_unit(date: str) -> dict:
    """
    Inactivate an org unit
    :param date: the date to inactivate the org unit from
    :return: the payload JSON used to update LoRa
    """

    obj_path = ['tilstande', 'organisationenhedgyldighed']
    props = {'gyldighed': 'Inaktiv'}

    return _create_payload(date, 'infinity', obj_path, props,
                           'Afslut enhed')


def move_org_unit(req: dict) -> dict:
    """
    Move an org unit to a new parent unit
    :param req: the JSON reqeust from the frontend
    :return: the payload JSON used to update LoRa
    """

    # TODO: add more asserts

    date = req['moveDate']
    obj_path = ['relationer', 'overordnet']
    props = {'uuid': req['newParentOrgUnitUUID']}

    return _create_payload(date, 'infinity', obj_path, props,
                           'Flyt enhed')


def rename_org_unit(req: dict) -> dict:
    """
    Rename an org unit.
    :param req: the JSON request sent from the frontend
    :return: the payload JSON used to update LoRa
    """

    From = req['valid-from']
    to = req['valid-to']
    obj_path = ['attributter', 'organisationenhedegenskaber']
    props = {'enhedsnavn': req['name']}

    return _create_payload(From, to, obj_path, props,
                           'Omdøb enhed')


def retype_org_unit(req: dict) -> dict:
    """
    Change the type of the org unit
    :param req: the JSON request sent from the frontend
    :return: the payload JSON used to update LoRa
    """

    From = req['valid-from']
    to = req['valid-to']
    obj_path = ['relationer', 'enhedstype']
    props = {'uuid': req['type']['uuid']}

    return _create_payload(From, to, obj_path, props, 'Ret enhedstype')


def _create_payload(From: str, to: str, obj_path: list,
                    props: dict, note: str) -> dict:
    # TODO: test this

    payload = {
        'note': note,
    }
    current_value = payload
    while obj_path:
        key = obj_path.pop(0)
        if obj_path:
            current_value[key] = {}
            current_value = current_value[key]
        else:
            props['virkning'] = _create_virkning(From, to)
            current_value[key] = [props]

    return payload


# ---------------------------- Updating addresses -------------------------- #

# ---- Handling of role types: contact-channel, location andn None ---- #


def _add_contact_channels(org_unit: dict,
                          contact_channels: list) -> dict:
    """
    Adds new contact channels to the address list
    :param org_unit: the org unit to update
    :param contact_channels: list of contact channels to add
    :return: updated list of addresses
    """
    addresses = org_unit['relationer']['adresser'].copy()

    if contact_channels:
        addresses.extend([
            {
                'urn': info['type']['prefix'] + info['contact-info'],
                'virkning': _create_virkning(info['valid-from'],
                                             info['valid-to']),
            }
            for info in contact_channels
        ])

    return addresses


# Role type location
def _update_existing_address(org_unit: dict,
                             address_uuid: str,
                             location: dict,
                             From: str,
                             to: str) -> list:
    """
    Used to update an already existing address
    :param org_unit: the org unit to update
    :param address_uuid: the address UUID to update
    :param location: location JSON given by the frontend
    :param From: the start date
    :param to: the end date
    :return: the updated list of addresses
    """

    # Note: the frontend makes a call for each location it wants to update

    assert location

    addresses = [
        addr if addr.get('uuid') != address_uuid else {
            'uuid': (location.get('UUID_EnhedsAdresse') or location['uuid']),
            'virkning': _create_virkning(From, to),
        }
        for addr in org_unit['relationer']['adresser']
    ]

    return addresses


# Role type not set in payload JSON
def _add_location(org_unit: dict, location: dict, From: str, to: str) -> dict:
    """
    Adds a new location the the existing list of addresses
    :param org_unit: the org unit to update
    :param location: the new location to add
    :param From: the start date of the address
    :param to: the end date of the address
    :return: the updated list of addresses
    """

    # Note: the frontend makes a call for each location it wants to update

    assert location

    new_addr = {
        'uuid': location['UUID_EnhedsAdresse'],
        'virkning': _create_virkning(From, to),
    }

    addresses = org_unit['relationer']['adresser'].copy()
    addresses.append(new_addr)

    return addresses


def _check_arguments(mandatory_args: list, args_to_check: list):
    for arg in mandatory_args:
        if arg not in args_to_check:
            raise exceptions.IllegalArgumentException('%s missing' % arg)


def create_update_kwargs(roletype: str, req: dict) -> dict:
    if roletype == 'contact-channel':
        if 'location' in req:
            kwargs = {'contact_channels': req['contact-channels']}
        else:
            kwargs = {}
    elif roletype == 'location':
        kwargs = {
            'address_uuid': req['uuid'],
            'location': req['location'],
            'From': req['valid-from'],
            'to': req['valid-to']
        }
    elif roletype:
        raise NotImplementedError(roletype)
    else:
        kwargs = {
            'location': req['location'],
            'From': req['valid-from'],
            'to': req['valid-to']
        }

    return kwargs


def update_org_unit_addresses(unitid: str, roletype: str, **kwargs):
    # TODO: use danchr's decorator (not yet committed) on the route instead
    assert roletype in ['contact-channel', 'location', None]

    org_unit = lora.organisationenhed(uuid=unitid)[0]['registreringer'][-1]

    if roletype == 'contact-channel':
        if 'contact_channels' in kwargs:
            # Adding contact channels
            note = 'Tilføj kontaktkanal'
            updated_addresses = _add_contact_channels(
                org_unit, kwargs['contact_channels'])
        else:
            # Contact channel already exists
            note = 'Tilføj eksisterende kontaktkanal'
            updated_addresses = []
    elif roletype == 'location':
        # Updating an existing address
        _check_arguments(['address_uuid', 'location', 'From', 'to'],
                         list(kwargs.keys()))
        note = 'Ret adresse'
        updated_addresses = _update_existing_address(
            org_unit, kwargs['address_uuid'], kwargs['location'],
            kwargs['From'], kwargs['to']
        )
    else:
        # Roletype is None - adding new location
        _check_arguments(['location', 'From', 'to'], list(kwargs.keys()))
        note = 'Tilføj addresse'
        updated_addresses = _add_location(org_unit, kwargs['location'],
                                          kwargs['From'], kwargs['to'])

    payload = {
        'note': note,
        'relationer': {
            'adresser': updated_addresses
        }
    }

    return payload
