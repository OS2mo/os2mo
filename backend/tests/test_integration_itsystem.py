#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import logging

import freezegun
import pytest

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

    @pytest.mark.psql_9_dependent
    def test_errors(self):
        # In Postgres 10.0 the messages mentioning type names was changed. See
        # https://github.com/postgres/postgres/commit/9a34123bc315e55b33038464422ef1cd2b67dab2
        # This test will fail if run against postgres >=10.0. We can ignore it
        # with `pytest -m "not psql_9_dependent"`.
        self.load_sample_structures(minimal=True)

        self.assertRequestResponse(
            '/service/details/create',
            {
                'description': 'Missing itsystem',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'itsystem',
                'obj': {
                    'itsystem': None,
                    'type': 'it',
                    'validity': {'from': '2017-12-01', 'to': None},
                },
                'status': 400,
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
            '/service/details/create',
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
            '/service/details/create',
            {
                'description': 'Missing itsystem',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'itsystem',
                'obj': {
                    'itsystem': None,
                    'type': 'it',
                    'validity': {'from': '2017-12-01', 'to': None},
                },
                'status': 400,
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
            '/service/details/create',
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
            '/service/details/create',
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
            '/service/details/create',
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
            '/service/details/edit',
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
            '/service/details/edit',
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

        funcid, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "it",
                    "user_key": "goofy-moofy",
                    "person": {
                        "uuid": userid,
                    },
                    "itsystem": {
                        "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
                    },
                    "validity": {
                        "from": "2018-09-01",
                        "to": None
                    }
                },
            ],
            amqp_topics={'employee.it.create': 1},
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=past'.format(userid),
            [],
            amqp_topics={'employee.it.create': 1},
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [],
            amqp_topics={'employee.it.create': 1},
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
                        "name": "Fedtmule Hund",
                        "givenname": "Fedtmule",
                        "surname": "Hund",
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
            amqp_topics={'employee.it.create': 1},
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
                "givenname": "Anders",
                "surname": "And",
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
            '/service/details/edit',
            [function_id],
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
                            "from": "2018-01-01",
                            "to": "2018-06-01",
                        }
                    }
                }
            ],
            amqp_topics={'employee.it.update': 1},
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
                "from": "2018-01-01",
                "to": "2018-06-01",
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=past'.format(user_id),
            [],
            amqp_topics={'employee.it.update': 1},
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(user_id),
            [updated],
            amqp_topics={'employee.it.update': 1},
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=future'.format(user_id),
            [],
            amqp_topics={'employee.it.update': 1},
        )

    def test_create_unit_itsystem(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "b688513d-11f7-4efc-b679-ab082a2055d0"

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/it?validity=past'.format(unitid),
                [],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/it'.format(unitid),
                [],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/it?validity=future'.format(unitid),
                [],
            )

        self.assertEqual(
            list(c.organisationfunktion.get_all(
                funktionsnavn='IT-system',
                tilknyttedebrugere=unitid,
            )),
            [],
        )

        funcid, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "it",
                    "user_key": "root",
                    "org_unit": {
                        "uuid": unitid,
                    },
                    "itsystem": {
                        "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
                    },
                    "validity": {
                        "from": "2018-09-01",
                        "to": None
                    }
                },
            ],
            amqp_topics={'org_unit.it.create': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it?validity=past'.format(unitid),
            [],
            amqp_topics={'org_unit.it.create': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it'.format(unitid),
            [],
            amqp_topics={'org_unit.it.create': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it?validity=future'.format(unitid),
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
                    "org_unit": {
                        'name': 'Samfundsvidenskabelige fakultet',
                        'user_key': 'samf',
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                        'validity': {'from': '2017-01-01', 'to': None},
                    },
                    "person": None,
                    "user_key": "root",
                    "uuid": funcid,
                    "validity": {
                        "from": "2018-09-01",
                        "to": None
                    }
                }
            ],
            amqp_topics={'org_unit.it.create': 1},
        )

    @freezegun.freeze_time('2017-06-22', tz_offset=2)
    def test_edit_unit_itsystem(self):
        self.load_sample_structures()

        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"
        function_id = "cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276"

        original = {
            "itsystem": {
                'name': 'Lokal Rammearkitektur',
                'reference': None,
                'system_type': None,
                'user_key': 'LoRa',
                'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                'validity': {'from': '2010-01-01', 'to': None},
            },
            "org_unit": {
                'name': 'Afdeling for Samtidshistorik',
                'user_key': 'frem',
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
            },
            "person": None,
            "user_key": "fwaf",
            "uuid": function_id,
            "validity": {
                "from": "2017-01-01",
                "to": "2017-12-31",
            }
        }

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/it'.format(unitid),
                [original],
            )

        self.assertRequestResponse(
            '/service/details/edit',
            [function_id],
            json=[
                {
                    "type": "it",
                    "uuid": function_id,
                    "data": {
                        "itsystem": {
                            "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
                        },
                        "validity": {
                            "from": "2017-06-22",
                            "to": "2018-06-01",
                        }
                    }
                }
            ],
            amqp_topics={'org_unit.it.update': 1},
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
                "from": "2017-06-22",
                "to": "2017-12-31",
            },
        )

        original['validity']['to'] = '2017-06-21'
        original['org_unit']['name'] = 'Afdeling for Fremtidshistorik'

        self.assertRequestResponse(
            '/service/ou/{}/details/it?validity=past'.format(unitid),
            [original],
            amqp_topics={'org_unit.it.update': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it'.format(unitid),
            [updated],
            amqp_topics={'org_unit.it.update': 1},
        )

        future = copy.deepcopy(updated)
        future.update(
            validity={
                "from": "2018-01-01",
                "to": "2018-06-01",
            },
        )
        future['org_unit']['name'] = 'Afdeling for Fortidshistorik'

        self.assertRequestResponse(
            '/service/ou/{}/details/it?validity=future'.format(unitid),
            [future],
            amqp_topics={'org_unit.it.update': 1},
        )

    @freezegun.freeze_time('2017-06-22', tz_offset=2)
    def test_edit_move_itsystem(self):
        self.load_sample_structures()

        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"
        function_id = "cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276"

        new_userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
        new_unitid = '04c78fc2-72d2-4d02-b55f-807af19eac48'

        original = {
            "itsystem": {
                'name': 'Lokal Rammearkitektur',
                'reference': None,
                'system_type': None,
                'user_key': 'LoRa',
                'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                'validity': {'from': '2010-01-01', 'to': None},
            },
            "org_unit": {
                'name': 'Afdeling for Samtidshistorik',
                'user_key': 'frem',
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
            },
            "person": None,
            "user_key": "fwaf",
            "uuid": function_id,
            "validity": {
                "from": "2017-01-01",
                "to": "2017-12-31",
            }
        }

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/it'.format(unitid),
                [original],
            )

        self.assertRequestResponse(
            '/service/details/edit',
            [function_id],
            json=[
                {
                    "type": "it",
                    "uuid": function_id,
                    "original": original,
                    "data": {
                        "org_unit": {
                            'uuid': new_unitid,
                        },
                        "person": {
                            "uuid": new_userid,
                        },
                        "user_key": "wooble",
                        "validity": {
                            "from": "2017-06-22",
                            "to": "2018-06-01",
                        },
                    },
                },
            ],
            amqp_topics={
                'employee.it.update': 1,
                'org_unit.it.update': 1,
            },
        )

        updated = copy.deepcopy(original)
        updated.update(
            user_key="wooble",
            org_unit={
                'name': 'Afdeling for Samtidshistorik',
                'user_key': 'frem',
                'uuid': new_unitid,
                'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
            },
            person={
                'name': 'Fedtmule Hund',
                'givenname': 'Fedtmule',
                'surname': 'Hund',
                'uuid': new_userid,
            },
            validity={
                "from": "2017-06-22",
                "to": "2017-12-31",
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it?validity=past'.format(unitid),
            [],
            amqp_topics={
                'employee.it.update': 1,
                'org_unit.it.update': 1,
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it'.format(unitid),
            [updated],
            amqp_topics={
                'employee.it.update': 1,
                'org_unit.it.update': 1,
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/it'.format(new_unitid),
            [updated],
            amqp_topics={
                'employee.it.update': 1,
                'org_unit.it.update': 1,
            },
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
                        'givenname': 'Anders',
                        'surname': 'And',
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
                        'givenname': 'Anders',
                        'surname': 'And',
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

    def test_reading_invalid_integration_data(self):
        self.load_sample_structures()

        userid = '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
        funcid = 'aaa8c495-d7d4-4af1-b33a-f4cb27b82c66'

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        expected = self.assertRequest(
            '/service/e/{}/details/it'.format(userid),
        )

        c.organisationfunktion.update(
            {
                'attributter': {
                    'organisationfunktionegenskaber': [
                        {
                            'integrationsdata': 'blødebjergeboller',
                            'virkning': {
                                'from': '2017-01-01 00:00:00+01:00',
                                'to': 'infinity',
                            },
                        },
                    ],
                },
            },
            funcid,
        )

        expected[0]['integration_data'] = None

        with self.assertLogs(level=logging.WARNING) as cm:
            self.assertRequestResponse(
                '/service/e/{}/details/it'.format(userid),
                expected,
            )

        self.assertIn(
            'WARNING:flask.app:invalid integation data for function {}!'
            .format(funcid),
            cm.output,
        )
