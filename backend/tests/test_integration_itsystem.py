#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Writing(util.LoRATestCase):
    maxDiff = None

    @classmethod
    def get_lora_environ(cls):
        # force LoRA to run under a UTC timezone, ensuring that we
        # handle this case correctly for writing
        return {
            'TZ': 'UTC',
        }

    def test_errors(self):
        self.load_sample_structures(minimal=True)

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'error': True,
                'error_key': 'E_INVALID_TYPE',
                'description': (
                    'Invalid \'itsystem\', expected dict, got: null'
                ),
                'key': 'itsystem',
                'expected': 'dict',
                'actual': 'null',
                'status': 400,
                'obj': {
                    'itsystem': None,
                    'type': 'it',
                    'validity': {
                        'from': '2017-12-01', 'to': None
                    }
                },
            },
            json=[
                {
                    "type": "it",
                    "itsystem": None,
                    "validity": {
                        "from": "2017-12-01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/create',
            {
                'error': True,
                'error_key': 'E_NOT_FOUND',
                'description': 'Not found.',
                'status': 404,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    },
                    "validity": {
                        "from": "2017-12-01",
                        "to": None,
                    },
                },
            ],
            status_code=404,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/create',
            {
                'error': True,
                'error_key': 'E_INVALID_TYPE',
                'description': (
                    'Invalid \'itsystem\', expected dict, got: null'
                ),
                'key': 'itsystem',
                'expected': 'dict',
                'actual': 'null',
                'status': 400,
                'obj': {
                    'itsystem': None,
                    'type': 'it',
                    'validity': {
                        'from': '2017-12-01',
                        'to': None
                    }
                },
            },
            json=[
                {
                    "type": "it",
                    "itsystem": None,
                    "validity": {
                        "from": "2017-12-01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'error': True,
                'error_key': 'V_MISSING_START_DATE',
                'description': 'Missing start date.',
                'status': 400,
                'obj': {
                    'itsystem': {
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb'},
                    'type': 'it',
                    'validity': {
                        'from': None, 'to': None
                    }
                },
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    },
                    "validity": {
                        "from": None,
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'description': 'invalid input syntax for uuid: "None"',
                'error': True,
                'error_key': 'E_INVALID_INPUT',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {},
                    "validity": {
                        "from": None,
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'error': True,
                'error_key': 'E_INVALID_UUID',
                'description': "Invalid uuid for 'uuid': '42'",
                'status': 400,
                'obj': {'uuid': '42'},
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '42',
                    },
                    "validity": {
                        "from": "2017-12-01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {
                'description': 'Not found.',
                'error': True,
                'error_key': 'E_NOT_FOUND',
                'status': 404,
            },
            json=[
                {
                    "type": "it",
                    # WRONG:
                    'uuid': '00000000-0000-0000-0000-000000000000',
                    "original": {
                        'name': 'Active Directory',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'AD',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        "validity": {
                            'from': '1932-05-12',
                            'to': None,
                        },
                    },
                    "data": {
                        "validity": {
                            "to": '2019-12-31',
                        },
                    },
                },
            ],
            status_code=404,
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {
                'description': 'Missing uuid',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'uuid',
                'obj': {
                    'type': 'it',
                    'data': {'uuid': None},
                    'original': {
                        'name': 'Active Directory',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'AD',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        'validity': {'from': '1932-05-12', 'to': None},
                    },
                },
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "original": {
                        'name': 'Active Directory',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'AD',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        "validity": {
                            'from': '1932-05-12',
                            'to': None,
                        },
                    },
                    "data": {
                        'uuid': None,
                    },
                },
            ],
            status_code=400,
        )

    def test_create_employee_itsystem(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/e/{}/details/it?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/it'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/it?validity=future'.format(userid),
                [],
            )

        self.assertEqual(
            list(c.organisationfunktion.get_all(
                funktionsnavn='IT-system',
                tilknyttedebrugere=userid,
            )),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "it",
                    "user_key": "goofy-moofy",
                    "itsystem": {
                        "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
                    },
                    "validity": {
                        "from": "2018-09-01",
                        "to": None
                    }
                },
            ],
        )

        (funcid, func), = c.organisationfunktion.get_all(
            funktionsnavn='IT-system',
            tilknyttedebrugere=userid,
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=future'.format(userid),
            [
                {
                    "itsystem": {
                        "name": "Lokal Rammearkitektur",
                        "reference": None,
                        "system_type": None,
                        "user_key": "LoRa",
                        "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
                        "validity": {
                            "from": "2010-01-01",
                            "to": None
                        }
                    },
                    "org_unit": None,
                    "person": {
                        "name": "Fedtmule",
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    },
                    "user_key": "goofy-moofy",
                    "uuid": funcid,
                    "validity": {
                        "from": "2018-09-01",
                        "to": None
                    }
                }
            ],
        )

    @freezegun.freeze_time('2018-01-01', tz_offset=1)
    def test_edit_employee_itsystem(self):
        self.load_sample_structures()

        user_id = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        function_id = "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66"

        original = {
            "itsystem": {
                "name": "Active Directory",
                "reference": None,
                "system_type": None,
                "user_key": "AD",
                "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
                "validity": {
                    "from": "2002-02-14",
                    "to": None,
                }
            },
            "org_unit": None,
            "person": {
                "name": "Anders And",
                "uuid": user_id,
            },
            "user_key": "donald",
            "uuid": function_id,
            "validity": {
                "from": "2017-01-01",
                "to": None,
            }
        }

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/e/{}/details/it'.format(user_id),
                [original],
            )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(user_id),
            user_id,
            json=[
                {
                    "type": "it",
                    "uuid": function_id,
                    "original": original,
                    "data": {
                        "itsystem": {
                            "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
                        },
                        "validity": {
                            "from": "2017-06-01",
                            "to": "2018-06-01",
                        }
                    }
                }
            ],
        )

        updated = copy.deepcopy(original)
        updated.update(
            itsystem={
                'name': 'Lokal Rammearkitektur',
                'reference': None,
                'system_type': None,
                'user_key': 'LoRa',
                'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                'validity': {'from': '2010-01-01', 'to': None},
            },
            validity={
                "from": "2017-06-01",
                "to": "2018-06-01",
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=past'.format(user_id),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(user_id),
            [updated],
        )


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Reading(util.LoRATestCase):
    def test_reading_organisation(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/it/',
            [

                {
                    'system_type': None,
                    'user_key': 'LoRa',
                    'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    'name': 'Lokal Rammearkitektur',
                },
                {
                    'system_type': None,
                    'user_key': 'AD',
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    'name': 'Active Directory',
                }
            ],
        )

    def test_reading_employee(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it',
            [
                {
                    'itsystem': {
                        'name': 'Active Directory',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'AD',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        'validity': {'from': '2002-02-14', 'to': None},
                    },
                    'org_unit': None,
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
                    'user_key': 'donald',
                    'uuid': 'aaa8c495-d7d4-4af1-b33a-f4cb27b82c66',
                    'validity': {'from': '2017-01-01', 'to': None},
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it'
            '?validity=past',
            [],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it'
            '?validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it'
            '?at=2016-06-01',
            [],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it'
            '?at=2016-06-01&validity=future',
            [
                {
                    'itsystem': {
                        'name': 'Active Directory',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'AD',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        'validity': {'from': '2002-02-14', 'to': None},
                    },
                    'org_unit': None,
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'user_key': 'donald',
                    'uuid': 'aaa8c495-d7d4-4af1-b33a-f4cb27b82c66',
                    'validity': {'from': '2017-01-01', 'to': None},
                },
            ],
        )

    def test_reading_unit(self):
        self.load_sample_structures()

        for unitid in (
            '2874e1dc-85e6-4269-823a-e1125484dfd3',
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            'b688513d-11f7-4efc-b679-ab082a2055d0',
            '85715fc7-925d-401b-822d-467eb4b163b6',
            'da77153e-30f3-4dc2-a611-ee912a28d8aa',
        ):
            for validity in ('past', 'present', 'future'):
                with self.subTest('{} - {}'.format(unitid, validity)):
                    self.assertRequestResponse(
                        '/service/ou/{}/details/it?validity={}'.format(
                            unitid, validity,
                        ),
                        [],
                    )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it',
            [
                {
                    'itsystem': {
                        'name': 'Lokal Rammearkitektur',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'LoRa',
                        'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                        'validity': {'from': '2010-01-01', 'to': None},
                    },
                    'org_unit': {
                        'name': 'Afdeling for Samtidshistorik',
                        'user_key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
                    },
                    'person': None,
                    'user_key': 'fwaf',
                    'uuid': 'cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276',
                    'validity': {'from': '2017-01-01', 'to': '2017-12-31'},
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?validity=past',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2016-06-01',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2016-06-01&validity=future',
            [
                {
                    'itsystem': {
                        'name': 'Lokal Rammearkitektur',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'LoRa',
                        'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                        'validity': {'from': '2010-01-01', 'to': None},
                    },
                    'org_unit': {
                        'name': 'Afdeling for Fortidshistorik',
                        'user_key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
                    },
                    'person': None,
                    'user_key': 'fwaf',
                    'uuid': 'cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276',
                    'validity': {'from': '2017-01-01', 'to': '2017-12-31'},
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2016-06-01&validity=past',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2018-06-01&validity=present',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2018-06-01&validity=past',
            [
                {
                    'itsystem': {
                        'name': 'Lokal Rammearkitektur',
                        'reference': None,
                        'system_type': None,
                        'user_key': 'LoRa',
                        'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                        'validity': {'from': '2010-01-01', 'to': None},
                    },
                    'org_unit': {
                        'name': 'Afdeling for Fortidshistorik',
                        'user_key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
                    },
                    'person': None,
                    'user_key': 'fwaf',
                    'uuid': 'cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276',
                    'validity': {'from': '2017-01-01', 'to': '2017-12-31'},
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/it'
            '?at=2018-06-01&validity=future',
            [],
        )
