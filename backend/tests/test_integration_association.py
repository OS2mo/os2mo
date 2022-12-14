# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import copy
from functools import partial
from urllib.parse import urlencode
from uuid import uuid4

import freezegun
import pytest
from parameterized import parameterized

import tests.cases
from mora import lora
from mora import mapping
from tests.util import set_settings_contextmanager


_substitute_association = {"name": "i18n:substitute_association"}  # const
_substitute_uuid = "7626ad64-327d-481f-8b32-36c78eb12f8c"
_unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
_userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
_it_system_uuid = "0872fb72-926d-4c5c-a063-ff800b8ee697"
_it_user_uuid = "11111111-1111-1111-1111-111111111111"
_job_function_uuid = str(uuid4())


def _lora_virkning(**kwargs):
    virkning = {
        "virkning": {
            "from": "2017-12-01 00:00:00+01",
            "from_included": True,
            "to": "2017-12-02 00:00:00+01",
            "to_included": False,
        },
    }
    virkning.update(kwargs)
    return virkning


def _lora_organisationfunktion(**kwargs):
    doc = {
        "livscykluskode": "Importeret",
        "tilstande": {
            "organisationfunktiongyldighed": [
                _lora_virkning(gyldighed="Aktiv"),
            ]
        },
        "note": "Oprettet i MO",
        "relationer": {
            "tilknyttedeorganisationer": [
                _lora_virkning(uuid="456362c4-0ee4-4e5e-a72c-751239745e62"),
            ],
            "tilknyttedebrugere": [
                _lora_virkning(uuid=_userid),
            ],
            "organisatoriskfunktionstype": [
                _lora_virkning(uuid="62ec821f-4179-4758-bfdf-134529d186e9"),
            ],
            "tilknyttedeenheder": [
                _lora_virkning(uuid=_unitid),
            ],
            "primær": [
                _lora_virkning(uuid="f49c797b-d3e8-4dc2-a7a8-c84265432474"),
            ],
        },
        "attributter": {
            "organisationfunktionegenskaber": [
                _lora_virkning(brugervendtnoegle="1234", funktionsnavn="Tilknytning"),
            ]
        },
    }

    for key, val in kwargs.items():
        if key in doc:
            doc[key].update(val)

    return doc


def _mo_create_it_user_doc():
    return {
        "type": "it",
        "uuid": _it_user_uuid,
        "itsystem": {"uuid": _it_system_uuid},
        "user_key": "usernameInItSystem",
        "person": {"uuid": _userid},
        "org_unit": {"uuid": _unitid},
        "engagement": None,
        "validity": {"from": "2017-01-01", "to": None},
    }


def _mo_return_it_user_doc():
    doc = _mo_create_it_user_doc()
    del doc["type"]
    doc["primary"] = None
    return doc


@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class AsyncTests(tests.cases.AsyncLoRATestCase):
    maxDiff = None

    @parameterized.expand(
        [
            # 1. Test usage of "substitute" property on associations
            (
                # MO payload: extra data
                {
                    "substitute": {"uuid": _substitute_uuid},
                },
                # MO response: expected extra data
                {
                    "substitute": {"uuid": _substitute_uuid},
                    "it": None,
                    "job_function": None,
                },
                # LoRa response: expected extra data
                {
                    "relationer": {
                        "tilknyttedefunktioner": [_lora_virkning(uuid=_substitute_uuid)]
                    }
                },
            ),
            # 2. Test usage of "it" and "job_function" properties on associations
            (
                # MO payload: extra data
                {
                    "it": {"uuid": _it_user_uuid},
                    "job_function": {"uuid": _job_function_uuid},
                },
                # MO response: expected extra data
                {
                    "substitute": None,
                    "it": [_mo_return_it_user_doc()],
                    "job_function": {"uuid": _job_function_uuid},
                },
                # LoRa response: expected extra data
                {
                    "relationer": {
                        "tilknyttedeitsystemer": [_lora_virkning(uuid=_it_user_uuid)],
                        "tilknyttedefunktioner": [
                            _lora_virkning(uuid=_job_function_uuid)
                        ],
                    }
                },
            ),
        ]
    )
    async def test_create_association(self, mo_data, mo_expected, lora_expected):
        def url(employee_uuid: str, **kwargs):
            base = f"/service/e/{employee_uuid}/details/association"
            args = {"validity": "future", "only_primary_uuid": "1"}
            if "it" in mo_data and "first_party_perspective" not in kwargs:
                args.update(it="1")
            if kwargs:
                args.update(**kwargs)
            return f"{base}?{urlencode(args)}"

        seed_substitute_roles = partial(
            set_settings_contextmanager,
            confdb_substitute_roles="62ec821f-4179-4758-bfdf-134529d186e9",
        )

        # Create an "IT User" (aka. "IT system binding")
        await self.request("/service/details/create", json=_mo_create_it_user_doc())

        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        association_uuid = "00000000-0000-0000-0000-000000000000"

        payload = [
            {
                "type": "association",
                "uuid": association_uuid,
                "org_unit": {"uuid": _unitid},
                "person": {"uuid": _userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": "1234",
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            }
        ]

        payload[0].update(mo_data)

        with seed_substitute_roles():
            await self.assertRequestResponse(
                "/service/details/create",
                [association_uuid],
                json=payload,
                amqp_topics={
                    "employee.association.create": 1,
                    "org_unit.association.create": 1,
                },
            )

        # Check that we created the expected "organisationfunktion" in LoRa
        expected = _lora_organisationfunktion(**lora_expected)
        associations = await c.organisationfunktion.fetch(
            tilknyttedebrugere=_userid, funktionsnavn="Tilknytning"
        )
        assert len(associations) == 1
        associationid = associations[0]
        actual_association = await c.organisationfunktion.get(associationid)
        self.assertRegistrationsEqual(actual_association, expected)

        # Check that we get the expected response from MO, case 1
        expected = {
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [],
            "org_unit": {"uuid": _unitid},
            "person": {"uuid": _userid},
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "user_key": "1234",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
        }
        expected.update(mo_expected)
        with seed_substitute_roles():
            await self.assertRequestResponse(
                url(_userid),
                [expected],
                amqp_topics={
                    "employee.association.create": 1,
                    "org_unit.association.create": 1,
                },
            )

        # Check that we get the expected response from MO, case 2
        expected = {
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [],
            "org_unit": {"uuid": _unitid},
            "person": {"uuid": _userid},
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "user_key": "1234",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            "first_party_association_type": {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
            },
            "third_party_associated": {"uuid": _substitute_uuid},
            "third_party_association_type": _substitute_association,
        }
        expected.update(mo_expected)
        with seed_substitute_roles():
            await self.assertRequestResponse(
                url(_userid, first_party_perspective="1"),
                [expected] if "it" not in mo_data else [],
                amqp_topics={
                    "employee.association.create": 1,
                    "org_unit.association.create": 1,
                },
            )

        # Check that we get the expected response from MO, case 3
        await self.assertRequestResponse(
            url(_substitute_uuid),
            [],
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

        # Check that we get the expected response from MO, case 2
        expected = {
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [],
            "org_unit": {"uuid": _unitid},
            "person": {"uuid": _userid},
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "user_key": "1234",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            "first_party_association_type": _substitute_association,
            "third_party_associated": {"uuid": _userid},
            "third_party_association_type": {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
            },
        }
        expected.update(mo_expected)
        with seed_substitute_roles():
            await self.assertRequestResponse(
                url(_substitute_uuid, first_party_perspective="1"),
                [expected] if "it" not in mo_data else [],
                amqp_topics={
                    "employee.association.create": 1,
                    "org_unit.association.create": 1,
                },
            )

    async def test_create_vacant_association(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        # test multiple valid formats
        association_uuid = "00000000-0000-0000-0000-000000000000"
        association_uuid2 = "00000000-0000-0000-0000-000000000001"

        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

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
                "it": None,
                "job_function": None,
            }
            if include_person:
                main["person"] = None
            return [main]

        with set_settings_contextmanager(
            confdb_substitute_roles="62ec821f-4179-4758-bfdf-134529d186e9"
        ):
            await self.assertRequestResponse(
                "/service/details/create",
                [association_uuid],
                json=payload(association_uuid),
                amqp_topics={
                    "org_unit.association.create": 1,
                },
            )
            await self.assertRequestResponse(
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
                        "uuid": subid,
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

        associations = await c.organisationfunktion.fetch(
            tilknyttedeenheder=unitid,
            tilknyttedeorganisationer="456362c4-0ee4-4e5e-a72c-751239745e62",
            brugervendtnoegle="1234",
            funktionsnavn="Tilknytning",
        )
        assert len(associations) == 2
        for associationid in associations:
            # assert we got back one of the newly created associations (ie. exists)
            assert associationid in (association_uuid, association_uuid2)

            # check that the content is also as expected
            actual_association = await c.organisationfunktion.get(associationid)

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
                "org_unit": {"uuid": unitid},
                "person": None,
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": assoc_uuid,
                "substitute": {"uuid": subid},
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
                "it": None,
                "job_function": None,
            }

        expected = [
            assoc_content_only_primary_uuid(association_uuid),
            assoc_content_only_primary_uuid(association_uuid2),
        ]

        with set_settings_contextmanager(
            confdb_substitute_roles="62ec821f-4179-4758-bfdf-134529d186e9"
        ):
            await self.assertRequestResponse(  # contains sorting (ie. unordered comparison)
                "/service/ou/{}/details/association"
                "?validity=future&only_primary_uuid=1".format(unitid),
                expected,
                amqp_topics={
                    "org_unit.association.create": 2,
                },
            )

    async def test_create_association_with_dynamic_classes(self):
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

        await self.assertRequestResponse(
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

        associations = await c.organisationfunktion.fetch(
            tilknyttedebrugere=userid, funktionsnavn="Tilknytning"
        )
        assert len(associations) == 1
        associationid = associations[0]

        actual_association = await c.organisationfunktion.get(associationid)

        self.assertRegistrationsEqual(actual_association, expected)

        expected = [
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [{"uuid": "cafebabe-c370-4502-81c2-7697009c9053"}],
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
                "user_key": "1234",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "substitute": None,
                "validity": {"from": "2017-12-01", "to": "2017-12-01"},
                "it": None,
                "job_function": None,
            }
        ]

        await self.assertRequestResponse(
            "/service/e/{}/details/association"
            "?validity=future&only_primary_uuid=1".format(userid),
            expected,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

    async def test_edit_association_with_preexisting(self):
        """More than one active association is allowed for each employee in each
        org unit"""

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

        await self.assertRequest(
            "/service/details/create",
            json=payload,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
            },
        )

        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        associations = await c.organisationfunktion.fetch(
            tilknyttedeenheder=unitid,
            tilknyttedebrugere=userid,
            funktionsnavn=mapping.ASSOCIATION_KEY,
        )
        assert len(associations) == 1

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

            await self.assertRequestResponse(
                "/service/details/edit",
                [association_uuid],
                json=req,
                status_code=200,
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

        await self.assertRequestResponse(
            "/service/details/edit",
            [association_uuid],
            json=req,
            amqp_topics={
                "employee.association.create": 1,
                "org_unit.association.create": 1,
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

    async def test_edit_association_move(self):
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

        await self.assertRequestResponse(
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
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
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
        actual_association = await c.organisationfunktion.get(association_uuid)

        self.assertRegistrationsEqual(expected_association, actual_association)

        expected = [
            {
                "association_type": {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
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
                "it": None,
                "job_function": None,
            }
        ]

        await self.assertRequestResponse(
            "/service/e/{}/details/association?at=2018-06-01"
            "&only_primary_uuid=1".format(userid),
            expected,
            amqp_topics={
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

    async def test_terminate_association_via_user(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {"validity": {"to": "2017-11-30"}}
        await self.assertRequestResponse(
            f"/service/e/{userid}/terminate",
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
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
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

        actual_association = await c.organisationfunktion.get(association_uuid)

        # drop lora-generated timestamps & users
        del (
            actual_association["fratidspunkt"],
            actual_association["tiltidspunkt"],
            actual_association["brugerref"],
        )

        assert actual_association == expected


@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Tests(tests.cases.LoRATestCase):
    maxDiff = None

    def test_create_association_from_missing_unit(self):
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

    def test_create_association_succeeds_on_two_associations(self):
        """An employee can have more than one active association per org unit"""

        # These are the user/unit ids on the already existing association
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

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

        self.assertRequest(
            "/service/details/create",
            json=payload,
            status_code=201,
        )

    def test_create_association_with_preexisting(self):
        """An employee cannot have more than one active association per org
        unit"""
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

    @set_settings_contextmanager(
        confdb_substitute_roles="bcd05828-cc10-48b1-bc48-2f0d204859b2"
    )
    def test_edit_association(self):
        # Check the POST request
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
        subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

        req = [
            {
                "type": "association",
                "uuid": association_uuid,
                "dynamic_classes": [],
                "data": {
                    "association_type": {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                    },
                    "substitute": {
                        "uuid": subid,
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
                "employee.association.update": 1,
                "org_unit.association.update": 1,
            },
        )

        self.assertRequestResponse(
            f"/service/ou/{unitid}/details/association?only_primary_uuid=1",
            [
                {
                    "association_type": {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                    },
                    "dynamic_classes": [],
                    "org_unit": {
                        "uuid": unitid,
                    },
                    "person": {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    },
                    "primary": None,
                    "user_key": "bvn",
                    "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                    "substitute": {
                        "uuid": subid,
                    },
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                    "it": None,
                    "job_function": None,
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
                f"/service/ou/{unitid}/details/association?only_primary_uuid=1",
                [
                    {
                        "association_type": {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        },
                        "dynamic_classes": [],
                        "org_unit": {
                            "uuid": unitid,
                        },
                        "person": None,
                        "primary": None,
                        "user_key": "bvn",
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "substitute": {
                            "uuid": subid,
                        },
                        "validity": {
                            "from": "2017-01-01",
                            "to": None,
                        },
                        "it": None,
                        "job_function": None,
                    }
                ],
                amqp_topics={
                    "employee.association.update": 1,
                    "org_unit.association.update": 2,
                },
            )

    @set_settings_contextmanager(
        confdb_substitute_roles="bcd05828-cc10-48b1-bc48-2f0d204859b2"
    )
    def test_edit_association_substitute(self):
        """Test that substitute field is removed when writing an association
        type that is not meant to have substitutes"""
        # Check the POST request
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
        subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

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
            f"/service/ou/{unitid}/details/association?only_primary_uuid=1",
            [
                {
                    "association_type": {
                        "uuid": "46de8c9f-ecbe-4638-8b2b-386845729c9a",
                    },
                    "dynamic_classes": [],
                    "org_unit": {
                        "uuid": unitid,
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
                    "it": None,
                    "job_function": None,
                }
            ],
            amqp_topics={
                "employee.association.update": 2,
                "org_unit.association.update": 2,
            },
        )

        self.assertRequestResponse(
            f"/service/ou/{subid}/details/association?only_primary_uuid=1",
            [],
            amqp_topics={
                "employee.association.update": 2,
                "org_unit.association.update": 2,
            },
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class AddressTests(tests.cases.LoRATestCase):
    maxDiff = None

    def test_terminate_association_directly(self):
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
