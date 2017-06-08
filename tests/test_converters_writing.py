#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora.converters import writing
import freezegun
import requests_mock
import unittest
from pprint import pprint

class TestCreateOrgUnit(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.virkning = {
            'from': '2017-11-30T00:00:00+01:00',
            'to': '2018-11-30T00:00:00+01:00'
        }

    def tearDown(self):
        pass

    def test_should_add_virkning1_correctly_to_org_unit_props_leafs_in_attributter(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                    },
                ],
            },
        }
        output_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
        }
        self.assertEqual(writing._set_virkning(input_obj, self.virkning), output_obj,
                         'Virkning not added correctly attributter')

    def test_should_add_virkning2_correctly_to_org_unit_props_leafs_in_attributter(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                    },
                ],
            },
        }
        output_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
        }
        self.assertEqual(writing._set_virkning(input_obj, self.virkning), output_obj,
                         'Virkning not added correctly for attributter')

    def test_should_add_virkning_correctly_to_org_unit_props_leafs_in_tilstande(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                    },
                ],
            },
        }
        output_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
        }
        self.assertEqual(writing._set_virkning(input_obj, self.virkning), output_obj,
                         'Virkning not added correctly for tilstande')

    def test_should_add_virkning_correctly_to_org_unit_props_leafs_in_enhedstype(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                    },
                ],
            },
            'enhedstype': [
                {
                    'uuid': '00000000-0000-0000-0000-000000000000',
                }
            ]
        }
        output_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
            'enhedstype': [
                {
                    'uuid': '00000000-0000-0000-0000-000000000000',
                    'virkning': {
                        'from': '2017-11-30T00:00:00+01:00',
                        'to': '2018-11-30T00:00:00+01:00'
                    },
                }
            ]
        }
        self.assertEqual(writing._set_virkning(input_obj, self.virkning), output_obj,
                         'Virkning not added correctly for enhedstype')

    def test_should_add_virkning_correctly_to_full_org_unit_obj(self):
        input_org_unit = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test name',
                        'brugervendtnoegle': 'test bvn',
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                    },
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    },
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                    }
                ],
                'tilhoerer': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    }
                ],
                'overordnet': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    }
                ],
            }
        }
        output_org_unit = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test name',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },

                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },

                    },
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'tilhoerer': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
            }
        }
        self.assertEqual(writing._set_virkning(input_org_unit, self.virkning), output_org_unit,
                         'Virkning not added correctly for full org unit')

    def test_should_create_org_unit_with_one_contact_channel_correctly(self):
        frontend_req = {
            'valid-from': '30-11-2017',
            'name': 'New Unit',
            'org': '59141156-ed0b-457c-9535-884447c5220b',
            'locations': [
                {
                    'contact-channels': [
                        {
                            'visibility': {
                                'name': 'N/A',
                                'uuid': '00000000-0000-0000-0000-000000000000',
                                'user-key': 'N/A'
                            },
                            'contact-info': '12345678',
                            'type': {
                                'name': 'Phone Number',
                                'uuid': 'b7ccfb21-f623-4e8f-80ce-89731f726224',
                                'prefix': 'urn:magenta.dk:telefon:'
                            }
                        }
                    ],
                    'name': 'locationname', 'primaer': True,
                    'location': {
                        'UUID_EnhedsAdresse': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'postnr': '8240',
                        'postdistrikt': 'Risskov',
                        'vejnavn': 'Pilevej 2, 8240 Risskov'
                    }
                }
            ],
            'type': {
                'name': 'Afdeling',
                'userKey': 'Afdeling',
                'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9'
            },
            'parent': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
            'valid-to': '30-11-2018',
            'user-key': 'NULL'
        }

        output_org_unit = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'New Unit',
                        'brugervendtnoegle': 'NewUnit',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },

                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    },
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },

                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    },
                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
            }
        }
        self.assertEqual(writing.create_org_unit(frontend_req), output_org_unit,
                         'Org unit not created correctly from FE req')

    def test_should_create_org_unit_with_two_contact_channels_correctly(self):
        frontend_req = {
            'valid-from': '30-11-2017',
            'name': 'New Unit',
            'org': '59141156-ed0b-457c-9535-884447c5220b',
            'locations': [
                {
                    'contact-channels': [
                        {
                            'visibility': {
                                'name': 'N/A',
                                'uuid': '00000000-0000-0000-0000-000000000000',
                                'user-key': 'N/A'
                            },
                            'contact-info': '12345678',
                            'type': {
                                'name': 'Phone Number',
                                'uuid': 'b7ccfb21-f623-4e8f-80ce-89731f726224',
                                'prefix': 'urn:magenta.dk:telefon:'
                            }
                        },
                        {
                            'visibility': {
                                'name': 'N/A',
                                'uuid': '00000000-0000-0000-0000-000000000000',
                                'user-key': 'N/A'
                            },
                            'contact-info': '87654321',
                            'type': {
                                'name': 'Phone Number',
                                'uuid': 'aaccfb21-f623-4e8f-80ce-89731f726224',
                                'prefix': 'urn:magenta.dk:telefon:'
                            }
                        }

                    ],
                    'name': 'locationname', 'primaer': True,
                    'location': {
                        'UUID_EnhedsAdresse': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'postnr': '8240',
                        'postdistrikt': 'Risskov',
                        'vejnavn': 'Pilevej 2, 8240 Risskov'
                    }
                }
            ],
            'type': {
                'name': 'Afdeling',
                'userKey': 'Afdeling',
                'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9'
            },
            'parent': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
            'valid-to': '30-11-2018',
            'user-key': 'NULL'
        }

        output_org_unit = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'New Unit',
                        'brugervendtnoegle': 'NewUnit',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },

                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    },
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },

                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:87654321',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    },

                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'from_included': True,
                            'to': '2018-11-30T00:00:00+01:00',
                            'to_included': False,
                        },
                    }
                ],
            }
        }
        self.assertEqual(writing.create_org_unit(frontend_req), output_org_unit,
                         'Org unit not created correctly from FE req')

    def test_should_extend_attributes_correctly(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {'brugervendtnoegle': 'A1',
                     'enhedsnavn': 'Digitaliseringskontoretg',
                     'virkning': {
                         'to_included': False,
                         'from': '2017-05-14 22:00:00+00',
                         'from_included': True,
                         'to': '2017-06-14 22:00:00+00'}
                     }
                ]
            }
        }
        output_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'brugervendtnoegle': 'A1',
                        'enhedsnavn': 'Digitaliseringskontoretg',
                        'virkning': {
                            'to_included': False,
                            'from': '2017-05-14 22:00:00+00',
                            'from_included': True,
                            'to': '2017-06-14 22:00:00+00'
                        }
                    },
                    {
                        'brugervendtnoegle': 'A1',
                        'enhedsnavn': 'Digitaliseringskontoretg',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        }
                    }
                ]
            }
        }
        self.assertEqual(writing._extend_current_virkning(input_obj, self.virkning),
                         output_obj,
                         'New org unit props not added correctly')


class TestCreateVirkning(unittest.TestCase):

    def setUp(self):
        self.from1 = '31-12-2017'
        self.to1 = '31-12-2018'
        self.from2 = '30-12-2017'
        self.to2 = '31-12-2018'

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_2017_12_31(self):
        self.assertEqual('2017-12-31T00:00:00+01:00',
                         writing._create_virkning(self.from1, self.to1)['from'],
                         'From should be 2017-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_2017_12_30(self):
        self.assertEqual('2017-12-30T00:00:00+01:00',
                         writing._create_virkning(self.from2, self.to2)['from'],
                         'From should be 2017-12-30T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_2018_12_31(self):
        self.assertEqual('2018-12-31T00:00:00+01:00',
                         writing._create_virkning(self.from2, self.to2)['to'],
                         'To should be 2018-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_2019_12_31(self):
        req = {
            'valid-from': '30-12-2017',
            'valid-to': '31-12-2019'
        }
        self.assertEqual('2019-12-31T00:00:00+01:00',
                         writing._create_virkning(req['valid-from'], req['valid-to'])['to'],
                         'To should be 2019-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_minus_infinity(self):
        req = {
            'valid-from': '-infinity',
            'valid-to': '31-12-2019',

        }
        self.assertEqual('-infinity',
                         writing._create_virkning(req['valid-from'], req['valid-to'])['from'],
                         'From should be -infinity')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_infinity(self):
        req = {
            'valid-from': '31-12-2019',
            'valid-to': 'infinity',

        }
        self.assertEqual('infinity',
                         writing._create_virkning(req['valid-from'], req['valid-to'])['to'],
                         'To should be infinity')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_true(self):
        self.assertEqual(True,
                         writing._create_virkning(self.from1, self.to1, from_included=True)['from_included'],
                         'from_included should be true')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_true_by_default(self):
        self.assertEqual(True,
                         writing._create_virkning(self.from1, self.to1)['from_included'],
                         'from_included should be true')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_false(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1, from_included=False)['from_included'],
                         'from_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_false(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1, to_included=False)['to_included'],
                         'to_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_false_by_default(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1)['to_included'],
                         'to_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_true(self):
        self.assertEqual(True,
                         writing._create_virkning(self.from1, self.to1, to_included=True)['to_included'],
                         'to_included should be true')

    # TODO: Should throw exception if to <= from


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

