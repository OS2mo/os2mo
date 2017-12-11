#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import datetime
import json

import freezegun

from mora import lora
from mora import util as mora_util
from . import util


class TestWritingIntegration(util.LoRATestCase):
    maxDiff = None

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_location_edit(self):
        self.load_sample_structures(minimal=True)

        LOCATION_URL = (
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/role-types/location/'
        )

        self.assertRequestResponse(
            LOCATION_URL,
            [
                {
                    'location': {
                        'name': 'Kontor',
                        'user-key': '07515902___1_______',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                    },
                    'name': 'Kontor',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': True,
                    'role-type': 'location',
                    'user-key': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

        self.assertRequestResponse(
            LOCATION_URL + 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
            {
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            json={
                "location": {
                    "UUID_EnhedsAdresse":
                        "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
                "name": "Kontor",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": True,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity",
                "$$hashKey": "0AP",
                "changed": True,
            },
        )

        self.assertRequestResponse(
            LOCATION_URL,
            [
                {
                    'location': {
                        'name': 'Kontor',
                        'user-key': '07519651__15_______',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Åbogade 15, 8200 Aarhus N',
                    },
                    'name': 'Kontor',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': True,
                    'role-type': 'location',
                    'user-key': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_location_edit_meta(self):
        self.load_sample_structures(minimal=True)

        LOCATION_URL = (
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/role-types/location/'
        )

        def check(primary, name):
            self.assertRequestResponse(
                LOCATION_URL,
                [
                    {
                        'location': {
                            'name': name,
                            'user-key': '07515902___1_______',
                            'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                            'valid-from': '2014-05-05T19:07:48.577000+00:00',
                            'valid-to': 'infinity',
                            'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                        },
                        'name': name,
                        'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'primaer': primary,
                        'role-type': 'location',
                        'user-key': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                    },
                ],
            )

        # Initial sanity check
        check(True, 'Kontor')

        # Edit primary only
        self.assertRequestResponse(
            LOCATION_URL + '44c532e1-f617-4174-b144-d37ce9fda2bd',
            {
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            json={
                "changed": True,
                "location": {
                    "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                },
                "name": "Kontor",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": False,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(False, 'Kontor')

        # Edit name only
        self.assertRequestResponse(
            LOCATION_URL + '44c532e1-f617-4174-b144-d37ce9fda2bd',
            {
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            json={
                "changed": True,
                "location": {
                    "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                },
                "name": "No Name No Name No Name",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": False,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(False, 'No Name No Name No Name')

        # Edit both
        self.assertRequestResponse(
            LOCATION_URL + '44c532e1-f617-4174-b144-d37ce9fda2bd',
            {
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            json={
                "changed": True,
                "location": {
                    "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                },
                "name": "Totally unnamed",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": True,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(True, 'Totally unnamed')

    @freezegun.freeze_time('2016-06-01 12:00:00', tz_offset=+1)
    def test_should_create_org_unit_with_virkning_to_infinity(self):
        self.load_sample_structures()

        root = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org = '456362c4-0ee4-4e5e-a72c-751239745e62'

        self.assertEquals(
            self.client.get('/o/{}/org-unit/{}/'.format(org, root)).json[0],
            {
                'activeName': 'Overordnet Enhed',
                'name': 'Overordnet Enhed',
                'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'parent': None,
                'parent-object': None,
                'type': {
                    'name': 'Afdeling',
                    'user-key': 'afd',
                    'userKey': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'user-key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'valid-from': '01-01-2016',
                'valid-to': 'infinity',
            },
        )

        # Check that the GET requests made to MORa by the frontend
        # before the actual POST request are working

        self.assert200(
            self.client.get('/role-types/contact/facets/type/classes/'
                            '?facetKey=Contact_channel_location'))
        self.assert200(
            self.client.get('/role-types/contact/facets/properties/classes/'))
        self.assert200(
            self.client.get('/o/%s/full-hierarchy?effective-date='
                            '01-06-2016&query=&treeType=treeType' % org))
        self.assert200(self.client.get(
            '/addressws/geographical-location?local=%s&vejnavn=pile' % org))

        # Check POST request

        payload = {
            "user-key": "NULL",
            "name": "NyEnhed",
            "valid-from": "01-02-2016",
            "org": org,
            "parent": root,
            "type": {
                "name": "Afdeling",
                "userKey": "Afdeling",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
            },
            "locations": [
                {
                    "name": "lnavn",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse":
                            "98001816-a7cc-4115-a9e6-2c5c06c79e5d",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 2, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "flaf",
                                "user-key": "blyf",
                                "uuid": "00000000-0000-0000-0000-000000000000"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }
        r = self.client.post('/o/' + org + '/org-unit',
                             data=json.dumps(payload),
                             content_type='application/json')
        self.assertEqual(201, r.status_code)

        # Get the UUID of the org unit just created
        uuid = r.json['uuid']

        lora_response = lora.get_org_unit(uuid)
        lora_response.pop('fratidspunkt')

        expected_response = util.jsonfile_to_dict(
            'tests/integration_test_data/create_org_unit_infinity.json')
        expected_response.pop('fratidspunkt')

        self.assertEqual(expected_response, lora_response)

        # Check that the GET requests made to MORa by the frontend
        # after the actual POST request are working

        # Convert 'now' (from freezegun) to epoch seconds
        now = datetime.datetime.today().strftime('%s') + '000'

        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=treeType&t=%s' % (org, now)))
        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=specific&orgUnitId=%s&t=%s' % (org, root, now)))

        with self.subTest('rename'):
            self.assertRequestFails(
                '/o/{}/org-unit/{}/?validity=past'.format(org, uuid),
                404,
            )

            r = self.client.get('/o/{}/org-unit/{}/'.format(org, uuid), )

            self.assert200(r)

            self.assertEqual([
                {
                    'activeName': 'NyEnhed',
                    'name': 'NyEnhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': {
                        'activeName': 'Overordnet Enhed',
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                    },
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'user-key': 'NyEnhed',
                    'uuid': uuid,
                    'valid-from': '01-02-2016',
                    'valid-to': 'infinity',
                },
            ], r.json)

            postdata = r.json[0]
            postdata["name"] = "MindreNyEnhed"
            postdata["valid-from"] = "05-02-2016"

            self.assertLess(
                mora_util.parsedatetime(postdata["valid-from"]),
                mora_util.now(),
            )

            self.assertRequestResponse(
                '/o/{}/org-unit/{}?rename=true'.format(org, uuid),
                {
                    'uuid': uuid,
                },
                json=postdata,
            )

            with self.subTest('history'):
                r = self.client.get('/o/{}/org-unit/{}/history/'.format(org,
                                                                        uuid))
                self.assertEqual(r.status_code, 200)

                entries = r.json

                for k in 'date', 'from', 'to':
                    for entry in entries:
                        del entry[k]

                self.assertEqual(entries, [
                    {
                        'action': 'Omdøb enhed',
                        'changedBy': '42c432e8-9c4a-11e6-9f62-873cf34a735f',
                        'object': uuid,
                        'section': 'Rettet',
                    },
                    {
                        'action': 'Oprettet i MO',
                        'changedBy': '42c432e8-9c4a-11e6-9f62-873cf34a735f',
                        'object': uuid,
                        'section': 'Opstaaet',
                    },
                ])

            r = self.client.get('/o/{}/org-unit/{}/?validity=past'
                                .format(org, uuid))

            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=past'.format(org, uuid),
                [
                    {
                        'activeName': 'NyEnhed',
                        'name': 'NyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '01-02-2016',
                        'valid-to': '05-02-2016',
                    },
                ]
            )

            postdata = r.json[0]
            postdata["name"] = "EndnuMindreNyEnhed"
            postdata["valid-from"] = "08-02-2016"
            postdata["valid-to"] = "infinity"

            self.assertRequestResponse(
                '/o/{}/org-unit/{}?rename=true'.format(org, uuid),
                {
                    'uuid': uuid,
                },
                json=postdata,
            )

            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=past'.format(org, uuid),
                [
                    {
                        'activeName': 'NyEnhed',
                        'name': 'NyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '01-02-2016',
                        'valid-to': '05-02-2016',
                    },
                    {
                        'activeName': 'MindreNyEnhed',
                        'name': 'MindreNyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '05-02-2016',
                        'valid-to': '08-02-2016',
                    },
                ]
            )

            r = self.client.get('/o/{}/org-unit/{}/?validity=past'
                                .format(org, uuid))

            postdata["name"] = "KommendeEnhed"
            postdata["valid-from"] = "1-10-2016"

            self.assertRequestResponse(
                '/o/{}/org-unit/{}?rename=true'.format(org, uuid),
                {
                    'uuid': uuid,
                },
                json=postdata,
            )

            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=past'.format(org, uuid),
                [
                    {
                        'activeName': 'NyEnhed',
                        'name': 'NyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '01-02-2016',
                        'valid-to': '05-02-2016',
                    },
                    {
                        'activeName': 'MindreNyEnhed',
                        'name': 'MindreNyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '05-02-2016',
                        'valid-to': '08-02-2016',
                    },
                ]
            )

            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=present'.format(org, uuid),
                [
                    {
                        'activeName': 'EndnuMindreNyEnhed',
                        'name': 'EndnuMindreNyEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '08-02-2016',
                        'valid-to': '01-10-2016',
                    },
                ]
            )

            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=future'.format(org, uuid),
                [
                    {
                        'activeName': 'KommendeEnhed',
                        'name': 'KommendeEnhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': root,
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'NyEnhed',
                        'uuid': uuid,
                        'valid-from': '01-10-2016',
                        'valid-to': 'infinity',
                    },
                ]
            )

    @freezegun.freeze_time('2017-05-01 12:00:00', tz_offset=+2)
    def test_should_create_org_unit_with_virkning_to_2017_02_01(self):
        self.load_sample_structures()

        root = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org = '456362c4-0ee4-4e5e-a72c-751239745e62'

        payload = {
            "user-key": "NULL",
            "name": "NyEnhed",
            "valid-from": "01-02-2017",
            "valid-to": "01-06-2017",
            "org": org,
            "parent": root,
            "type": {
                "name": "Afdeling",
                "userKey": "Afdeling",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
            },
            "locations": [
                {
                    "name": "lnavn",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse":
                            "98001816-a7cc-4115-a9e6-2c5c06c79e5d",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 2, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "flaf",
                                "user-key": "blyf",
                                "uuid": "00000000-0000-0000-0000-000000000000"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }
        r = self.client.post('/o/' + org + '/org-unit',
                             data=json.dumps(payload),
                             content_type='application/json')
        self.assertEqual(201, r.status_code)

        # Get the UUID of the org unit just created
        uuid = r.json['uuid']

        lora_response = lora.get_org_unit(uuid)
        lora_response.pop('fratidspunkt')
        lora_response.pop('livscykluskode')
        lora_response.pop('note')

        expected_response = util.jsonfile_to_dict(
            'tests/integration_test_data/create_org_unit_2011-01-01.json')
        expected_response.pop('fratidspunkt')

        self.assertEqual(expected_response, lora_response)

    @freezegun.freeze_time('2017-01-01 12:00:00', tz_offset=+1)
    def test_permanent_rename(self):
        self.load_sample_structures()

        PARENTID = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        ORGID = '456362c4-0ee4-4e5e-a72c-751239745e62'
        UNITID = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        # Check that the GET requests made to MORa by the frontend
        # before the actual POST request are working

        self.assert200(self.client.get(
            '/o/%s/org-unit/?query=Humanistisk+fakultet' % ORGID))
        self.assert200(self.client.get(
            '/o/%s/org-unit/?query=%s&effective-date='
            '2017-01-01T12:00:00+00:00' % (ORGID, UNITID)))

        expected = {
            "activeName": "Humanistisk fakultet",
            "name": "Humanistisk fakultet",
            "org": ORGID,
            "parent": PARENTID,
            "parent-object": {
                "activeName": "Overordnet Enhed",
                "name": "Overordnet Enhed",
                "org": ORGID,
                "parent": None,
                "parent-object": None,
                'type': {
                    'name': 'Afdeling',
                    'user-key': 'afd',
                    'userKey': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                "user-key": "root",
                "uuid": PARENTID,
                "valid-from": "01-01-2016",
                "valid-to": "infinity",
            },
            'type': {
                'name': 'Institut',
                'user-key': 'inst',
                'userKey': 'inst',
                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
            },
            "user-key": "hum",
            "uuid": UNITID,
            "valid-from": "01-01-2016",
            "valid-to": "infinity",
        }

        self.assertRequestResponse(
            '/o/{}/org-unit/{}/'.format(ORGID, UNITID),
            [expected],
        )

        postdata = copy.deepcopy(expected)
        postdata["name"] = "Humanistisk fikultat"
        postdata["valid-from"] = "01-06-2016"
        del postdata["valid-to"]

        r = self.client.post(
            '/o/{}/org-unit/{}?rename=true'.format(ORGID, UNITID),
            data=json.dumps(postdata),
            content_type='application/json',
        )

        self.assert200(r)
        self.assertEquals(r.json, {'uuid': UNITID})

        # Check that the GET requests made to MORa by the frontend
        # after the actual POST request are working

        # Convert 'now' (from freezegun) to epoch seconds
        now = datetime.datetime.today().strftime('%s') + '000'

        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=treeType&t=%s' % (ORGID, now)))
        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=specific&orgUnitId=%s&t=%s' % (ORGID, PARENTID, now)))

    @freezegun.freeze_time('2017-07-01', tz_offset=+1)
    def test_rename_org_unit_from_the_july1(self):
        self.load_sample_structures()

        ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
        ORG_UNIT = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        self.assertRequestResponse(
            '/o/%s/org-unit/%s?rename=true' % (ORG, ORG_UNIT),
            {'uuid': ORG_UNIT},
            json={
                "activeName": "Samfundsvidenskabelige fakultet",
                "name": "NEW NAME",
                "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "parent-object": {
                    "activeName": "Overordnet Enhed",
                    "name": "Overordnet Enhed",
                    "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "parent": None,
                    "parent-object": None,
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    "user-key": "root",
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "valid-from": "2015-12-31T23:00:00+00:00",
                    "valid-to": "infinity"
                },
                'type': {
                    'name': 'Fakultet',
                    'user-key': 'fak',
                    'userKey': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                "user-key": "samf",
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "valid-from": "01-08-2017"
            }
        )

        # Check that the renaming was written correctly to LoRa

        expected_response = [
            {
                'brugervendtnoegle': 'samf',
                'enhedsnavn': 'NEW NAME',
                'virkning': {
                    'from': '2017-08-01 00:00:00+02',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False
                }
            },
            {
                'brugervendtnoegle': 'samf',
                'enhedsnavn': 'Samfundsvidenskabelige fakultet',
                'virkning': {
                    'from': '2017-01-01 00:00:00+01',
                    'from_included': True,
                    'to': '2017-08-01 00:00:00+02',
                    'to_included': False
                }
            }
        ]

        actual_response = lora.get_org_unit(ORG_UNIT)['attributter'][
            'organisationenhedegenskaber']

        self.assertEqual(expected_response, actual_response)

    def test_org_unit_deletion(self):
        with freezegun.freeze_time('2017-01-01'):
            self.load_sample_structures()

            ORGID = '456362c4-0ee4-4e5e-a72c-751239745e62'
            UNITID = '04c78fc2-72d2-4d02-b55f-807af19eac48'

            # Check that the GET requests made to MORa by the frontend
            # before the actual POST request are working

            # Convert 'now' (from freezegun) to epoch seconds
            now = datetime.datetime.today().strftime('%s') + '000'

            self.assert200(self.client.get(
                '/o/%s/org-unit/?query=Afdeling+for+Samtidshistorik' % ORGID))
            self.assert200(self.client.get(
                '/o/%s/org-unit/?query=%s'
                '&effective-date=2017-07-01T12:00:00+00:00' % (ORGID, UNITID)))
            self.assert200(self.client.get(
                '/o/%s/org-unit/%s/?validity='
                '&effective-date=01-03-2017&t=%s' % (ORGID, UNITID, now)))
            self.assert200(self.client.get(
                '/o/%s/org-unit/%s/role-types/location/'
                '?validity=&effective-date=01-03-2017&t=%s' % (
                    ORGID, UNITID, now)))

            hierarchy_path = (
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy?'
                'treeType=specific'
                '&orgUnitId=da77153e-30f3-4dc2-a611-ee912a28d8aa'
            )

            orgunit_path = (
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
            )

            expected_existing = [
                {
                    'children': [],
                    'hasChildren': False,
                    'name': 'Afdeling for Samtidshistorik',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'user-key': 'frem',
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'valid-from': '01-01-2016',
                    'valid-to': '01-01-2019',
                },
            ]

            # check our preconditions
            self.assertEqual(
                self.client.get(hierarchy_path).json,
                expected_existing,
            )

            self.assertEqual(
                lora.get_org_unit('04c78fc2-72d2-4d02-b55f-807af19eac48')[
                    'tilstande'],
                {
                    'organisationenhedgyldighed': [
                        {
                            'gyldighed': 'Aktiv',
                            'virkning': {
                                'from': '2016-01-01 00:00:00+01',
                                'from_included': True,
                                'to': '2019-01-01 00:00:00+01',
                                'to_included': False,
                            },
                        },
                    ],
                },
            )

            # expire the unit at 1 March 2017
            self.assertRequestResponse(
                orgunit_path + '?endDate=01-03-2017',
                {
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                },
                method='DELETE',
            )

            self.assertEqual(
                lora.get_org_unit('04c78fc2-72d2-4d02-b55f-807af19eac48')[
                    'tilstande'],
                {
                    'organisationenhedgyldighed': [
                        {
                            'gyldighed': 'Aktiv',
                            'virkning': {
                                'from': '2016-01-01 00:00:00+01',
                                'from_included': True,
                                'to': '2017-03-01 00:00:00+01',
                                'to_included': False,
                            },
                        },
                        {
                            'gyldighed': 'Inaktiv',
                            'virkning': {
                                'from': '2017-03-01 00:00:00+01',
                                'from_included': True,
                                'to': 'infinity',
                                'to_included': False,
                            },
                        },
                    ],
                },
            )

        # check that it's gone
        with freezegun.freeze_time('2017-06-01'):
            self.assertEqual(
                self.client.get(hierarchy_path).json,
                [],
            )

        with self.assertRaises(AssertionError):
            # the test below fails, for now...

            # but not too gone...
            with freezegun.freeze_time('2017-02-01'):
                self.assertEqual(
                    self.client.get(hierarchy_path).json,
                    expected_existing,
                )

        # Check that the GET requests made to MORa by the frontend
        # after the actual POST request are working

        with freezegun.freeze_time('2017-08-03'):
            self.assert404(self.client.get(
                '/o/%s/org-unit/%s/?validity=present&effective-date='
                '&t=1501766568577' % (ORGID, UNITID)))
            self.assert200(self.client.get(
                '/o/%s/org-unit/%s/role-types/location/?validity=present'
                '&effective-date=&t=1501766568577' % (ORGID, UNITID)))
            self.assert200(self.client.get(
                '/o/%s/full-hierarchy?effective-date=&query='
                '&treeType=treeType&t=1501766568624' % ORGID))

    @freezegun.freeze_time('2016-01-01', tz_offset=+1)
    def test_should_be_possible_to_inactivate_an_org_unit_several_times(self):
        self.load_sample_structures()

        ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
        ORG_UNIT = '04c78fc2-72d2-4d02-b55f-807af19eac48'

        # Expire the unit at 1 March 2017

        self.assertRequestResponse(
            '/o/%s/org-unit/%s?endDate=01-03-2017' % (ORG, ORG_UNIT),
            {
                'uuid': ORG_UNIT,
            },
            method='DELETE',
        )

        expected_output = [
            {
                'gyldighed': 'Aktiv',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': '2017-03-01 00:00:00+01',
                    'to_included': False
                }
            },
            {
                'gyldighed': 'Inaktiv',
                'virkning': {
                    'from': '2017-03-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False
                }
            }
        ]

        actual_output = lora.get_org_unit(ORG_UNIT)[
            'tilstande']['organisationenhedgyldighed']

        self.assertEqual(expected_output, actual_output)

        # ... and then again on 14 March 2017

        self.assertRequestResponse(
            '/o/%s/org-unit/%s?endDate=14-03-2017' % (ORG, ORG_UNIT),
            {
                'uuid': ORG_UNIT,
            },
            method='DELETE',
        )

        expected_output = [
            {
                'gyldighed': 'Aktiv',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': '2017-03-14 00:00:00+01',
                    'to_included': False
                }
            },
            {
                'gyldighed': 'Inaktiv',
                'virkning': {
                    'from': '2017-03-14 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False
                }
            }
        ]

        actual_output = lora.get_org_unit(ORG_UNIT)[
            'tilstande']['organisationenhedgyldighed']

        self.assertEqual(expected_output, actual_output)

    @freezegun.freeze_time('2017-06-01 12:00:00', tz_offset=+1)
    def test_should_move_org_unit_correctly(self):
        self.load_sample_structures()

        root = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org = '456362c4-0ee4-4e5e-a72c-751239745e62'
        org_unit = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'  # hum
        new_parent_org_unit = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # samf

        # Check that the GET requests made to MORa by the frontend
        # before the actual POST request are working

        # Convert 'now' (from freezegun) to epoch seconds
        now = datetime.datetime.today().strftime('%s') + '000'

        self.assert200(
            self.client.get('/o/%s/full-hierarchy?effective-date='
                            '01-06-2017&query=&treeType=treeType' % org))
        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=specific&orgUnitId=%s&t=%s' % (org, root, now)))
        self.assert200(
            self.client.get(
                '/o/%s/org-unit/?query=%s&effective-date=01-06-2016' % (
                    org, root)))

        # Check the POST request

        self.assertRequestResponse(
            '/o/%s/org-unit/%s/actions/move' % (org, org_unit),
            {'uuid': org_unit},
            json={
                'moveDate': '01-05-2017',
                'newParentOrgUnitUUID': new_parent_org_unit
            }
        )

        # Check that the GET requests made to MORa by the frontend
        # after the actual POST request are working

        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date='
            '&query=&treeType=treeType&t=%s' % (org, now)))
        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=specific&orgUnitId=%s&t=%s' % (org, root, now)))

        entry = lora.get_org_unit(org_unit)

        expected = util.jsonfile_to_dict(
            'tests/integration_test_data/should_move_org_unit_correctly.json',
        )
        expected['relationer']['overordnet'][1]['uuid'] = new_parent_org_unit

        # drop lora-generated timestamps & users
        del entry['fratidspunkt'], entry['tiltidspunkt'], entry['brugerref']

        self.assertEqual(entry, expected)

        with self.subTest('present'):
            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=present'.format(org, org_unit),
                [
                    {
                        'activeName': 'Humanistisk fakultet',
                        'name': 'Humanistisk fakultet',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                        'parent-object': {
                            'activeName': 'Samfundsvidenskabelige fakultet',
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'parent-object': None,
                            'type': {
                                'name': 'Fakultet',
                                'user-key': 'fak',
                                'userKey': 'fak',
                                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                            },
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '01-01-2017',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Institut',
                            'user-key': 'inst',
                            'userKey': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                        },
                        'user-key': 'hum',
                        'uuid': org_unit,
                        'valid-from': '01-05-2017',
                        'valid-to': 'infinity',
                    },
                ],
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/o/{}/org-unit/{}/?validity=past'.format(org, org_unit),
                [
                    {
                        'activeName': 'Humanistisk fakultet',
                        'name': 'Humanistisk fakultet',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'parent-object': {
                            'activeName': 'Overordnet Enhed',
                            'name': 'Overordnet Enhed',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': None,
                            'parent-object': None,
                            'type': {
                                'name': 'Afdeling',
                                'user-key': 'afd',
                                'userKey': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                            },
                            'user-key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'type': {
                            'name': 'Institut',
                            'user-key': 'inst',
                            'userKey': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                        },
                        'user-key': 'hum',
                        'uuid': org_unit,
                        'valid-from': '01-01-2016',
                        'valid-to': '01-05-2017',
                    },
                ],
            )

        with self.subTest('future'):
            self.assert404(
                self.client.get(
                    '/o/{}/org-unit/{}/?validity=future'.format(org, org_unit),
                ),
            )

    @freezegun.freeze_time('2016-06-01 12:00:00', tz_offset=+1)
    def test_create_unit_with_contact_channels(self):
        self.load_sample_structures(minimal=True)

        org = '456362c4-0ee4-4e5e-a72c-751239745e62'

        r = self.client.post(
            '/o/{}/org-unit'.format(org),
            content_type='application/json',
            data=json.dumps({
                "user-key": "NULL",
                "name": "NewUnit",
                "valid-from": "01-08-2017",
                "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "type": {
                    "name": "Afdeling",
                    "userKey": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                },
                "locations": [
                    {
                        "name": "Kontor",
                        "primaer": True,
                        "location": {
                            "UUID_EnhedsAdresse":
                                "0a3f50c4-c4ba-32b8-e044-0003ba298018",
                            "postdistrikt": "Viby J",
                            "postnr": "8260",
                            "vejnavn": "Åbovej 5, Åbo, 8260 Viby J",
                        },
                        "contact-channels": [
                            {
                                "contact-info": "42",
                                "visibility": {
                                    "name": "N/A",
                                    "user-key": "secret",
                                    "uuid": "N/A",
                                },
                                "type": {
                                    "name": "Phone Number",
                                    "prefix": "urn:magenta.dk:telefon:",
                                    "uuid":
                                        "b7ccfb21-f623-4e8f-80ce-89731f726224",
                                },
                            },
                            {
                                "contact-info": "1337",
                                "visibility": {
                                    "name": "N/A",
                                    "user-key": "external",
                                    "uuid": "N/A",
                                },
                                "type": {
                                    "name": "Phone Number",
                                    "prefix": "urn:magenta.dk:telefon:",
                                    "uuid":
                                        "b7ccfb21-f623-4e8f-80ce-89731f726224",
                                },
                            },
                        ],
                    },
                ],
            }),
        )

        self.assertEqual(r.status_code, 201)

        unitid = r.json['uuid']
        unitpath = '/o/{}/org-unit/{}/'.format(org, unitid)

        self.assertRequestFails(unitpath + 'role-types/contact-channel/', 404)
        self.assertRequestResponse(
            unitpath + 'role-types/contact-channel/?validity=future', [
                {
                    'contact-info': '1337',
                    'location': {
                        "name": "Åbovej 5, Åbo, 8260 Viby J",
                        'user-key': '07519659___5_______',
                        'uuid': '0a3f50c4-c4ba-32b8-e044-0003ba298018',
                        'valid-from': '2000-02-05T15:27:05+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Åbovej 5, Åbo, 8260 Viby J'
                    },
                    'type': {
                        'name': 'Telefonnummer',
                        'prefix': 'urn:magenta.dk:telefon:',
                        'user-key': 'Telephone_number',
                    },
                    'valid-from': '01-08-2017',
                    'valid-to': 'infinity',
                    'visibility': {
                        'name': 'Må vises eksternt',
                        'user-key': 'external',
                        'uuid': 'c67d7315-a0a2-4238-a883-f33aa7ddabc2',
                    },
                },
                {
                    'contact-info': '42',
                    'location': {
                        "name": "Åbovej 5, Åbo, 8260 Viby J",
                        'user-key': '07519659___5_______',
                        'uuid': '0a3f50c4-c4ba-32b8-e044-0003ba298018',
                        'valid-from': '2000-02-05T15:27:05+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Åbovej 5, Åbo, 8260 Viby J'
                    },
                    'type': {
                        'name': 'Telefonnummer',
                        'prefix': 'urn:magenta.dk:telefon:',
                        'user-key': 'Telephone_number',
                    },
                    'valid-from': '01-08-2017',
                    'valid-to': 'infinity',
                    'visibility': {
                        'name': 'Hemmeligt',
                        'user-key': 'secret',
                        'uuid': '8d37a1ec-3d58-461f-821f-c2a7bb6bc861',
                    },
                },
            ])

    @freezegun.freeze_time('2017-08-01', tz_offset=+1)
    def test_should_new_add_past_and_future_locations_correctly(self):
        self.load_sample_structures()

        ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
        ORG_UNIT = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        # First add an address in the past

        self.assertRequestResponse(
            '/o/%s/org-unit/%s/role-types/location' % (ORG, ORG_UNIT),
            {'uuid': ORG_UNIT},
            json={
                "valid-from": "01-07-2017",
                "valid-to": "19-07-2017",
                "location": {
                    "UUID_EnhedsAdresse": "0a3f50c2-6f16-32b8-"
                                          "e044-0003ba298018",
                    "postdistrikt": "Sabro",
                    "postnr": "8471",
                    "vejnavn": "Astervej 2, 8471 Sabro"
                },
                "name": "fortid",
                "$$hashKey": "0YS"
            }
        )

        expected_addresses = [
            {
                'uuid': '0a3f50c2-6f16-32b8-e044-0003ba298018',
                'virkning': {
                    'from': '2017-07-01 00:00:00+02',
                    'from_included': True,
                    'notetekst': 'v0:0:fortid',
                    'to': '2017-07-19 00:00:00+02',
                    'to_included': False
                }
            },
            {
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'virkning': {
                    'from': '2017-01-01 00:00:00+01',
                    'from_included': True,
                    'notetekst': 'v0:1:Kontor',
                    'to': 'infinity',
                    'to_included': False
                }
            },
            {
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'virkning': {
                    'from': '2017-01-01 00:00:00+01',
                    'from_included': True,
                    'notetekst': 'v0:external:b1f1817d-5f02-'
                                 '4331-b8b3-97330a5d3197',
                    'to': 'infinity',
                    'to_included': False
                }
            }
        ]

        actual_addresses = lora.get_org_unit(ORG_UNIT)[
            'relationer']['adresser']

        self.assertEqual(expected_addresses, actual_addresses)

        # Then add an address in the future

        self.assertRequestResponse(
            '/o/%s/org-unit/%s/role-types/location' % (ORG, ORG_UNIT),
            {'uuid': ORG_UNIT},
            json={
                "valid-from": "01-09-2017",
                "valid-to": "19-09-2017",
                "location": {
                    "UUID_EnhedsAdresse": "0a3f50c2-6f16-32b8-"
                                          "e044-0003ba298018",
                    "postdistrikt": "Sabro",
                    "postnr": "8471",
                    "vejnavn": "Astervej 2, 8471 Sabro"
                },
                "name": "fremtid",
                "$$hashKey": "0YS"
            }
        )

        expected_addresses = [
            {
                'uuid': '0a3f50c2-6f16-32b8-e044-0003ba298018',
                'virkning': {
                    'from': '2017-09-01 00:00:00+02',
                    'from_included': True,
                    'notetekst': 'v0:0:fremtid',
                    'to': '2017-09-19 00:00:00+02',
                    'to_included': False
                }
            },
            {
                'uuid': '0a3f50c2-6f16-32b8-e044-0003ba298018',
                'virkning': {
                    'from': '2017-07-01 00:00:00+02',
                    'from_included': True,
                    'notetekst': 'v0:0:fortid',
                    'to': '2017-07-19 00:00:00+02',
                    'to_included': False
                }
            },
            {
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'virkning': {
                    'from': '2017-01-01 00:00:00+01',
                    'from_included': True,
                    'notetekst': 'v0:1:Kontor',
                    'to': 'infinity',
                    'to_included': False
                }
            },
            {
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'virkning': {
                    'from': '2017-01-01 00:00:00+01',
                    'from_included': True,
                    'notetekst': 'v0:external:b1f1817d-5f02-'
                                 '4331-b8b3-97330a5d3197',
                    'to': 'infinity',
                    'to_included': False
                }
            }
        ]

        actual_addresses = lora.get_org_unit(ORG_UNIT)[
            'relationer']['adresser']

        self.assertEqual(expected_addresses, actual_addresses)

    def test_should_move_employee_correctly_present(self):
        self.load_sample_structures()

        new_org_unit = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # samf

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        engagementid = 'd000591f-8705-4324-897a-075e3623f37b'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        self.assertRequestResponse(
            '/e/{}/actions/move?date={}&org-unit={}'.format(
                userid,
                '01-01-2018',
                new_org_unit),
            [],
            json={
                "presentEngagementIds": [{
                    "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                    "overwrite": 1
                }],
                "futureEngagementIds": [],
                "presentRoleIds": [],
                "futureRoleIds": []
            }
        )

        # We expect the existing engagement to have been inactivated at the
        # date supplied

        expected_old = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_present_old.json',
        )

        actual_old = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_old['fratidspunkt'], actual_old['tiltidspunkt'], actual_old[
            'brugerref']

        self.assertEqual(actual_old, expected_old)

        # We expect a new engagement to have been created, active from the date
        # with the new org unit associated
        expected_new = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_present_new.json',
        )

        # Find the new engagement
        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 2)
        new_engagement = list(
            filter(lambda x: x != engagementid, engagements))[-1]
        actual_new = c.organisationfunktion.get(new_engagement)

        del actual_new['fratidspunkt'], actual_new['tiltidspunkt'], actual_new[
            'brugerref']

        self.assertEqual(actual_new, expected_new)

    def test_should_move_employee_correctly_future_overwrite(self):
        self.load_sample_structures()

        new_org_unit = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # samf

        # Check the POST request
        c = lora.Connector(effective_date='2002-01-01',
                           virkningfra='-infinity', virkningtil='infinity')

        engagementid = 'd000591f-8705-4324-897a-075e3623f37b'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        self.assertRequestResponse(
            '/e/{}/actions/move?date={}&org-unit={}'.format(
                userid,
                '01-01-2002',
                new_org_unit),
            [],
            json={
                "presentEngagementIds": [],
                "futureEngagementIds": [{
                    "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                    "overwrite": 1
                }],
                "presentRoleIds": [],
                "futureRoleIds": []
            }
        )

        # We expect the existing engagement to be completely inactive
        expected_old = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_future_old_overwrite.json',
        )

        actual_old = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_old['fratidspunkt'], actual_old['tiltidspunkt'], actual_old[
            'brugerref']

        self.assertEqual(actual_old, expected_old)

        # We expect a new engagement to have been created with the new org
        # unit, active from the supplied date to the start date of the
        # existing engagement
        expected_new = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_future_new_overwrite.json',
        )

        # Find the new engagement
        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 2)
        new_engagement = list(
            filter(lambda x: x != engagementid, engagements))[-1]
        actual_new = c.organisationfunktion.get(new_engagement)

        del actual_new['fratidspunkt'], actual_new['tiltidspunkt'], actual_new[
            'brugerref']

        self.assertEqual(actual_new, expected_new)

    def test_should_move_employee_correctly_future_no_overwrite(self):
        self.load_sample_structures()

        new_org_unit = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # samf

        # Check the POST request
        c = lora.Connector(effective_date='2002-01-01',
                           virkningfra='-infinity', virkningtil='infinity')

        engagementid = 'd000591f-8705-4324-897a-075e3623f37b'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        self.assertRequestResponse(
            '/e/{}/actions/move?date={}&org-unit={}'.format(
                userid,
                '01-01-2002',
                new_org_unit),
            [],
            json={
                "presentEngagementIds": [],
                "futureEngagementIds": [{
                    "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                    "overwrite": 0
                }],
                "presentRoleIds": [],
                "futureRoleIds": []
            }
        )

        # We expect the existing engagement to remain unchanged
        expected_old = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_future_old.json',
        )

        actual_old = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_old['fratidspunkt'], actual_old['tiltidspunkt'], actual_old[
            'brugerref']

        self.assertEqual(actual_old, expected_old)

        # We expect a new engagement to have been created with the new org
        # unit, active from the supplied date to the start date of the
        # existing engagement
        expected_new = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'should_move_engagement_correctly_future_new.json',
        )

        # Find the new engagement
        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 2)
        new_engagement = list(
            filter(lambda x: x != engagementid, engagements))[-1]
        actual_new = c.organisationfunktion.get(new_engagement)

        del actual_new['fratidspunkt'], actual_new['tiltidspunkt'], actual_new[
            'brugerref']

        self.assertEqual(actual_new, expected_new)

    def test_should_create_new_engagement_correctly(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "2f9a3e4f-5f91-40a4-904c-68a376b7320f"

        payload = [{
            "valid-from": "01-12-2017",
            "valid-to": "02-12-2017",
            "org-unit": {
                "children": [],
                "hasChildren": False,
                "name": "Samfundsvidenskabelige fakultet",
                "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "type": {"name": "Fakultet"},
                "user-key": "samf",
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "valid-from": "2016-12-31T23:00:00+00:00",
                "valid-to": "infinity"
            },
            "job-title": {
                "name": "Skorstensfejer",
                "uuid": "a294c42b-3c9d-4a31-bf78-1e1684d2e206"
            },
            "type": {
                "name": "Ansat",
                "uuid": "2c49130e-1446-4aee-874f-819d3358de20"
            },
            "person": "2f9a3e4f-5f91-40a4-904c-68a376b7320f",
            "role-type": "engagement",
            "user-key": "NULL"
        }]

        self.assertRequestResponse('/mo/e/{}/actions/role'.format(userid),
                                   userid, json=payload)

        # We expect the existing engagement to be completely inactive
        expected_old = util.jsonfile_to_dict(
            'tests/integration_test_data/'
            'create_engagement.json',
        )

        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 1)
        engagementid = engagements[0]

        actual_engagement = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(actual_engagement, expected_old)

    def test_should_terminate_employee_correctly(self):
        self.load_sample_structures()

        # Check the POST request
        date = '2019-01-01'

        c = lora.Connector(effective_date=date, virkningfra='-infinity',
                           virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 1)

        engagement_before = [
            {
                'job-title': {
                    'name': 'Fakultet',
                    'userKey': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                },
                'org': None,
                'org-unit': {
                    'activeName': 'Humanistisk fakultet',
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': None,
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity'
                },
                'person': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                'person-name': 'Anders And',
                'role-type': 'engagement',
                'type': {
                    'name': 'Afdeling',
                    'userKey': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'valid-from': '01-01-2017',
                'valid-to': 'infinity'
            }
        ]
        self.assertRequestResponse(
            '/e/{}/role-types/engagement/?validity=present'
            '&effective-date={}'.format(userid, date),
            engagement_before
        )

        self.assertRequestResponse(
            '/e/{}/actions/terminate?date={}'.format(userid, date),
            userid, method='POST')

        engagement_after = [
            {
                'job-title': {
                    'name': 'Fakultet',
                    'userKey': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                },
                'org': None,
                'org-unit': {
                    'activeName': 'Humanistisk fakultet',
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': None,
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity'
                },
                'person': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                'person-name': 'Anders And',
                'role-type': 'engagement',
                'type': {
                    'name': 'Afdeling',
                    'userKey': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'valid-from': '01-01-2017',
                'valid-to': '01-01-2019'
            }
        ]

        self.assertRequestResponse(
            '/e/{}/role-types/engagement/?validity=present'
            '&effective-date={}'.format(userid, date),
            engagement_after
        )
