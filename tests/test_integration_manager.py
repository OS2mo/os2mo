#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from unittest.mock import patch

import freezegun

from mora import lora
from tests import util

mock_uuid = '1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5'


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('uuid.uuid4', new=lambda: mock_uuid)
class Tests(util.LoRATestCase):
    maxDiff = None

    @util.mock('aabogade.json', allow_mox=True)
    def test_create_manager(self, m):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                'address': {
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                },
                "responsibility": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "manager_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "manager_level": {
                    "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': '2017-12-01 00:00:00+01',
                            'from_included': True,
                            'to': '2017-12-02 00:00:00+01',
                            'to_included': False,
                        },
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    },
                    {
                        "objekttype": "lederniveau",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        managers = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(managers), 1)
        managerid = managers[0]

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': {
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                },
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': None,
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01T00:00:00+01:00',
                    'to': '2017-12-02T00:00:00+01:00',
                },
            }],
        )

    def test_create_manager_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "responsibility": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "manager_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "manager_level": {
                    "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    },
                    {
                        "objekttype": "lederniveau",
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        managers = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(managers), 1)
        managerid = managers[0]

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': None,
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': None,
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01T00:00:00+01:00', 'to': None,
                },
            }],
        )

    def test_create_manager_minimal(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                },
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        managers = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(managers), 1)
        managerid = managers[0]

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': None,
                'manager_level': None,
                'manager_type': None,
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': None,
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01T00:00:00+01:00',
                    'to': '2017-12-02T00:00:00+01:00',
                },
            }],
        )

    def test_create_manager_fails_on_empty_payload(self):
        self.load_sample_structures()

        payload = [
            {
                "type": "manager",
            }
        ]

        self.assertRequestFails(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/create', 400,
            json=payload)

    def test_edit_manager_no_overwrite(self):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        req = [{
            "type": "manager",
            "uuid": manager_uuid,
            "data": {
                "org_unit": {
                    'uuid': "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "responsibility": {
                    'uuid': "64dcaca7-daff-4d9f-b4a9-78f2920e8e50"
                },
                "manager_level": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "manager_type": {
                    'uuid': "e34d4426-9845-4c72-b31e-709be85d6fa2"
                },
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederniveau",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "64dcaca7-daff-4d9f-b4a9-78f2920e8e50",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [{
                'address': {
                    'href': 'mailto:ceo@example.com',
                    'name': 'ceo@example.com',
                    'urn': 'urn:mailto:ceo@example.com',
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                },
                'manager_level': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': {
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'validity': {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': '2018-04-01T00:00:00+02:00',
                },
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': {
                    'href': 'mailto:ceo@example.com',
                    'name': 'ceo@example.com',
                    'urn': 'urn:mailto:ceo@example.com',
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                },
                'manager_level': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'name': 'Filosofisk Institut',
                    'user_key': 'fil',
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': None,
                'uuid': manager_uuid,
                'validity': {
                    'from': '2018-04-01T00:00:00+02:00', 'to': None,
                },
            }],
        )

    @util.mock('aabogade.json', allow_mox=True)
    def test_edit_manager_overwrite(self, m):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        req = [{
            "type": "manager",
            "uuid": manager_uuid,
            "original": {
                "org_unit": {
                    'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "responsibility": {
                    'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                },
                "manager_level": {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "manager_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "validity": {
                    "from": "2017-01-01 00:00:00+01:00",
                    "to": None,
                },
            },
            "data": {
                "address": {
                    "address_type": {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
                "org_unit": {
                    'uuid': "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "responsibility": {
                    'uuid': "64dcaca7-daff-4d9f-b4a9-78f2920e8e50"
                },
                "manager_level": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "manager_type": {
                    'uuid': "e34d4426-9845-4c72-b31e-709be85d6fa2"
                },
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': "2018-04-01 00:00:00+02",
                            'to_included': False,
                        },
                    },
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': "2018-04-01 00:00:00+02",
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "64dcaca7-daff-4d9f-b4a9-78f2920e8e50",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': {
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                },
                'manager_level': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'name': 'Filosofisk Institut',
                    'user_key': 'fil',
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': None,
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'validity': {
                    'from': '2018-04-01T00:00:00+02:00', 'to': None,
                },
            }],
        )

    def test_terminate_manager(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "from": "2017-12-01T00:00:00+01"
            }
        }

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

        expected = {
            "note": "Afslut medarbejder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [{
                'address': {
                    'href': 'mailto:ceo@example.com',
                    'name': 'ceo@example.com',
                    'urn': 'urn:mailto:ceo@example.com',
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                },
                'manager_level': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': {
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'validity': {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': '2017-12-01T00:00:00+01:00',
                },
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [],
        )

    def test_edit_manager_minimal(self):
        self.load_sample_structures()

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        expected_lora = {
            "note": "Automatisk indlæsning",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        expected_mora = [{
            'address': {
                'address_type': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0'
                },
                'href': 'mailto:ceo@example.com',
                'name': 'ceo@example.com',
                'urn': 'urn:mailto:ceo@example.com'},
            'manager_level': {'example': None,
                              'name': 'Institut',
                              'scope': None,
                              'user_key': 'inst',
                              'uuid': 'ca76a441-6226-404f-'
                              '88a9-31e02e420e52'},
            'manager_type': {'example': None,
                             'name': 'Afdeling',
                             'scope': None,
                             'user_key': 'afd',
                             'uuid': '32547559-cfc1-4d97-'
                             '94c6-70b192eff825'},
            'org_unit': {'name': 'Humanistisk fakultet',
                         'user_key': 'hum',
                         'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'},
            'person': {'name': 'Anders And',
                       'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
            'responsibility': {'example': None,
                               'name': 'Fakultet',
                               'scope': None,
                               'user_key': 'fak',
                               'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'},
            'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
            'validity': {'from': '2017-01-01T00:00:00+01:00',
                         'to': None}
        }]

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        with self.subTest('preconditions'):
            self.assertRegistrationsEqual(
                c.organisationfunktion.get(manager_uuid),
                expected_lora,
            )

            self.assertRequestResponse(
                '/service/e/{}/details/manager'.format(userid),
                expected_mora,
            )

        # perform the operation
        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=[{
                "type": "manager",
                "uuid": manager_uuid,
                "data": {
                    "responsibility": {
                        'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
                    },
                    "validity": {
                        "from": "2016-04-01T00:00:00+02",
                    },
                },
            }])

        # adjust the data as expected
        expected_lora['note'] = 'Rediger leder'
        expected_lora['livscykluskode'] = 'Rettet'
        expected_lora['relationer']['opgaver'][0]['uuid'] = \
            "ca76a441-6226-404f-88a9-31e02e420e52"

        for g, f in (
                ('attributter', 'organisationfunktionegenskaber'),
                ('relationer', 'adresser'),
                ('relationer', 'opgaver'),
                ('relationer', 'organisatoriskfunktionstype'),
                ('relationer', 'tilknyttedebrugere'),
                ('relationer', 'tilknyttedeenheder'),
                ('relationer', 'tilknyttedeorganisationer'),
                ('tilstande', 'organisationfunktiongyldighed'),
        ):
            for m in expected_lora[g][f]:
                m['virkning']['from'] = '2016-04-01 00:00:00+02'

        expected_mora[0]['validity']['from'] = '2016-04-01T00:00:00+02:00'
        expected_mora[0]['responsibility'] = {
            'example': None,
            'name': 'Institut',
            'scope': None,
            'user_key': 'inst',
            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
        }

        # compare them!
        self.assertRegistrationsEqual(c.organisationfunktion.get(manager_uuid),
                                      expected_lora)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            expected_mora,
        )
