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
                        'user-key': '07515902___1_______',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                    },
                    'name': '',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': False,
                    'role-type': 'location',
                    'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

        self.assertRequestResponse(
            LOCATION_URL,
            [
                {
                    'location': {
                        'user-key': '07515902___1_______',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                    },
                    'name': '',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': False,
                    'role-type': 'location',
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
                "name": "",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": False,
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
                        'user-key': '07519651__15_______',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                        'vejnavn': 'Åbogade 15, 8200 Aarhus N',
                    },
                    'name': '',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': False,
                    'role-type': 'location',
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
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                    },
                ],
            )

        # Initial sanity check
        check(False, '')

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
                "name": "",
                "org-unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "primaer": True,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(True, '')

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
                "primaer": True,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(True, 'No Name No Name No Name')

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
                "primaer": False,
                "role-type": "location",
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "valid-from": "01-01-2016",
                "valid-to": "infinity"
            },
        )

        check(False, 'Totally unnamed')

    @freezegun.freeze_time('2016-06-01 12:00:00', tz_offset=+1)
    def test_should_create_org_unit_with_virkning_to_infinity(self):
        self.load_sample_structures()

        root = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org = '456362c4-0ee4-4e5e-a72c-751239745e62'

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
                                "name": "N/A",
                                "user-key": "N/A",
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

        lora_response = lora.organisationenhed.get(
            uuid=uuid, virkningfra='-infinity', virkningtil='infinity')
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
            r = self.client.get('/o/{}/org-unit/{}/'.format(org, uuid), )

            self.assert200(r)

            postdata = r.json[0]
            postdata["name"] = "MindreNyEnhed"
            postdata["valid-from"] = "05-02-2016"

            r = self.client.post(
                '/o/{}/org-unit/{}?rename=true'.format(org, uuid),
                data=json.dumps(postdata),
                content_type='application/json',
            )
            self.assert200(r)

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

    @freezegun.freeze_time('2010-06-01 12:00:00', tz_offset=+1)
    def test_should_create_org_unit_with_virkning_to_2011_01_01(self):
        self.load_sample_structures()

        root = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org = '456362c4-0ee4-4e5e-a72c-751239745e62'

        payload = {
            "user-key": "NULL",
            "name": "NyEnhed",
            "valid-from": "01-01-2010",
            "valid-to": "01-01-2011",
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
                                "name": "N/A",
                                "user-key": "N/A",
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

        lora_response = lora.organisationenhed(
            uuid=uuid, virkningtil='infinity')[0]['registreringer'][-1]
        lora_response.pop('fratidspunkt')

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
            "hasChildren": True,
            "name": "Humanistisk fakultet",
            "org": ORGID,
            "parent": PARENTID,
            "parent-object": {
                "activeName":
                    "Overordnet Enhed",
                "hasChildren": True,
                "name": "Overordnet Enhed",
                "org": ORGID,
                "parent": None,
                "parent-object": None,
                "type": {"name": "Afdeling"},
                "user-key": "root",
                "uuid": PARENTID,
                "valid-from": "01-01-2016",
                "valid-to": "infinity",
            },
            'type': {'name': 'Institut'},
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
                    'type': {'name': 'Afdeling'},
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'valid-from': '01-01-2016',
                    'valid-to': '01-01-2018',
                },
            ]

            # check our preconditions
            self.assertEqual(
                self.client.get(hierarchy_path).json,
                expected_existing,
            )

            self.assertEqual(
                lora.organisationenhed.get(
                    '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    virkningfra='-infinity', virkningtil='infinity',
                )['tilstande'],
                {
                    'organisationenhedgyldighed': [
                        {
                            'gyldighed': 'Aktiv',
                            'virkning': {
                                'from': '2016-01-01 00:00:00+01',
                                'from_included': True,
                                'to': '2018-01-01 00:00:00+01',
                                'to_included': False,
                            },
                        },
                        {
                            'gyldighed': 'Inaktiv',
                            'virkning': {
                                'from': '2018-01-01 00:00:00+01',
                                'from_included': True,
                                'to': 'infinity',
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
                lora.organisationenhed.get(
                    '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    virkningfra='-infinity', virkningtil='infinity',
                )['tilstande'],
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
                                'from': '-infinity',
                                'from_included': True,
                                'to': '2016-01-01 00:00:00+01',
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

        self.assert200(self.client.get(
            '/o/%s/org-unit/%s/?validity=present&effective-date='
            '&t=1501766568577' % (ORGID, UNITID)))
        self.assert200(self.client.get(
            '/o/%s/org-unit/%s/role-types/location/?validity=present'
            '&effective-date=&t=1501766568577' % (ORGID, UNITID)))
        self.assert200(self.client.get(
            '/o/%s/full-hierarchy?effective-date=&query='
            '&treeType=treeType&t=1501766568624' % ORGID))

    @freezegun.freeze_time('2016-06-01 12:00:00', tz_offset=+1)
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
                            '01-06-2016&query=&treeType=treeType' % org))
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
                'moveDate': '01-05-2016',
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
