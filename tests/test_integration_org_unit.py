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
from . import util

mock_uuid = 'f494ad89-039d-478e-91f2-a63566554bd6'


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('mora.service.orgunit.uuid.uuid4', new=lambda: mock_uuid)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_org_unit_temporality(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=past',
            [
                {
                    "name": "Afdeling for Fremtidshistorik",
                    "user_key": "frem",
                    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    "validity": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2017-01-01T00:00:00+01:00"
                    }
                }
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=present',
            [
                {
                    "name": "Afdeling for Samtidshistorik",
                    "user_key": "frem",
                    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                    "validity": {
                        "from": "2017-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00"
                    }
                }
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=future',
            [
                {
                    "name": "Afdeling for Fortidshistorik",
                    "user_key": "frem",
                    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                    "validity": {
                        "from": "2018-01-01T00:00:00+01:00",
                        "to": "2019-01-01T00:00:00+01:00"
                    }
                }
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=past&at=2020-01-01',
            [
                {
                    'name': 'Afdeling for Fremtidshistorik',
                    'user_key': 'frem',
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa'
                    },
                    'validity': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2017-01-01T00:00:00+01:00'
                    }
                },
                {
                    'name': 'Afdeling for Samtidshistorik',
                    'user_key': 'frem',
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa'
                    },
                    'validity': {
                        'from': '2017-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    }
                },
                {
                    'name': 'Afdeling for Fortidshistorik',
                    'user_key': 'frem',
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                    },
                    'parent': {
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa'
                    },
                    'validity': {
                        'from': '2018-01-01T00:00:00+01:00',
                        'to': '2019-01-01T00:00:00+01:00'
                    }
                }
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=present&at=2020-01-01',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=future&at=2020-01-01',
            [],
        )

    @util.mock('aabogade.json', allow_mox=True)
    def test_create_org_unit(self, m):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Fake Corp",
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "addresses": [
                {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefonnummer",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "value": "11 22 33 44",
                },
                {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "Adresse",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2010-02-04T00:00:00+01",
                "to": "2017-10-22T00:00:00+02",
            }
        }

        r = self._perform_request('/service/ou/create', json=payload)
        unitid = r.json

        expected = {
            "livscykluskode": "Opstaaet",
            "note": "Oprettet i MO",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2010-02-04 00:00:00+01"
                        },
                        "brugervendtnoegle":
                            'Fake Corp f494ad89-039d-478e-91f2-a63566554bd6',
                        "enhedsnavn": "Fake Corp"
                    }
                ]
            },
            "relationer": {
                'adresser': [
                    {
                        'objekttype': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        'urn': 'urn:magenta.dk:telefon:+4511223344',
                        'virkning': {
                            'from': '2010-02-04 00:00:00+01',
                            'from_included': True,
                            'to': '2017-10-22 00:00:00+02',
                            'to_included': False,
                        },
                    },
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': '2010-02-04 00:00:00+01',
                            'from_included': True,
                            'to': '2017-10-22 00:00:00+02',
                            'to_included': False,
                        },
                    },
                ],
                "overordnet": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2010-02-04 00:00:00+01"
                        },
                        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
                    }
                ],
                "tilhoerer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2010-02-04 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "enhedstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2010-02-04 00:00:00+01"
                        },
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                    }
                ],
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2010-02-04 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
        }

        actual_org_unit = c.organisationenhed.get(unitid)

        self.assertRegistrationsEqual(expected, actual_org_unit)

        self.assertRequestResponse(
            '/service/ou/{}/'.format(unitid),
            {
                'name': 'Fake Corp',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'parent': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
                'user_key': 'Fake Corp f494ad89-039d-478e-91f2-a63566554bd6',
                'uuid': unitid,
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/'.format(unitid),
            {
                'address': True,
                'association': False,
                'engagement': False,
                'leave': False,
                'manager': False,
                'org_unit': True,
                'role': False,
            },
        )

    def test_edit_org_unit_overwrite(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = {
            "original": {
                "validity": {
                    "from": "2016-01-01 00:00:00+01",
                    "to": None
                },
                "parent": {
                    'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "org_unit_type": {
                    'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "name": "Filosofisk Institut",
            },
            "data": {
                "org_unit_type": {
                    'uuid': "79e15798-7d6d-4e85-8496-dcc8887a1c1a"
                },
                "validity": {
                    "from": "2017-01-01T00:00:00+01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(org_unit_uuid),
            org_unit_uuid, json=req)

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    }
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    },
                    {
                        "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "adresser": [
                    {
                        "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "urn": "urn:magenta.dk:telefon:+4587150000",
                        "objekttype": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_edit_org_unit(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = {
            "data": {
                "org_unit_type": {
                    'uuid': "79e15798-7d6d-4e85-8496-dcc8887a1c1a"
                },
                "validity": {
                    "from": "2017-01-01T00:00:00+01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(org_unit_uuid),
            org_unit_uuid, json=req)

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    },
                    {
                        "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "adresser": [
                    {
                        "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "urn": "urn:magenta.dk:telefon:+4587150000",
                        "objekttype": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_rename_org_unit(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = {
            "data": {
                "name": "Filosofisk Institut II",
                "validity": {
                    "from": "2018-01-01T00:00:00+01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(org_unit_uuid),
            org_unit_uuid, json=req)

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2018-01-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut II"
                    },
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2018-01-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "adresser": [
                    {
                        "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "urn": "urn:magenta.dk:telefon:+4587150000",
                        "objekttype": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_rename_org_unit_early(self):
        # Test that we can rename a unit to a date *earlier* than its
        # creation date. We are expanding the validity times on the
        # object, so we insert a separate copy as to not 'taint' the
        # fixtures, as LoRa is unable to properly delete objects
        # without the validities bleeding through.

        self.load_sample_structures()

        org_unit_uuid = '930f078b-30ac-4970-8004-66ab8cbd1f3d'

        util.load_fixture(
            'organisation/organisationenhed',
            'create_organisationenhed_fil.json', org_unit_uuid)

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(org_unit_uuid),
            org_unit_uuid, json={
                "data": {
                    "name": "Filosofisk Institut II",
                    "validity": {
                        "from": "2015-01-01T00:00:00+01",
                    },
                },
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'
            '?validity=past'.format(org_unit_uuid),
            [],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'.format(org_unit_uuid),
            [{
                'name': 'Filosofisk Institut II',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'parent': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'user_key': 'fil',
                'uuid': org_unit_uuid,
                'validity': {
                    'from': '2015-01-01T00:00:00+01:00', 'to': None,
                },
            }],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'
            '?validity=future'.format(org_unit_uuid),
            [],
        )

    def test_move_org_unit(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = {
            "data": {
                "parent": {
                    "uuid": "235ce700-c322-4ebb-94d5-fafb5aace1b5"
                },
                "validity": {
                    "from": "2017-07-01T00:00:00+02",
                },
            },
        }

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(org_unit_uuid),
            org_unit_uuid, json=req)

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-07-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-07-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-07-01 00:00:00+02"
                        },
                    }, {
                        "uuid": "235ce700-c322-4ebb-94d5-fafb5aace1b5",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-07-01 00:00:00+02",
                            "to": "infinity"
                        },
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "adresser": [
                    {
                        "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "objekttype": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "urn": "urn:magenta.dk:telefon:+4587150000",
                        "objekttype": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_terminate_org_unit(self):
        self.load_sample_structures()

        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"

        payload = {
            "validity": {
                "from": "2016-10-22T00:00:00+02"
            }
        }

        self._perform_request('/service/ou/{}/terminate'.format(unitid),
                              json=payload)

        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=past',
            [
                {'name': 'Filosofisk Institut',
                 'org': {'name': 'Aarhus Universitet',
                         'user_key': 'AU',
                         'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'},
                 'org_unit_type': {'example': None,
                                   'name': 'Institut',
                                   'scope': None,
                                   'user_key': 'inst',
                                   'uuid': 'ca76a441-6226-404f-'
                                           '88a9-31e02e420e52'},
                 'parent': {'name': 'Humanistisk fakultet',
                            'user_key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'},
                 'user_key': 'fil',
                 'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                 'validity': {'from': '2016-01-01T00:00:00+01:00',
                              'to': '2016-10-22T00:00:00+02:00'}}]
        )

        # Verify that we are no longer able to see org unit
        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=present',
            [],
        )

    def test_terminate_org_unit_validations(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "00000000-0000-0000-0000-000000000000",
            ),
            {
                'error': True,
                'cause': 'not-found',
                'description': 'no such unit!',
                'status': 404,
            },
            status_code=404,
            json={
                "validity": {
                    "from": "2017-01-01T00:00:00+02"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            ),
            {
                'error': True,
                'cause': 'validation',
                'status': 400,

                'description': 'cannot terminate unit with 1 active children',

                'role_count': 0,
                'child_count': 1,

                'child_units': [
                    {
                        'child_count': 0,
                        'name': 'Afdeling for Fremtidshistorik',
                        'user_key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    },
                ],
            },
            status_code=400,
            json={
                "validity": {
                    "from": "2017-01-01T00:00:00+02"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'cause': 'validation',
                'status': 400,

                'description':
                'cannot terminate unit with 2 active children '
                'and 4 active roles',

                'role_count': 4,
                'child_count': 2,

                'child_units': [
                    {
                        'child_count': 0,
                        'name': 'Filosofisk Institut',
                        'user_key': 'fil',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                    {
                        'child_count': 1,
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
            },
            status_code=400,
            json={
                "validity": {
                    "from": "2017-06-01T00:00:00+02"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'cause': 'validation',
                'status': 400,

                'description':
                'cannot terminate unit with 1 active children '
                'and 4 active roles',

                'role_count': 4,
                'child_count': 1,

                'child_units': [
                    {
                        'child_count': 0,
                        'name': 'Filosofisk Institut',
                        'user_key': 'fil',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                ],
            },
            status_code=400,
            json={
                "validity": {
                    "from": "2019-01-01T00:00:00+01"
                }
            },
        )

        for unitid in (
            '85715fc7-925d-401b-822d-467eb4b163b6',
        ):
            self.assertRequestResponse(
                '/service/ou/{}/terminate'.format(
                    unitid,
                ),
                unitid,
                json={
                    "validity": {
                        "from": "2019-01-01T00:00:00+01"
                    }
                },
            )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'cause': 'validation',
                'status': 400,

                'description':
                'cannot terminate unit with 4 active roles',

                'role_count': 4,
                'child_count': 0,

                'child_units': [],
            },
            status_code=400,
            json={
                "validity": {
                    "from": "2019-01-01T00:00:00+01"
                }
            },
        )
