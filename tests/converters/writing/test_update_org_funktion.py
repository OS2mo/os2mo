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

    def test_update_org_funktion_diminishing(self):
        # Arrange
        req = {
            "oldvalidfrom": "2017-01-01T00:00:00+01:00",
            "oldvalidto": "infinity",
            "newvalidfrom": "2017-01-01T00:00:00+01:00",
            "newvalidto": "2018-01-01T00:00:00+01:00",
            "jobtitle": "da8dc037-810d-41d4-a456-0c34906fe366",
            "type": "4fa10174-776f-4246-8ae5-d0fff3c680dd",
        }

        original = {
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "brugervendtnoegle": "973f5b52-0ce1-421e-"
                                             "bc0a-c2d7b7946f79",
                        "funktionsnavn": "Name",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "note": "Automatisk indl\u00e6sning",
            "relationer": {
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            }
        }

        expected_result = {
            "note": "Rediger engagement",
            "relationer": {
                "organisatoriskfunktionstype": [{
                    'uuid': "4fa10174-776f-4246-8ae5-d0fff3c680dd",
                    'virkning': {
                        "from": "2017-01-01T00:00:00+01:00",
                        'from_included': True,
                        'to': '2018-01-01T00:00:00+01:00',
                        'to_included': False
                    }
                }],
                "opgaver": [
                    {
                        'uuid': 'da8dc037-810d-41d4-a456-0c34906fe366',
                        'virkning': {
                            "from": "2017-01-01T00:00:00+01:00",
                            'to': '2018-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        'virkning': {
                            'from': '2018-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "2018-01-01T00:00:00+01:00",
                            'from_included': True,
                            "to": "infinity",
                            'to_included': False
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2017-01-01T00:00:00+01:00",
                            'from_included': True,
                            "to": "2018-01-01T00:00:00+01:00",
                            'to_included': False
                        }
                    }
                ]
            }
        }

        # Act
        actual_result = writing.update_engagement_payload(req, original)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_update_org_expanding(self):
        # Arrange
        req = {
            "oldvalidfrom": "2017-01-01T00:00:00+01:00",
            "oldvalidto": "2018-01-01T00:00:00+01:00",
            "newvalidfrom": "2017-01-01T00:00:00+01:00",
            "newvalidto": "2019-01-01T00:00:00+01:00",
            "jobtitle": "da8dc037-810d-41d4-a456-0c34906fe366",
            "type": "4fa10174-776f-4246-8ae5-d0fff3c680dd",
        }

        original = {
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "brugervendtnoegle": "973f5b52-0ce1-421e-"
                                             "bc0a-c2d7b7946f79",
                        "funktionsnavn": "Name",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ]
            },
            "note": "Automatisk indl\u00e6sning",
            "relationer": {
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00"
                        }
                    }
                ]
            }
        }

        expected_result = {
            "note": "Rediger engagement",
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "brugervendtnoegle": "973f5b52-0ce1-421e-"
                                             "bc0a-c2d7b7946f79",
                        "funktionsnavn": "Name",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2019-01-01T00:00:00+01:00"
                        }
                    }
                ]
            },
            "relationer": {
                "organisatoriskfunktionstype": [{
                    'uuid': "4fa10174-776f-4246-8ae5-d0fff3c680dd",
                    'virkning': {
                        "from": "2017-01-01T00:00:00+01:00",
                        'from_included': True,
                        'to': '2019-01-01T00:00:00+01:00',
                        'to_included': False
                    }
                }],
                "opgaver": [
                    {
                        'uuid': 'da8dc037-810d-41d4-a456-0c34906fe366',
                        'virkning': {
                            "from": "2017-01-01T00:00:00+01:00",
                            'to': '2019-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2019-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2019-01-01T00:00:00+01:00"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            'from_included': True,
                            'to_included': False,
                            "from": "2017-01-01T00:00:00+01:00",
                            "to": "2019-01-01T00:00:00+01:00"
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2017-01-01T00:00:00+01:00",
                            'from_included': True,
                            "to": "2019-01-01T00:00:00+01:00",
                            'to_included': False
                        }
                    }
                ]
            }
        }

        # Act
        actual_result = writing.update_engagement_payload(req, original)

        # Assert
        self.assertEqual(expected_result, actual_result)
