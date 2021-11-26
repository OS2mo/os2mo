# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import copy

import freezegun
from mock import patch

import mora.async_util
import tests.cases
from mora import lora
from mora import mapping

substitute_association = {"name": "i18n:substitute_association"}  # const


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Tests(tests.cases.LoRATestCase):
    maxDiff = None

    @patch(
        "mora.conf_db.get_configuration",
        return_value={"substitute_roles": "62ec821f-4179-4758-bfdf-134529d186e9"},
    )
    def test_create_association(self, mock):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        association_uuid = "00000000-0000-0000-0000-000000000000"
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
        subid = "aefb4355-11b1-411b-a64d-34f2ff9640f6"
        payload = [
            {
                "type": "association",
                "uuid": association_uuid,
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "substitute": {"uuid": subid},
                "user_key": "1234",
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": userid,
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": unitid,
                    }
                ],
                "tilknyttedefunktioner": [
                    {
                        "uuid": "aefb4355-11b1-411b-a64d-34f2ff9640f6",
                        "virkning": {
                            "from": "2017-12-01 " "00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 " "00:00:00+01",
                            "to_included": False,
                        },
                    }
                ],
                "primær": [
                    {
                        "uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474",
                        "virkning": {
                            "from": "2017-12-01 00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 00:00:00+01",
                            "to_included": False,
                        },
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "Tilknytning",
                    }
                ]
            },
        }

        associations = mora.async_util.async_to_sync(c.organisationfunktion.fetch)(
            tilknyttedebrugere=userid, funktionsnavn="Tilknytning"
        )
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            associationid
        )

        self.assertRegistrationsEqual(actual_association, expected)

        expected = [
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "substitute": {"uuid": subid},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            }
        ]

        self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1".format(userid),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )
        expected = [
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "substitute": {"uuid": subid},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
                "first_party_association_type": {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "third_party_associated": {"uuid": subid},
                "third_party_association_type": substitute_association,
            }
        ]

        self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1&first_party_perspective=1".format(
                userid
            ),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

        expected = []

        self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1".format(subid),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

        expected = [
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "substitute": {"uuid": subid},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
                "first_party_association_type": substitute_association,
                "third_party_associated": {"uuid": userid},
                "third_party_association_type": {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                },
            }
        ]

        self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1&first_party_perspective=1".format(
                subid
            ),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

    @patch(
        "mora.conf_db.get_configuration",
        return_value={"substitute_roles": "62ec821f-4179-4758-bfdf-134529d186e9"},
    )
    def test_create_vacant_association(self, mock):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        # test multiple valid formats
        association_uuid = "00000000-0000-0000-0000-000000000000"
        association_uuid2 = "00000000-0000-0000-0000-000000000001"

        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        subid = "aefb4355-11b1-411b-a64d-34f2ff9640f6"

        def payload(assoc_uuid, include_person=True):
            """
            :param assoc_uuid: uuid to use
            :param include_person: change between formats (both legal)
            :return: valid assoication payload
            """

            main = {
                "type": "association",
                "uuid": assoc_uuid,
                "org_unit": {"uuid": unitid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "substitute": {"uuid": subid},
                "user_key": "1234",
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
            if include_person:
                main["person"] = None
            return [main]

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload(association_uuid),
            amqp_topics={
                "org_unit.association.create": 1,
            },
        )
        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid2],
            json=payload(association_uuid2, include_person=False),
            amqp_topics={
                "org_unit.association.create": 2,
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": unitid,
                    }
                ],
                "tilknyttedefunktioner": [
                    {
                        "uuid": "aefb4355-11b1-411b-a64d-34f2ff9640f6",
                        "virkning": {
                            "from": "2017-12-01 " "00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 " "00:00:00+01",
                            "to_included": False,
                        },
                    }
                ],
                "primær": [
                    {
                        "uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474",
                        "virkning": {
                            "from": "2017-12-01 00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 00:00:00+01",
                            "to_included": False,
                        },
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "Tilknytning",
                    }
                ]
            },
        }

        associations = mora.async_util.async_to_sync(c.organisationfunktion.fetch)(
            tilknyttedeenheder=unitid,
            tilknyttedeorganisationer="456362c4-0ee4-4e5e-a72c-751239745e62",
            brugervendtnoegle="1234",
            funktionsnavn="Tilknytning",
        )
        self.assertEqual(len(associations), 2)
        for associationid in associations:
            # assert we got back one of the newly created associations (ie. exists)
            self.assertIn(associationid, [association_uuid, association_uuid2])

            # check that the content is also as expected
            actual_association = mora.async_util.async_to_sync(
                c.organisationfunktion.get
            )(associationid)

            self.assertRegistrationsEqual(actual_association, expected)

        def assoc_content_only_primary_uuid(assoc_uuid):
            """
            creates expected format

            :param assoc_uuid:
            :return:
            """
            return {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": None,
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": assoc_uuid,
                "substitute": {"uuid": subid},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            }

        expected = [
            assoc_content_only_primary_uuid(association_uuid),
            assoc_content_only_primary_uuid(association_uuid2),
        ]

        self.assertRequestResponse(  # contains sorting (ie. unordered comparison)
            "/service/ou/{}/details/association"
            "?validity=future&only_primary_uuid=1".format(unitid),
            expected,
            amqp_topics={
                "org_unit.association.create": 2,
            },
        )

    def test_create_association_from_missing_unit(self):
        self.load_sample_structures()

        unitid = "00000000-0000-0000-0000-000000000000"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "address": {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefonnummer",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "value": "33369696",
                },
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Org unit not found.",
                "error": True,
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
            json=payload,
            status_code=404,
        )

    def test_create_association_fails_on_two_assocations(self):
        """An employee cannot have more than one active association per org
        unit"""
        self.load_sample_structures()

        # These are the user/unit ids on the already existing association
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        payload = [
            {
                "type": "association",
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "address": {"uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "The employee already has an active "
                "association with the given org unit.",
                "error": True,
                "error_key": "V_MORE_THAN_ONE_ASSOCIATION",
                "existing": [
                    association_uuid,
                ],
                "status": 400,
            },
            json=payload,
            status_code=400,
        )

    def test_create_association_with_preexisting(self):
        """An employee cannot have more than one active association per org
        unit"""
        self.load_sample_structures()

        # These are the user/unit ids on the already existing association
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        self.assertRequestResponse(
            "/service/details/terminate",
            [association_uuid],
            json=[
                {
                    "type": "association",
                    "uuid": association_uuid,
                    "validity": {"to": "2017-02-01"},
                },
            ],
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )

        self.assertRequest(
            "/service/details/create",
            json=[
                {
                    "type": "association",
                    "org_unit": {"uuid": unitid},
                    "person": {"uuid": userid},
                    "association_type": {
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "address": {
                        "address_type": {
                            "example": "20304060",
                            "name": "Telefonnummer",
                            "scope": "PHONE",
                            "user_key": "Telefon",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        },
                        "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                        "value": "33369696",
                    },
                    "validity": {
                        "from": "2018-01-01",
                        "to": None,
                    },
                }
            ],
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

    def test_create_association_no_unit(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "address": {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "AdressePost",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                    },
                    "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                },
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Missing org_unit",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "org_unit",
                "obj": payload[0],
                "status": 400,
            },
            json=payload,
            status_code=400,
        )

    def test_create_association_fails_on_empty_payload(self):
        self.load_sample_structures()

        payload = [
            {
                "type": "association",
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Missing org_unit",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "org_unit",
                "obj": {"type": "association"},
                "status": 400,
            },
            json=payload,
            status_code=400,
        )

    def test_create_association_with_dynamic_classes(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        association_uuid = "00000000-0000-0000-0000-000000000000"
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
        classid = "cafebabe-c370-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "association",
                "uuid": association_uuid,
                "dynamic_classes": [{"uuid": classid}],
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": "1234",
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": userid,
                    }
                ],
                "tilknyttedeklasser": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": classid,
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": unitid,
                    }
                ],
                "primær": [
                    {
                        "uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474",
                        "virkning": {
                            "from": "2017-12-01 00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 00:00:00+01",
                            "to_included": False,
                        },
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
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "Tilknytning",
                    }
                ]
            },
        }

        associations = mora.async_util.async_to_sync(c.organisationfunktion.fetch)(
            tilknyttedebrugere=userid, funktionsnavn="Tilknytning"
        )
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            associationid
        )

        self.assertRegistrationsEqual(actual_association, expected)

        expected = [
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [{"uuid": "cafebabe-c370-4502-81c2-7697009c9053"}],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "substitute": None,
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            }
        ]

        self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1".format(userid),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

    @patch(
        "mora.conf_db.get_configuration",
        return_value={"substitute_roles": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
    )
    def test_edit_association(self, mock):
        self.load_sample_structures()

        # Check the POST request
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "dynamic_classes": [],
                "data": {
                    "association_type": {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                    },
                    "substitute": {"uuid": "3afe52b2-6dc1-4ebf-ab27-790ee2931604"},
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/edit",
            [association_uuid],
            json=req,
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

        self.assertRequestResponse(
            "/service/ou/{}/details/association?only_primary_uuid=1".format(unitid),
            [
                {
                    "association_type": {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                    },
                    "dynamic_classes": [],
                    "org_unit": {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    },
                    "person": {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    },
                    "primary": None,
                    "user_key": "bvn",
                    "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                    "substitute": {"uuid": "3afe52b2-6dc1-4ebf-ab27-790ee2931604"},
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                }
            ],
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )
        with self.subTest("change to vacant"):
            new_req = copy.deepcopy(req)
            new_req[0]["data"]["person"] = None
            self.assertRequestResponse(
                "/service/details/edit",
                [association_uuid],
                json=new_req,
                amqp_topics={
                    "employee.association.update": 1,
                    "org_unit.association.update": 2,
                },
            )

            self.assertRequestResponse(
                "/service/ou/{}/details/association?only_primary_uuid=1".format(unitid),
                [
                    {
                        "association_type": {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        },
                        "dynamic_classes": [],
                        "org_unit": {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        },
                        "person": None,
                        "primary": None,
                        "user_key": "bvn",
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "substitute": {"uuid": "3afe52b2-6dc1-4ebf-ab27-790ee2931604"},
                        "validity": {
                            "from": "2017-01-01",
                            "to": None,
                        },
                    }
                ],
                amqp_topics={
                    "employee.association.update": 1,
                    "org_unit.association.update": 2,
                },
            )

    @patch(
        "mora.conf_db.get_configuration",
        return_value={"substitute_roles": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
    )
    def test_edit_association_substitute(self, mock):
        """Test that substitute field is removed when writing an association
        type that is not meant to have substitutes"""
        self.load_sample_structures()

        # Check the POST request
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
        subid = "3afe52b2-6dc1-4ebf-ab27-790ee2931604"

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "dynamic_classes": [],
                "data": {
                    "association_type": {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                    },
                    "substitute": {"uuid": subid},
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/edit",
            [association_uuid],
            json=req,
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "dynamic_classes": [],
                "data": {
                    "association_type": {
                        "uuid": "46de8c9f-ecbe-4638-8b2b-386845729c9a"
                    },
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/edit",
            [association_uuid],
            json=req,
            amqp_topics={
                "employee.association.update": 2,
                "org_unit.association.update": 2,
            },
        )

        self.assertRequestResponse(
            "/service/ou/{}/details/association?only_primary_uuid=1".format(unitid),
            [
                {
                    "association_type": {
                        "uuid": "46de8c9f-ecbe-4638-8b2b-386845729c9a",
                    },
                    "dynamic_classes": [],
                    "org_unit": {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    },
                    "person": {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    },
                    "primary": None,
                    "user_key": "bvn",
                    "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                    "substitute": None,
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                }
            ],
            amqp_topics={
                "employee.association.update": 2,
                "org_unit.association.update": 2,
            },
        )

        self.assertRequestResponse(
            "/service/ou/{}/details/association?only_primary_uuid=1".format(subid),
            [],
            amqp_topics={
                "employee.association.update": 2,
                "org_unit.association.update": 2,
            },
        )

    def test_edit_association_with_preexisting(self):
        """Only one active association is allowed for each employee in each
        org unit"""
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        payload = {
            "type": "association",
            "org_unit": {"uuid": unitid},
            "person": {"uuid": userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [],
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }

        self.assertRequest(
            "/service/details/create",
            json=payload,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        associations = mora.async_util.async_to_sync(c.organisationfunktion.fetch)(
            tilknyttedeenheder=unitid,
            tilknyttedebrugere=userid,
            funktionsnavn=mapping.ASSOCIATION_KEY,
        )
        self.assertEqual(len(associations), 1)
        existing_uuid = associations[0]

        with self.subTest("validation"):
            req = [
                {
                    "type": "association",
                    "uuid": association_uuid,
                    "data": {
                        "validity": {
                            "from": "2017-12-01",
                            "to": "2017-12-01",
                        },
                        "org_unit": {"uuid": unitid},
                    },
                }
            ]

            self.assertRequestResponse(
                "/service/details/edit",
                {
                    "description": "The employee already has an active "
                    "association with the given org unit.",
                    "error": True,
                    "error_key": "V_MORE_THAN_ONE_ASSOCIATION",
                    "existing": [
                        existing_uuid,
                    ],
                    "status": 400,
                },
                json=req,
                status_code=400,
                amqp_topics={
                    "employee.association.create": 1,
                    "org_unit.association.create": 1,
                },
            )

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "data": {
                    "validity": {
                        "from": "2017-12-02",
                        "to": "2017-12-02",
                    },
                    "org_unit": {"uuid": unitid},
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/edit",
            [
                association_uuid,
            ],
            json=req,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

    def test_edit_association_move(self):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "b688513d-11f7-4efc-b679-ab082a2055d0"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "data": {
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2018-04-01",
                        "to": "2019-03-31",
                    },
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/edit",
            [association_uuid],
            json=req,
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

        expected_association = {
            "note": "Rediger tilknytning",
            "relationer": {
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2019-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "2019-04-01 00:00:00+02",
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
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
                            "to": "infinity",
                        },
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
                            "to": "infinity",
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning",
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual_association = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            association_uuid
        )

        self.assertRegistrationsEqual(expected_association, actual_association)

        expected = [
            {
                "association_type": {
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                },
                "dynamic_classes": [],
                "org_unit": {
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                },
                "person": {
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                },
                "primary": None,
                "user_key": "bvn",
                "substitute": None,
                "uuid": association_uuid,
                "validity": {
                    "from": "2018-04-01",
                    "to": "2019-03-31",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/e/{}/details/association?at=2018-06-01"
            "&only_primary_uuid=1".format(userid),
            expected,
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

    def test_terminate_association_via_user(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {"validity": {"to": "2017-11-30"}}
        self.assertRequestResponse(
            "/service/e/{}/terminate".format(userid),
            userid,
            json=payload,
            amqp_topics={
                "employee.employee.delete": 1,
                "employee.association.delete": 1,
                "employee.engagement.delete": 1,
                "employee.manager.delete": 1,
                "employee.address.delete": 1,
                "employee.role.delete": 1,
                "employee.it.delete": 1,
                "employee.leave.delete": 1,
                "org_unit.association.delete": 1,
                "org_unit.engagement.delete": 1,
                "org_unit.manager.delete": 1,
                "org_unit.role.delete": 1,
            },
        )

        expected = {
            "note": "Afsluttet",
            "relationer": {
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
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
                            "to": "2017-12-01 00:00:00+01",
                        },
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity",
                        },
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
                            "to": "infinity",
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Tilknytning",
                    }
                ]
            },
        }

        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        actual_association = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            association_uuid
        )

        # drop lora-generated timestamps & users
        del (
            actual_association["fratidspunkt"],
            actual_association["tiltidspunkt"],
            actual_association["brugerref"],
        )

        self.assertEqual(actual_association, expected)


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class AddressTests(tests.cases.LoRATestCase):
    maxDiff = None

    def test_terminate_association_directly(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        associationid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        payload = {
            "type": "association",
            "uuid": associationid,
            "validity": {"to": "2017-11-30"},
        }

        orig = self.assertRequest(
            "/service/e/{}/details/association" "?validity=present".format(userid),
        )

        expected = copy.deepcopy(orig)
        expected[0]["validity"]["to"] = "2017-11-30"

        self.assertRequestResponse(
            "/service/details/terminate",
            associationid,
            json=payload,
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )

        self.assertRequestResponse(
            "/service/e/{}/details/association" "?validity=past".format(userid),
            [],
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )

        self.assertRequestResponse(
            "/service/e/{}/details/association" "?validity=present".format(userid),
            expected,
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )

        self.assertRequestResponse(
            "/service/e/{}/details/association" "?validity=future".format(userid),
            [],
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )

    @freezegun.freeze_time("2018-01-01", tz_offset=1)
    def test_terminate_association_in_the_past(self):
        self.load_sample_structures()

        # Check the POST request
        associationid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

        self.assertRequestFails(
            "/service/details/terminate",
            200,
            json={
                "type": "association",
                "uuid": associationid,
                "validity": {"to": "2017-11-30"},
            },
            amqp_topics={
                "employee.association.delete": 1,
                "org_unit.association.delete": 1,
            },
        )
