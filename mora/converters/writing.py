#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import mora.util as util


def _add_virkning_to_lora_object(lora_obj: dict, virkning: dict) -> dict:
    for k, v in lora_obj.items():
        if isinstance(v, dict):
            _add_virkning_to_lora_object(v, virkning)
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
        'from': util.reparsedate(req.get('valid-from'), '-infinity'),
        'to': util.reparsedate(req.get('valid-to'), 'infinity'),
    }

    nullrelation = [{
        'virkning': virkning,
    }]

#     org_unit = {
#         'attributter': {
#             'organisationenhedegenskaber': [
#                 {
#                     'enhedsnavn': req['name'],
#                     'brugervendtnoegle': req['user-key'],
# #                    'virkning': virkning.copy(),
#                 },
#             ],
#         },
#         'tilstande': {
#             'organisationenhedgyldighed': [
#                 {
#                     'gyldighed': 'Aktiv',
# #                   'virkning': virkning.copy(),
#                 },
#             ],
#         },
#         'relationer': {
#             'adresser': [
#                 {
#                     'uuid': location['location']['UUID_EnhedsAdresse'],
# #                   'virkning': virkning.copy(),
#                 }
#                 for location in req.get('locations', [])
#             ] + [
#                 {
#                     'urn': 'urn:magenta.dk:telefon:{}'.format(
#                         channel['contact-info'],
#                     ),
#  #                  'virkning': virkning.copy(),
#                 }
#                 for location in req.get('locations', [])
#                 for channel in location.get('contact-channels', [])
#             ] or nullrelation,
#             'tilhoerer': [
#                 {
#                     'uuid': req['org'],
# #                   'virkning': virkning.copy(),
#                 }
#             ],
#             # 'tilknyttedeenheder': [
#             #     {
#             #         'urn': req['tilknyttedeenheder'],
#             #         'virkning': virkning.copy(),
#             #     }
#             # ],
#             'enhedstype': [
#                 {
#                     'uuid': req['type']['uuid'],
# #                   'virkning': virkning.copy(),
#                 }
#             ],
#             'overordnet': [
#                 {
#                     'uuid': req['parent'],
# #                    'virkning': virkning.copy(),
#                 }
#             ],
#         }
#     }
#
#
#     return virkning
    return {}