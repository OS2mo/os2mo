#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from mora.converters import writing


class TestUpdateOrgFunktion(TestCase):
    maxDiff = None

    def test_update_org_funktion(self):
        # Arrange
        req = {
            "job-title": {
                "name": "Afdeling",
                "userKey": "afd",
                "uuid": "1a20ee5b-71e1-4e1d-8d26-6cb3cead2cb5"
            },
            "org-unit": {
                "activeName": "Humanistisk fakultet",
                "name": "Humanistisk fakultet",
                "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "type": {
                    "name": "Institut",
                    "user-key": "inst",
                    "userKey": "inst",
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "user-key": "hum",
                "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "valid-from": "31-12-2015",
                "valid-to": "infinity"
            },
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "person-name": "Anders And",
            "role-type": "engagement",
            "type": {
                "name": "Afdeling",
                "userKey": "afd",
                "uuid": "da76a441-6226-404f-88a9-31e02e420e52"
            },
            "uuid": "783fdca1-2f9d-4ee4-bbbf-846bdb8c0b27",
            "valid-from": "01-01-2016",
            "valid-to": "01-01-2018",
            "$$hashKey": "04D",
            "changed": True
        }

        original = {
            "relationer": {
                "opgaver": [
                    {
                        'uuid': '6d54f021-1617-4b4f-a2fc-84c1177c06ca',
                        'virkning': {
                            'from': '2015-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2017-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    },
                    {
                        'uuid': '65207d1d-6fca-4762-ad20-d2d7818ffe8b',
                        'virkning': {
                            'from': '2017-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2019-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    }
                ]
            }
        }

        expected_result = {
            "note": "Ret engagement",
            "relationer": {
                "organisatoriskfunktionstype": [{
                    'uuid': "da76a441-6226-404f-88a9-31e02e420e52",
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'from_included': True,
                        'to': '2018-01-01T00:00:00+01:00',
                        'to_included': False
                    }
                }],
                "opgaver": [
                    {
                        'uuid': '6d54f021-1617-4b4f-a2fc-84c1177c06ca',
                        'virkning': {
                            'from': '2015-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2016-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    },
                    {
                        'uuid': "1a20ee5b-71e1-4e1d-8d26-6cb3cead2cb5",
                        'virkning': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    },
                    {
                        'uuid': '65207d1d-6fca-4762-ad20-d2d7818ffe8b',
                        'virkning': {
                            'from': '2018-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2019-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    }
                ]
            }
        }

        # Act
        actual_result = writing.update_org_funktion(req, original)

        # Assert
        self.assertEqual(expected_result, actual_result)
