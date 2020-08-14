# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun
import notsouid

from tests import util


kle_aspekt_facet = {
    'description': '',
    'user_key': 'kle_aspect',
    'uuid': '8a29b2cf-ef98-46f4-9794-0e39354d6ddf'
}

kle_nummer_facet = {
    'description': '',
    'user_key': 'kle_number',
    'uuid': '27935dbb-c173-4116-a4b5-75022315749d'
}


@freezegun.freeze_time('2018-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    @notsouid.freeze_uuid('11111111-1111-1111-1111-111111111111',
                          auto_increment=True)
    def test_create_kle(self):
        self.load_sample_structures()

        org_unit_uuid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

        payload = [
            {
                "type": "kle",
                "org_unit": {'uuid': org_unit_uuid},
                "kle_aspect": [
                    {'uuid': "9016d80a-c6d2-4fb4-83f1-87ecc23ab062"},
                    {'uuid': "fdbdb18f-5a28-4414-bc43-d5c2b70c0510"}
                ],
                "kle_number": {
                    'uuid': "d7c12965-6207-4c82-88b8-68dbf6667492"
                },
                "user_key": "1234",
                "validity": {
                    "from": "2017-12-01",
                    "to": None,
                },
            }
        ]

        expected = [{
            'kle_aspect': [
                {
                    'example': None,
                    'facet': kle_aspekt_facet,
                    'full_name': 'Ansvarlig',
                    'name': 'Ansvarlig',
                    'scope': None,
                    'top_level_facet': kle_aspekt_facet,
                    'user_key': 'kle_ansvarlig',
                    'uuid': '9016d80a-c6d2-4fb4-83f1-87ecc23ab062'
                },
                {
                    'example': None,
                    'facet': kle_aspekt_facet,
                    'full_name': 'Indsigt',
                    'name': 'Indsigt',
                    'scope': None,
                    'top_level_facet': kle_aspekt_facet,
                    'user_key': 'kle_indsigt',
                    'uuid': 'fdbdb18f-5a28-4414-bc43-d5c2b70c0510'
                }
            ],
            'kle_number': {
                'example': None,
                'facet': kle_nummer_facet,
                'full_name': 'KLE nummer',
                'name': 'KLE nummer',
                'scope': None,
                'top_level_facet': kle_nummer_facet,
                'user_key': 'kle_number',
                'uuid': 'd7c12965-6207-4c82-88b8-68dbf6667492'
            },
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'validity': {'from': '2016-01-01', 'to': None}
            },
            'user_key': '1234',
            'uuid': '11111111-1111-1111-1111-111111111111',
            'validity': {'from': '2017-12-01', 'to': None}
        }]

        self.assertRequest(
            '/service/details/create',
            json=payload,
            amqp_topics={
                'org_unit.kle.create': 1,
            },
        )

        actual = self.assertRequest(
            '/service/ou/{}/details/kle'.format(org_unit_uuid),
            amqp_topics={
                'org_unit.kle.create': 1,
            },
        )

        self.assertEqual(expected, actual)

    def test_edit_kle_no_overwrite(self):
        self.load_sample_structures()

        org_unit_uuid = "dad7d0ad-c7a9-4a94-969d-464337e31fec"
        kle_uuid = '4bee0127-a3a3-419a-8bcc-d1b81d21c5b5'

        req = [{
            "type": "kle",
            "uuid": kle_uuid,
            "data": {
                "org_unit": {'uuid': org_unit_uuid},
                "kle_aspect": [
                    {'uuid': "fdbdb18f-5a28-4414-bc43-d5c2b70c0510"},
                    {'uuid': "f9748c65-3354-4682-a035-042c534c6b4e"}
                ],
                "kle_number": {
                    'uuid': "73360db1-bad3-4167-ac73-8d827c0c8751"
                },
                "user_key": "5678",
                "validity": {
                    "from": "2017-12-06",
                    "to": None,
                },
            },
        }]

        org_unit_address_type_facet = {
            'description': '',
            'user_key': 'org_unit_address_type',
            'uuid': '3c44e5d2-7fef-4448-9bf6-449bf414ec49'
        }

        expected = [{
            'kle_aspect': [
                {
                    'example': None,
                    'facet': kle_aspekt_facet,
                    'full_name': 'Udførende',
                    'name': 'Udførende',
                    'scope': None,
                    'top_level_facet': kle_aspekt_facet,
                    'user_key': 'kle_udfoerende',
                    'uuid': 'f9748c65-3354-4682-a035-042c534c6b4e'
                },
                {
                    'example': None,
                    'facet': kle_aspekt_facet,
                    'full_name': 'Indsigt',
                    'name': 'Indsigt',
                    'scope': None,
                    'top_level_facet': kle_aspekt_facet,
                    'user_key': 'kle_indsigt',
                    'uuid': 'fdbdb18f-5a28-4414-bc43-d5c2b70c0510'
                }
            ],
            'kle_number': {
                'example': 'test@example.com',
                'facet': org_unit_address_type_facet,
                'full_name': 'Email',
                'name': 'Email',
                'scope': 'EMAIL',
                'top_level_facet': org_unit_address_type_facet,
                'user_key': 'OrgEnhedEmail',
                'uuid': '73360db1-bad3-4167-ac73-8d827c0c8751'
            },
            'org_unit': {
                'name': 'Skole og Børn',
                'user_key': 'skole-børn',
                'uuid': 'dad7d0ad-c7a9-4a94-969d-464337e31fec',
                'validity': {'from': '2017-01-01', 'to': None}
            },
            'user_key': '5678',
            'uuid': '4bee0127-a3a3-419a-8bcc-d1b81d21c5b5',
            'validity': {'from': '2017-12-06', 'to': None}
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [kle_uuid],
            json=req,
            amqp_topics={
                'org_unit.kle.update': 1,
            },
        )

        actual = self.assertRequest(
            '/service/ou/{}/details/kle'.format(org_unit_uuid),
            amqp_topics={
                'org_unit.kle.update': 1,
            },
        )

        self.assertSortedEqual(expected, actual)
