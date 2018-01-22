#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import unittest
from mora.converters import writing


class TestOrgUnitRetypeOrUpdateStartdate(unittest.TestCase):
    maxDiff = None

    # FIXME
    @unittest.SkipTest
    @freezegun.freeze_time('2017-01-01')
    def test_should_retype_org_unit_correctly(self):
        frontend_req = {
            "activeName": "Aarhus Havn",
            "hasChildren": False,
            "name": "Aarhus Havn",
            "org": "59141156-ed0b-457c-9535-884447c5220b",
            "parent": "80945a5a-ca10-4470-a801-80c6edaf6341",
            "parent-object": {
                "activeName": "Aarhus Kommune",
                "hasChildren": True,
                "name": "Aarhus Kommune",
                "org": "59141156-ed0b-457c-9535-884447c5220b",
                "parent": None, "parent-object": None,
                "user-key": "ÅRHUS",
                "uuid": "80945a5a-ca10-4470-a801-80c6edaf6341",
                "valid-from": "2015-12-31 23:00:00+00",
                "valid-to": "infinity"
            },
            "user-key": "HAVNEN",
            "uuid": "20780e20-3faa-4dd7-9102-4f0583bb1092",
            "valid-from": "01-01-2010",
            "valid-to": "infinity",
            "$$hashKey": "04E",
            "type-updated": "",
            "type": {
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "changed": True,
        }
        expected_output = {
            'note': 'Ret enhedstype',
            'relationer': {
                'enhedstype': [
                    {
                        'virkning': {
                            'from': '2017-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                        'uuid': '0034fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                    }
                ]
            },
        }
        actual_output = writing.retype_org_unit(frontend_req)

        self.assertEqual(actual_output, expected_output,
                         'Unexpected output for retype org unit')

    def test_should_update_startdate_correctly(self):
        frontend_req = {
            "activeName": "Aarhus Havn",
            "hasChildren": False,
            "name": "Aarhus Havn",
            "org": "59141156-ed0b-457c-9535-884447c5220b",
            "parent": "4eec0c69-5d59-483c-ad40-4fb9d560d428",
            "parent-object": {
                "activeName": "Aarhus Kommune",
                "hasChildren": True,
                "name": "Aarhus Kommune",
                "org": "59141156-ed0b-457c-9535-884447c5220b",
                "parent": None,
                "parent-object": None,
                "type": {
                    "name": "Afdeling 003"
                },
                "user-key": "ÅRHUS",
                "uuid": "4eec0c69-5d59-483c-ad40-4fb9d560d428",
                "valid-from": "2015-12-31T23:00:00+00:00",
                "valid-to": "infinity"
            },
            "type": {
                "name": "Afdeling 933"
            }, "user-key": "HAVNEN",
            "uuid": "9352be59-30cd-404e-9d51-d3f2c8399782",
            "valid-from": "20-01-2016",
            "valid-to": "infinity",
            "$$hashKey": "1RH",
            "valid-from-updated": "2016-01-19T23:00:00.000Z",
            "changed": True
        }
        expected_output = {
            'note': 'Ret start dato',
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2016-01-20T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ]
            }
        }
        self.assertEqual(expected_output,
                         writing.retype_org_unit(frontend_req))

    # FIXME
    @unittest.SkipTest
    @freezegun.freeze_time('2017-07-31')
    def test_should_update_type_and_startdate_correctly(self):
        frontend_req = {
            "activeName": "Aarhus Havn",
            "hasChildren": False,
            "name": "Aarhus Havn",
            "org": "59141156-ed0b-457c-9535-884447c5220b",
            "parent": "4eec0c69-5d59-483c-ad40-4fb9d560d428",
            "parent-object": {
                "activeName": "Aarhus Kommune",
                "hasChildren": True,
                "name": "Aarhus Kommune",
                "org": "59141156-ed0b-457c-9535-884447c5220b",
                "parent": None,
                "parent-object": None,
                "type": {
                    "name": "Afdeling 003"
                },
                "user-key": "ÅRHUS",
                "uuid": "4eec0c69-5d59-483c-ad40-4fb9d560d428",
                "valid-from": "2015-12-31T23:00:00+00:00",
                "valid-to": "infinity"
            },
            "type": {
                "name": "Afdeling 933",
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "user-key": "HAVNEN",
            "uuid": "9352be59-30cd-404e-9d51-d3f2c8399782",
            "valid-from": "23-01-2016",
            "valid-to": "infinity",
            "$$hashKey": "6PJ",
            "type-updated": "",
            "changed": True,
            "valid-from-updated": "2016-01-22T23:00:00.000Z"
        }
        expected_output = {
            'note': 'Ret enhedstype og start dato',
            'relationer': {
                'enhedstype': [
                    {
                        'uuid': '0034fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '2017-07-31T00:00:00+02:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ]
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2016-01-23T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    },
                ]
            }
        }
        self.assertEqual(expected_output, writing.retype_org_unit(
            frontend_req))
