#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import unittest

from mora.converters import writing


class TestSetVirkning(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.virkning = {
            'from': '2017-11-30T00:00:00+01:00',
            'to': '2018-11-30T00:00:00+01:00'
        }

    def test_should_add_virkning1_correctly_to_org_unit_props_leafs_attr(self):
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
        self.assertEqual(writing._set_virkning(input_obj, self.virkning),
                         output_obj,
                         'Virkning not added correctly attributter')

    def test_should_add_virkning2_correctly_to_org_unit_props_leafs_attr(self):
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
        self.assertEqual(writing._set_virkning(input_obj, self.virkning),
                         output_obj,
                         'Virkning not added correctly for attributter')

    def test_should_add_virkning_correctly_to_org_unit_props_leafs_tilst(self):
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
        self.assertEqual(writing._set_virkning(input_obj, self.virkning),
                         output_obj,
                         'Virkning not added correctly for tilstande')

    def test_should_add_virkning_to_org_unit_props_leafs_enhedtype(self):
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
        self.assertEqual(writing._set_virkning(input_obj, self.virkning),
                         output_obj,
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
        self.assertEqual(writing._set_virkning(input_org_unit, self.virkning),
                         output_org_unit,
                         'Virkning not added correctly for full org unit')

    def test_should_add_or_overwrite_virkning_correctly(self):
        input_obj = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'test unit',
                        'brugervendtnoegle': 'test bvn',
                        'virkning': {
                            'from': '2015-11-30T00:00:00+01:00',
                            'to': '2016-11-30T00:00:00+01:00'
                        },
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
                    'virkning': {
                        'from': '2011-11-30T00:00:00+01:00',
                        'to': '2012-11-30T00:00:00+01:00'
                    },
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
        self.assertEqual(
            writing._set_virkning(input_obj, self.virkning, True), output_obj,
            'Virkning not added and overwritten correctly')
