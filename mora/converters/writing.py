#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import datetime

from .. import lora
from .. import util
from .. import exceptions

from . import meta


def _set_virkning(lora_obj: dict, virkning: dict) -> dict:
    """
    Adds virkning to the "leafs" of the given LoRa JSON (tree) object.

    :param lora_obj: A LoRa object with or without virkning. All virknings that
        are already set will be preserved.
    :param virkning: The virkning to set in the LoRa object
    :return: The LoRa object with the new virkning

    """
    for k, v in lora_obj.items():
        if isinstance(v, dict):
            _set_virkning(v, virkning)
        elif isinstance(v, list):
            for d in v:
                d.setdefault('virkning', virkning.copy())
    return lora_obj


def _create_virkning(From: str, to: str, from_included=True,
                     to_included=False, note=None) -> dict:
    """
    Create virkning from frontend request.

    :param From: The "from" date.
    :param to: The "to" date.
    :param from_included: Specify if the from-date should be included or not.
    :param to_included: Specify if the to-date should be included or not.
    :return: The virkning object.
    """
    d = {
        'from': util.to_lora_time(From),
        'to': util.to_lora_time(to),
        'from_included': from_included if not From == '-infinity' else False,
        'to_included': to_included if not to == 'infinity' else False
    }
    if note:
        d['notetekst'] = str(note)
    return d


def create_org_unit(req: dict) -> dict:
    """
    Create org unit data to send to LoRa.

    :param req: Dictionary representation of JSON request from the frontend.
    :return: Dictionary representation of the org unit JSON object to send to
        LoRa.
    """

    # Create virkning

    # NOTE: 'to' date is always infinity here but if the 'valid-to' is set in
    # the frontend request, the org unit end-date will be changed below
    virkning = _create_virkning('-infinity', 'infinity')

    # Create the organisation unit object
    org_unit = {
        'note': 'Oprettet i MO',
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
                    'virkning': dict(
                        **virkning,
                        notetekst=str(
                            meta.Address.fromdict(location)),
                    ),
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
                    'virkning': dict(
                        **virkning,
                        notetekst=str(meta.PhoneNumber(
                            location=location['location']
                            ['UUID_EnhedsAdresse'],
                            visibility=channel['visibility'][
                                'user-key'],
                        )),
                    ),
                }
                for location in req.get('locations', [])
                for channel in location.get('contact-channels', [])
            ],
            # TODO: what happens if we have neither locations nor addresses?
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

    org_unit = _set_virkning(org_unit, virkning)
    org_unit['tilstande']['organisationenhedgyldighed'][0]['virkning'][
        'from'] = util.to_lora_time(req.get('valid-from'))
    org_unit['tilstande']['organisationenhedgyldighed'][0]['virkning'][
        'from_included'] = True

    # TODO: refactor - lines below are also found in the retype function
    org_unit['tilstande']['organisationenhedgyldighed'].append(
        {
            'gyldighed': 'Inaktiv',
            'virkning': _create_virkning('-infinity', req.get('valid-from'),
                                         False, False)
        }
    )
    if 'valid-to' in req:
        org_unit['tilstande']['organisationenhedgyldighed'][0]['virkning'][
            'to'] = util.to_lora_time(req.get('valid-to'))
        org_unit['tilstande']['organisationenhedgyldighed'].append(
            {
                'gyldighed': 'Inaktiv',
                'virkning': _create_virkning(req['valid-to'], 'infinity')
            }
        )

    return org_unit


def inactivate_org_unit(startdate: str, enddate: str) -> dict:
    """
    Inactivate an org unit.

    :param startend: The date from which the org unit is active.
    :param enddate: The date to inactivate the org unit from.
    :return: The payload JSON used to update LoRa.
    """

    obj_path = ['tilstande', 'organisationenhedgyldighed']
    props_active = {'gyldighed': 'Aktiv'}
    props_inactive = {'gyldighed': 'Inaktiv'}

    payload = _create_payload('-infinity', startdate, obj_path, props_inactive,
                              'Afslut enhed')
    payload = _create_payload(startdate, enddate, obj_path, props_active,
                              'Afslut enhed', payload)
    payload = _create_payload(enddate, 'infinity', obj_path, props_inactive,
                              'Afslut enhed', payload)

    return payload


def move_org_unit(req: dict) -> dict:
    """
    Move an org unit to a new parent unit.

    :param req: The JSON reqeust from the frontend.
    :return: The payload JSON used to update LoRa.
    """

    date = req['moveDate']
    obj_path = ['relationer', 'overordnet']
    props = {'uuid': req['newParentOrgUnitUUID']}

    return _create_payload(date, 'infinity', obj_path, props,
                           'Flyt enhed')


def rename_org_unit(req: dict) -> dict:
    """
    Rename an org unit.

    :param req: The JSON request sent from the frontend.
    :return: The payload JSON used to update LoRa.
    """

    From = req['valid-from']
    to = req.get('valid-to', 'infinity')
    obj_path = ['attributter', 'organisationenhedegenskaber']
    props = {'enhedsnavn': req['name']}

    return _create_payload(From, to, obj_path, props,
                           'Omdøb enhed')


# TODO: rename this function...
def retype_org_unit(req: dict) -> dict:
    """
    Change the type or start-date of the org unit.

    :param req: The JSON request sent from the frontend.
    :return: The payload JSON used to update LoRa.
    """

    payload = None

    if 'type-updated' in req.keys():
        # Update the org unit type
        From = datetime.datetime.today()
        obj_path = ['relationer', 'enhedstype']
        props = {'uuid': req['type']['uuid']}
        to = req['valid-to']
        payload = _create_payload(From, to, obj_path, props, 'Ret enhedstype')

    if 'valid-from-updated' in req.keys():
        # Update the org unit start-date
        From = req['valid-from']
        obj_path = ['tilstande', 'organisationenhedgyldighed']
        props = {'gyldighed': 'Aktiv'}
        to = req['valid-to']
        payload = _create_payload(From, to, obj_path, props,
                                  'Ret enhedstype og start dato'
                                  if payload else 'Ret start dato', payload)

        # TODO: maybe the adding-more-stuff-to-a-payload functionality below
        # should be moved into the _create_payload function

        payload['tilstande']['organisationenhedgyldighed'].append(
            {
                'gyldighed': 'Inaktiv',
                'virkning': _create_virkning('-infinity', From, False, False)
            }
        )

    return payload


def _create_payload(From: str, to: str, obj_path: list,
                    props: dict, note: str, payload: dict = None) -> dict:
    """
    Generate payload to send to LoRa when updating or writing new data. See
    the example below.

    :param From: The "from" date.
    :param to: The "to" date.
    :param obj_path: List with "path" to object to add.
    :param props: Properties to add.
    :param note: Note to add to the payload.
    :param payload: An already existing payload that should have extra
        properties added.
    :return: The resulting payload (see example below).

    :Example:

    >>> _create_payload(
            '01-01-2017', '01-01-2018',
            ['tilstande', 'organisationenhedgyldighed'],
            {'gyldighed': 'Aktiv'}, 'Ret gyldighed'
        )
        {
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'to': '2018-01-01T00:00:00+01:00',
                            'from_included': True,
                            'from': '2017-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    }
                ]
            },
            'note': 'Ret gyldighed'
        }
    """

    obj_path_copy = obj_path.copy()
    props_copy = props.copy()

    if payload:
        payload['note'] = note
    else:
        payload = {
            'note': note,
        }

    current_value = payload
    while obj_path_copy:
        key = obj_path_copy.pop(0)
        if obj_path_copy:
            if key not in current_value.keys():
                current_value[key] = {}
            current_value = current_value[key]
        else:
            props_copy['virkning'] = _create_virkning(From, to)
            if key in current_value.keys():
                current_value[key].append(props_copy)
            else:
                current_value[key] = [props_copy]

    return payload


# ---------------------------- Updating addresses -------------------------- #

# ---- Handling of role types: contact-channel, location and None ---- #


def _add_contact_channels(org_unit: dict, location: dict,
                          contact_channels: list) -> dict:
    """
    Adds new contact channels to the address list.

    :param org_unit: The org unit to update.
    :param location: The location to attach the contact channel to.
    :param contact_channels: List of contact channels to add.
    :return: The updated list of addresses.
    """
    addresses = org_unit['relationer']['adresser'].copy()

    if contact_channels:
        addresses.extend([
            {
                'urn': info['type']['prefix'] + info['contact-info'],
                'virkning': _create_virkning(
                    info['valid-from'],
                    info['valid-to'],
                    note=meta.PhoneNumber(
                        location=location['uuid'],
                        visibility=info['visibility']['user-key'],
                    ),
                ),
            }
            for info in contact_channels
        ])

    return addresses


# Role type location
def _update_existing_address(org_unit: dict,
                             address_uuid: str,
                             location: dict,
                             From: str,
                             to: str, **kwargs) -> list:
    """
    Used to update an already existing address.

    :param org_unit: The org unit to update.
    :param address_uuid: The address UUID to update.
    :param location: Location JSON given by the frontend.
    :param From: The start date.
    :param to: The end date.
    :return: The updated list of addresses.
    """

    # Note: the frontend makes a call for each location it wants to update

    assert location

    addresses = [
        address if address.get('uuid') != address_uuid else {
            'uuid': (location.get('UUID_EnhedsAdresse') or location['uuid']),
            'virkning': _create_virkning(From, to,
                                         note=meta.Address(**kwargs)),
        }
        for address in org_unit['relationer']['adresser']
    ]

    return addresses


# Role type not set in payload JSON
def _add_location(org_unit: dict, location: dict, From: str, to: str,
                  **kwargs: dict) -> dict:
    """
    Adds a new location the the existing list of addresses.

    :param org_unit: The org unit to update.
    :param location: The new location to add.
    :param From: The start date of the address.
    :param to: The end date of the address.
    :param kwargs: The necessary data from the frontend request.
    :return: The updated list of addresses.
    """

    # Note: the frontend makes a call for each location it wants to update

    assert location

    new_addr = {
        'uuid': location['UUID_EnhedsAdresse'],
        'virkning': _create_virkning(From, to,
                                     note=meta.Address(**kwargs)),
    }

    addresses = org_unit['relationer']['adresser'].copy()
    addresses.append(new_addr)

    return addresses


def _check_arguments(mandatory_args: collections.abc.Iterable,
                     args_to_check: collections.abc.Iterable):
    """
    Check that the mandatory arguments are present when updating or adding new
    locations to an org unit.

    :param mandatory_args: List of mandatory arguments.
    :param args_to_check: List of arguments to check.
    :raises: IllegalArgumentException if the argument list does not contain all
        the mandatory arguments.
    """
    for arg in mandatory_args:
        if arg not in args_to_check:
            raise exceptions.IllegalArgumentException('%s missing' % arg)


def create_update_kwargs(req: dict) -> dict:
    """
    Pick out the necessary data from the frontend request depending on
    the roletype - the frontend handles location updates in a very funny
    way...

    :param req: The frontend request.
    :return: The necessary data depending on the roletype.
    """

    roletype = req.get('role-type')

    if roletype == 'contact-channel':
        if 'location' in req:
            kwargs = {
                'contact_channels': req['contact-channels'],
                'roletype': roletype,
                'location': req['location'],
            }
        else:
            kwargs = {
                'roletype': roletype,
            }
    elif roletype == 'location':
        kwargs = {
            'roletype': roletype,
            'address_uuid': req['uuid'],
            'location': req['location'],
            'From': req['valid-from'],
            'to': req['valid-to'],
            'name': req['name'],
            'primary': req.get('primaer', False),
        }
    elif roletype:
        raise NotImplementedError(roletype)
    else:
        kwargs = {
            'roletype': roletype,
            'location': req['location'],
            'From': req['valid-from'],
            'to': req['valid-to'],
            'name': req['name'],
            'primary': req.get('primaer', False),
        }

    return kwargs


def update_org_unit_addresses(unitid: str, roletype: str, **kwargs):
    """
    Update or add an org unit address or contact channel.

    :param unitid: The org unit UUID.
    :param roletype: The roletype (contact-channel, location, None) to use -
      this is handled in a funny way by the frontend!?
    :param kwargs: The required data from the frontend request.
    :return: The payload to send (PUT) to LoRa.
    """

    assert roletype in ['contact-channel', 'location', None]

    org_unit = lora.organisationenhed(
        uuid=unitid, virkningfra='-infinity', virkningtil='infinity')[0][
        'registreringer'][-1]

    if roletype == 'contact-channel':
        if 'contact_channels' in kwargs:
            # Adding contact channels
            note = 'Tilføj kontaktkanal'
            updated_addresses = _add_contact_channels(
                org_unit, **kwargs)
        else:
            # Contact channel already exists
            note = 'Tilføj eksisterende kontaktkanal'
            updated_addresses = []
    elif roletype == 'location':
        # Updating an existing address
        _check_arguments(['address_uuid', 'location', 'From', 'to',
                          'name', 'primary'],
                         kwargs)
        note = 'Ret adresse'
        updated_addresses = _update_existing_address(org_unit, **kwargs)
    else:
        # Roletype is None - adding new location
        _check_arguments(['location', 'From', 'to', 'name', 'primary'],
                         kwargs)
        note = 'Tilføj addresse'
        updated_addresses = _add_location(org_unit, **kwargs)

    payload = {
        'note': note,
        'relationer': {
            'adresser': updated_addresses
        }
    }

    return payload
