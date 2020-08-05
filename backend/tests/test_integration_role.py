# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun

from mora import lora
from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_role(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "role",
                "person": {'uuid': userid},
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "role_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": '1234',
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        role_id, = self.assertRequest(
            '/service/details/create',
            json=payload,
            amqp_topics={
                'org_unit.role.create': 1,
                'employee.role.create': 1,
            },
        )

        expected = {
            "livscykluskode": "Importeret",
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
                ]
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
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "Rolle"
                    }
                ]
            }
        }

        actual_role = c.organisationfunktion.get(role_id)

        self.assertRegistrationsEqual(actual_role, expected)

    def test_create_role_on_unit(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "role",
                "person": {'uuid': userid},
                "org_unit": {'uuid': unitid},
                "role_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        roleid, = self.assertRequest(
            '/service/details/create',
            json=payload,
            amqp_topics={
                'org_unit.role.create': 1,
                'employee.role.create': 1,
            },
        )

        expected = {
            "livscykluskode": "Importeret",
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
                        "uuid": userid
                    }
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
                        "uuid": unitid
                    }
                ]
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
                        "brugervendtnoegle": roleid,
                        "funktionsnavn": "Rolle"
                    }
                ]
            }
        }

        actual_role = c.organisationfunktion.get(roleid)

        self.assertRegistrationsEqual(actual_role, expected)

    def test_create_role_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "role",
                "person": {'uuid': userid},
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "role_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                },
            }
        ]

        role_id, = self.assertRequest(
            '/service/details/create',
            json=payload,
            amqp_topics={
                'org_unit.role.create': 1,
                'employee.role.create': 1,
            },
        )

        expected = {
            "livscykluskode": "Importeret",
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
                ]
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
                        "brugervendtnoegle": role_id,
                        "funktionsnavn": "Rolle"
                    }
                ]
            }
        }

        actual_role = c.organisationfunktion.get(role_id)

        self.assertRegistrationsEqual(actual_role, expected)

    def test_edit_role_no_overwrite(self):
        self.load_sample_structures()

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        req = [{
            "type": "role",
            "uuid": role_uuid,
            "data": {
                "role_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                },
                "org_unit": {
                    'uuid': "b688513d-11f7-4efc-b679-ab082a2055d0"
                },
                "user_key": "bjørndrager",
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [role_uuid],
            json=req,
            amqp_topics={
                'employee.role.update': 1,
                'org_unit.role.update': 1,
            },
        )

        expected_role = {
            "note": "Rediger rolle",
            "relationer": {
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
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
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
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
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
                ]
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
                            "to": "2018-04-01 00:00:00+02"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bjørndrager",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(expected_role, actual_role)

    def test_edit_role_minimal(self):
        self.load_sample_structures()

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        req = [{
            "type": "role",
            "uuid": role_uuid,
            "data": {
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [role_uuid],
            json=req,
            amqp_topics={
                'employee.role.update': 1,
                'org_unit.role.update': 1,
            },
        )

        expected_role = {
            "note": "Rediger rolle",
            "relationer": {
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
                ]
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
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(expected_role, actual_role)

    def test_edit_role_minimal_unit(self):
        self.load_sample_structures()

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        req = [{
            "type": "role",
            "uuid": role_uuid,
            "data": {
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [role_uuid],
            json=req,
            amqp_topics={
                'employee.role.update': 1,
                'org_unit.role.update': 1,
            },
        )

        expected_role = {
            "note": "Rediger rolle",
            "relationer": {
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
                ]
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
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(expected_role, actual_role)

    def test_edit_role_person(self):
        self.load_sample_structures()

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        req = {
            "type": "role",
            "uuid": role_uuid,
            "data": {
                "person": {
                    "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                },
                "validity": {
                    "from": "2018-01-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            role_uuid,
            json=req,
            amqp_topics={
                'employee.role.update': 1,
                'org_unit.role.update': 1,
            },
        )

        expected_role = {
            "note": "Rediger rolle",
            "relationer": {
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
                            "to": "2018-01-01 00:00:00+01",
                        }
                    },
                    {
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
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
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(expected_role, actual_role)

    def test_edit_role_overwrite(self):
        self.load_sample_structures()

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        req = [{
            "type": "role",
            "uuid": role_uuid,
            "original": {
                "validity": {
                    "from": "2017-01-01",
                    "to": None
                },
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "role_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"},
            },
            "data": {
                "role_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                },
                "org_unit": {
                    'uuid': "b688513d-11f7-4efc-b679-ab082a2055d0"
                },
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [role_uuid],
            json=req,
            amqp_topics={
                'employee.role.update': 1,
                'org_unit.role.update': 1,
            },
        )

        expected_role = {
            "note": "Rediger rolle",
            "relationer": {
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
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
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
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
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
                ]
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
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(expected_role, actual_role)

    def test_terminate_role(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "to": "2017-11-30"
            }
        }

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json=payload,
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.engagement.delete': 1,
                'employee.employee.delete': 1,
                'employee.it.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        expected_role = {
            "note": "Afsluttet",
            "relationer": {
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
                ]
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
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Rolle"
                    }
                ]
            },
        }

        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'

        actual_role = c.organisationfunktion.get(role_uuid)

        self.assertRegistrationsEqual(actual_role, expected_role)

    def test_reading(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/'
            'details/role?only_primary_uuid=1',
            [{
                'org_unit': {
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'role_type': {
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'uuid': '1b20d0b9-96a0-42a6-b196-293bb86e62e8',
                'user_key': 'bvn',
                'validity': {'from': '2017-01-01', 'to': None},
            }],
        )

    def test_create_role_missing_unit(self):
        self.load_sample_structures()

        # Check the POST request
        unitid = "00000000-0000-0000-0000-000000000000"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "role",
                "person": {'uuid': userid},
                "org_unit": {'uuid': unitid},
                "role_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            '/service/details/create',
            {
                'description': 'Org unit not found.',
                'error': True,
                'error_key': 'E_ORG_UNIT_NOT_FOUND',
                'org_unit_uuid': '00000000-0000-0000-0000-000000000000',
                'status': 404,
            },
            json=payload,
            status_code=404,
        )

    def test_create_role_missing_user(self):
        self.load_sample_structures()

        # Check the POST request
        unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
        userid = "00000000-0000-0000-0000-000000000000"

        payload = [
            {
                "type": "role",
                "person": {'uuid': userid},
                "org_unit": {'uuid': unitid},
                "role_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            '/service/details/create',
            {
                'description': 'User not found.',
                'employee_uuid': '00000000-0000-0000-0000-000000000000',
                'error': True,
                'error_key': 'E_USER_NOT_FOUND',
                'status': 404,
            },
            json=payload,
            status_code=404,
        )
