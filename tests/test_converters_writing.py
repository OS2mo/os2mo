#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora.converters import writing
import unittest


class TestConvertersWriting(unittest.TestCase):
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
        self.assertEqual(writing._add_virkning(input_obj, self.virkning), output_obj,
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
        self.assertEqual(writing._add_virkning(input_obj, self.virkning), output_obj,
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
        self.assertEqual(writing._add_virkning(input_obj, self.virkning), output_obj,
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
        self.assertEqual(writing._add_virkning(input_obj, self.virkning), output_obj,
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
        self.assertEqual(writing._add_virkning(input_org_unit, self.virkning), output_org_unit,
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
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
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
                    },
                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
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
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
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
                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:87654321',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    },

                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '2017-11-30T00:00:00+01:00',
                            'to': '2018-11-30T00:00:00+01:00'
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
    # TODO: freeze timezone

    def setUp(self):
        self.req1 = {
            'valid-from': '31-12-2017',
            'valid-to': '31-12-2018'
        }
        self.req2 = {
            'valid-from': '30-12-2017',
            'valid-to': '31-12-2018'
        }


    def tearDown(self):
        pass

    def test_should_set_from_to_2017_12_31(self):
        self.assertEqual('2017-12-31T00:00:00+01:00',
                         writing._create_virkning(self.req1)['from'],
                         'From should be 2017-12-31T00:00:00+01:00')

    def test_should_set_from_to_2017_12_30(self):
        self.assertEqual('2017-12-30T00:00:00+01:00',
                         writing._create_virkning(self.req2)['from'],
                         'From should be 2017-12-30T00:00:00+01:00')

    def test_should_set_to_to_2018_12_31(self):
        self.assertEqual('2018-12-31T00:00:00+01:00',
                         writing._create_virkning(self.req2)['to'],
                         'To should be 2018-12-31T00:00:00+01:00')

    def test_should_set_to_to_2019_12_31(self):
        req = {
            'valid-from': '30-12-2017',
            'valid-to': '31-12-2019'
        }
        self.assertEqual('2019-12-31T00:00:00+01:00',
                         writing._create_virkning(req)['to'],
                         'To should be 2019-12-31T00:00:00+01:00')

    def test_should_set_from_to_minus_infinity(self):
        req = {
            'valid-from': '-infinity',
            'valid-to': '31-12-2019',

        }
        self.assertEqual('-infinity',
                         writing._create_virkning(req)['from'],
                         'From should be -infinity')

    def test_should_set_to_to_infinity(self):
        req = {
            'valid-from': '31-12-2019',
            'valid-to': 'infinity',

        }
        self.assertEqual('infinity',
                         writing._create_virkning(req)['to'],
                         'To should be infinity')

    # TODO: Should throw exception if to <= from
    # TODO: should we set from_included and to_included?
