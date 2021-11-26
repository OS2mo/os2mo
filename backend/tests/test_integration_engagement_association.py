# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import copy

import freezegun

import mora.async_util
from mora import lora
from tests.cases import LoRATestCase


class EngAssocUtils:
    association_uuid = "00000000-0000-0000-0000-000000000000"
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"
    engagement_association_type_uuid = "5695e331-d837-473f-9b00-6f528fbd23f6"
    user_key = "1234"
    validity = {
        "from": "2017-12-01",
        "to": "2018-12-01",
    }
    payload = [
        {
            "type": "engagement_association",
            "uuid": association_uuid,
            "org_unit": {
                "location": "",
                "name": "Kolding Kommune",
                "user_key": "Kolding Kommune",
                "uuid": unitid,
            },
            "engagement_association_type": {
                "example": None,
                "name": "k1",
                "owner": None,
                "scope": "TEXT",
                "user_key": "k1",
                "uuid": engagement_association_type_uuid,
            },
            "validity": validity,
            "engagement": {"uuid": engagement_uuid},
            "user_key": user_key,
        }
    ]

    @classmethod
    def create_payload(cls):
        return (
            cls.association_uuid,
            cls.unitid,
            cls.engagement_uuid,
            cls.engagement_association_type_uuid,
            cls.user_key,
            cls.validity,
            copy.deepcopy(cls.payload),
        )

    @classmethod
    def expected_created(cls):
        return [
            {
                "engagement": {"uuid": cls.engagement_uuid},
                "engagement_association_type": {
                    "uuid": cls.engagement_association_type_uuid
                },
                "org_unit": {"uuid": cls.unitid},
                "user_key": cls.user_key,
                "uuid": cls.association_uuid,
                "validity": cls.validity,
            }
        ]


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Tests(LoRATestCase):
    maxDiff = None

    def test_create_engagement_association(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        (
            association_uuid,
            unitid,
            engagement_uuid,
            engagement_association_type_uuid,
            user_key,
            validity,
            payload,
        ) = EngAssocUtils.create_payload()

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
        )

        expected = {
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2018-12-02 00:00:00+01",
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
                            "to": "2018-12-02 00:00:00+01",
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
                            "to": "2018-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "5695e331-d837-473f-9b00-6f528fbd23f6",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2018-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": unitid,
                    }
                ],
                "tilknyttedefunktioner": [
                    {
                        "uuid": engagement_uuid,
                        "objekttype": "engagement",
                        "virkning": {
                            "from": "2017-12-01 " "00:00:00+01",
                            "from_included": True,
                            "to": "2018-12-02 " "00:00:00+01",
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
                            "to": "2018-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "engagement_association",
                    }
                ]
            },
        }

        associations = mora.async_util.async_to_sync(c.organisationfunktion.fetch)(
            tilknyttedefunktioner=engagement_uuid,
            funktionsnavn="engagement_association",
        )
        self.assertEqual(len(associations), 1)
        associationid = associations[0]

        actual_association = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            associationid
        )

        self.assertRegistrationsEqual(expected, actual_association)

        expected = EngAssocUtils.expected_created()

        self.assertRequestResponse(
            "/api/v1/engagement_association/by_uuid"
            "?validity=future&only_primary_uuid=1&uuid={}".format(association_uuid),
            expected,
        )

    def test_create_association_fails_on_two_assocations(self):
        """An employee cannot have more than one active association per org
        unit"""
        self.load_sample_structures()

        # Check the POST request
        (
            association_uuid,
            unitid,
            engagement_uuid,
            engagement_association_type_uuid,
            user_key,
            validity,
            payload,
        ) = EngAssocUtils.create_payload()

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
        )

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

    def test_edit_association(self):
        """
        create then edit
        :return:
        """
        self.load_sample_structures()

        # Check the POST request
        #  ##### CREATE
        (
            association_uuid,
            unitid,
            engagement_uuid,
            engagement_association_type_uuid,
            user_key,
            validity,
            payload,
        ) = EngAssocUtils.create_payload()
        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
        )

        #  ##### EDIT
        engagement_association_type_uuid2 = "51cc63b8-d8d1-4b74-95df-7c105c9c88dd"
        payload_data = payload[0]
        edit_payload = {
            "type": payload_data.pop("type"),
            "uuid": payload_data.pop("uuid"),
            "data": payload_data,
        }
        payload_data["engagement_association_type"] = {
            "example": None,
            "name": "k2",
            "owner": None,
            "scope": "TEXT",
            "user_key": "k2",
            "uuid": engagement_association_type_uuid2,
        }

        self.assertRequestResponse(
            "/service/details/edit",
            association_uuid,
            json=edit_payload,
        )

        expected = [
            {
                "engagement": {"uuid": engagement_uuid},
                "engagement_association_type": {
                    "uuid": engagement_association_type_uuid2
                },
                "org_unit": {"uuid": unitid},
                "user_key": user_key,
                "uuid": association_uuid,
                "validity": validity,
            }
        ]

        self.assertRequestResponse(
            "/api/v1/engagement_association/by_uuid"
            "?validity=future&only_primary_uuid=1&uuid={}".format(association_uuid),
            expected,
        )

    def test_terminate_association_directly(self):
        """
        create then terminate
        :return:
        """
        self.load_sample_structures()

        # Check the POST request

        (
            association_uuid,
            unitid,
            engagement_uuid,
            engagement_association_type_uuid,
            user_key,
            validity,
            payload,
        ) = EngAssocUtils.create_payload()

        self.assertRequestResponse(
            "/service/details/create",
            [association_uuid],
            json=payload,
        )

        new_valid_to = "2017-12-30"
        expected = EngAssocUtils.expected_created()
        expected[0]["validity"]["to"] = new_valid_to

        payload = {
            "type": "engagement_association",
            "uuid": association_uuid,
            "validity": {"to": new_valid_to},
        }

        # ### TERMINATE
        self.assertRequestResponse(
            "/service/details/terminate",
            association_uuid,
            json=payload,
        )

        self.assertRequestResponse(
            "/api/v1/engagement_association/by_uuid"
            "?validity=future&only_primary_uuid=1&uuid={}".format(association_uuid),
            expected,
        )
