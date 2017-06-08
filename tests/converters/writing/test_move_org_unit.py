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


class TestMoveOrgUnit(unittest.TestCase):
    maxDiff = None

    @freezegun.freeze_time('2017-05-15 12:00:00', tz_offset=+1)
    @requests_mock.mock()
    def test_should_move_org_unit_correctly(self, mock):
        frontend_req = {
            'moveDate': '18-06-2017',
            'newParentOrgUnitUUID': '5c5ba813-0550-4284-8f47-cbb36725568d'
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
                                                'from': '2017-05-07T22:00:00+00:00',
                                                'to': '2017-06-18T00:00:00+02:00',
                                                'to_included': False
                                            }
                                        },
                                        {
                                            'uuid': '5c5ba813-0550-4284-8f47-cbb36725568d',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-06-18T00:00:00+02:00',
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

        actual_output = writing.move_org_unit(frontend_req, '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5')
        expected_output = expected_output['results'][0][0]['registreringer'][-1]

        self.assertEqual(actual_output, expected_output, 'Unexpected output for move org unit')

