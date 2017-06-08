#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import requests_mock
import unittest

from mora.converters import writing


class TestRenameOrgUnit(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @freezegun.freeze_time('2017-05-15 12:00:00', tz_offset=+1)
    @requests_mock.mock()
    def test_should_rename_org_unit_correctly(self, mock):
        frontend_req = {
            'name': 'A6om',
            'user-key': 'A6',
            'parent-object': {
                'name': 'Øvrige Enheder',
                'user-key': 'ØVRIGE',
                'parent-object': {
                    'name': 'Aarhus Kommune',
                    'user-key': 'ÅRHUS',
                    'parent-object': None,
                    'valid-to': 'infinity',
                    'activeName': 'Aarhus Kommune',
                    'valid-from': '2015-12-31 23:00:00+00',
                    'uuid': '7454a573-5dab-4c2f-baf2-89f273286dec',
                    'hasChildren': True,
                    'org': '59141156-ed0b-457c-9535-884447c5220b',
                    'parent': None},
                'valid-to': 'infinity',
                'activeName': 'Øvrige Enheder',
                'valid-from': '2015-12-31 23:00:00+00',
                'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                'hasChildren': True,
                'org': '59141156-ed0b-457c-9535-884447c5220b',
                'parent': '7454a573-5dab-4c2f-baf2-89f273286dec'},
            'valid-to': 'infinity',
            'activeName': 'A6',
            'valid-from': '20-05-2017',
            'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
            'hasChildren': False,
            'org': '59141156-ed0b-457c-9535-884447c5220b',
            'parent': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc'
        }
        lora_response = {
            'results': [
                [
                    {
                        'registreringer': [
                            {
                                'tilstande': {
                                    'organisationenhedgyldighed': [
                                        {
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            },
                                            'gyldighed': 'Aktiv'
                                        }
                                    ]
                                },
                                'fratidspunkt': {
                                    'graenseindikator': True,
                                    'tidsstempeldatotid': '2017-06-02T12:57:21.367559+00:00'
                                },
                                'brugerref': '42c432e8-9c4a-11e6-9f62-873cf34a735f',
                                'attributter': {
                                    'organisationenhedegenskaber': [
                                        {
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            },
                                            'brugervendtnoegle': 'A6',
                                            'enhedsnavn': 'A6'
                                        }
                                    ]
                                },
                                'livscykluskode': 'Rettet',
                                'tiltidspunkt': {
                                    'tidsstempeldatotid': 'infinity'
                                },
                                'relationer': {
                                    'tilhoerer': [
                                        {
                                            'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        }
                                    ],
                                    'adresser': [
                                        {
                                            'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        },
                                    ],
                                    'enhedstype': [
                                        {
                                            'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        }
                                    ],
                                    'overordnet': [
                                        {
                                            'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        }
                                    ]
                                }
                            }
                        ],
                        'id': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'
                    }
                ]
            ]
        }
        mock.get('http://mox/organisation/organisationenhed?uuid=65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
                 json=lora_response)
        expected_output = {
            'results': [
                [
                    {
                        'registreringer': [
                            {
                                'tilstande': {
                                    'organisationenhedgyldighed': [
                                        {
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            },
                                            'gyldighed': 'Aktiv'
                                        },
                                    ]
                                },
                                'fratidspunkt': {
                                    'graenseindikator': True,
                                    'tidsstempeldatotid': '2017-06-02T12:57:21.367559+00:00'
                                },
                                'brugerref': '42c432e8-9c4a-11e6-9f62-873cf34a735f',
                                'attributter': {
                                    'organisationenhedegenskaber': [
                                        {
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07T22:00:00+00:00',
                                                'to': '2017-05-20T00:00:00+02:00',
                                                'to_included': False
                                            },
                                            'brugervendtnoegle': 'A6',
                                            'enhedsnavn': 'A6'
                                        },
                                        {
                                            'virkning': {
                                                'from': '2017-05-20T00:00:00+02:00',
                                                'from_included': True,
                                                'to': 'infinity',
                                                'to_included': False,
                                            },
                                            'brugervendtnoegle': 'A6',
                                            'enhedsnavn': 'A6om'
                                        }
                                    ]
                                },
                                'livscykluskode': 'Rettet',
                                'tiltidspunkt': {
                                    'tidsstempeldatotid': 'infinity'
                                },
                                'relationer': {
                                    'tilhoerer': [
                                        {
                                            'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        },
                                    ],
                                    'adresser': [
                                        {
                                            'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        },
                                    ], 'enhedstype': [
                                        {
                                            'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        },
                                    ],
                                    'overordnet': [
                                        {
                                            'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': 'infinity',
                                                'to_included': False
                                            }
                                        },
                                    ]
                                }
                            }
                        ],
                        'id': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'
                    }
                ]
            ]
        }

        actual_output = writing.rename_org_unit(frontend_req)
        expected_output = expected_output['results'][0][0]['registreringer'][-1]

        self.assertEqual(actual_output, expected_output, 'Unexpected output for rename org unit')

