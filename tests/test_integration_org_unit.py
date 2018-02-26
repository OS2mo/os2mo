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
@patch('mora.service.org.uuid.uuid4', new=lambda: mock_uuid)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_org_unit(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Fake Corp",
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
            },
            # TODO
            "addresses": [

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
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    }
                ],
                # "addresser": [
                #     {
                #         "virkning": {
                #             "to_included": False,
                #             "to": "2017-10-22 00:00:00+02",
                #             "from_included": True,
                #             "from": "2010-02-04 00:00:00+01"
                #         },
                #         "uuid": "f494ad89-039d-478e-91f2-a63566554bd6"
                #     }
                # ]
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

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"

        payload = {
            "validity": {
                "from": "2017-10-22T00:00:00+02"
            }
        }

        self._perform_request('/service/ou/{}/terminate'.format(unitid),
                              json=payload)

        expected = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'brugervendtnoegle': 'fil',
                        'enhedsnavn': 'Filosofisk '
                                      'Institut',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ]
            },
            'livscykluskode': 'Rettet',
            'note': 'Afslut enhed',
            'relationer': {
                'adresser': [
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    },
                    {
                        'objekttype':
                            '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        'urn': 'urn:magenta.dk:telefon:+4587150000',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ],
                'overordnet': [
                    {
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ],
                'tilhoerer': [
                    {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
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
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': '2017-10-22 '
                                  '00:00:00+02',
                            'to_included': False
                        }
                    },
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '2017-10-22 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ]
            }
        }

        actual_org_unit = c.organisationenhed.get(unitid)

        self.assertRegistrationsEqual(expected, actual_org_unit)
