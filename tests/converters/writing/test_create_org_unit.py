#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.converters import writing


class TestCreateOrgUnit(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.virkning = {
            'from': '2017-11-30T00:00:00+01:00',
            'to': '2018-11-30T00:00:00+01:00'
        }

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
                        'UUID_EnhedsAdresse':
                            '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
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
            'user-key': 'NULL'
        }

        output_org_unit = {
            'note': 'Oprettet i MO',
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'New Unit',
                        'brugervendtnoegle': 'NewUnit',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
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
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                    {'gyldighed': 'Inaktiv',
                     'virkning': {
                         'from': '-infinity',
                         'from_included': False,
                         'to': '2017-11-30T00:00:00+01:00',
                         'to_included': False}
                     }
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },

                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
            }
        }
        self.assertEqual(writing.create_org_unit(frontend_req),
                         output_org_unit,
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
                        'UUID_EnhedsAdresse':
                            '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
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
            'user-key': 'NULL'
        }

        output_org_unit = {
            'note': 'Oprettet i MO',
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'enhedsnavn': 'New Unit',
                        'brugervendtnoegle': 'NewUnit',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
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
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': '2017-11-30T00:00:00+01:00',
                            'to_included': False
                        }
                    }
                ],
            },
            'relationer': {
                'adresser': [
                    {
                        'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },

                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:12345678',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                    {
                        'urn': 'urn:magenta.dk:telefon:87654321',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },

                ],
                'tilhoerer': [
                    {
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
                'enhedstype': [
                    {
                        'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
                'overordnet': [
                    {
                        'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }
                ],
            }
        }
        self.assertEqual(writing.create_org_unit(frontend_req),
                         output_org_unit,
                         'Org unit not created correctly from FE req')
