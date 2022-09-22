# SPDX-FileCopyrightText: 2018-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.util import DBTestCase


class Tests(DBTestCase):
    def setUp(self):
        super().setUp()
        self.a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        self.b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        self.c = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        self.a_a = self.add_klasse(ansvarlig_uuid=self.a, ejer_uuid=self.a)
        self.a_b = self.add_klasse(ansvarlig_uuid=self.a, ejer_uuid=self.b)
        self.a_c = self.add_klasse(ansvarlig_uuid=self.a, ejer_uuid=self.c)
        self.b_a = self.add_klasse(ansvarlig_uuid=self.b, ejer_uuid=self.a)
        self.b_b = self.add_klasse(ansvarlig_uuid=self.b, ejer_uuid=self.b)
        self.b_c = self.add_klasse(ansvarlig_uuid=self.b, ejer_uuid=self.c)
        self.c_a = self.add_klasse(ansvarlig_uuid=self.c, ejer_uuid=self.a)
        self.c_b = self.add_klasse(ansvarlig_uuid=self.c, ejer_uuid=self.b)
        self.c_c = self.add_klasse(ansvarlig_uuid=self.c, ejer_uuid=self.c)

    def add_klasse(self, ansvarlig_uuid: str, ejer_uuid: str) -> str:
        uuid = self.post(
            "/klassifikation/klasse",
            json={
                "note": "Ny klasse",
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": "ORGFUNK",
                            "titel": "XYZ",
                            "virkning": {
                                "from": "2014-05-19 12:02:32",
                                "to": "infinity",
                            },
                        }
                    ]
                },
                "tilstande": {
                    "klassepubliceret": [
                        {
                            "publiceret": "Publiceret",
                            "virkning": {
                                "from": "2014-05-19 12:02:32",
                                "to": "infinity",
                            },
                        }
                    ]
                },
                "relationer": {
                    "ansvarlig": [
                        {
                            "uuid": ansvarlig_uuid,
                            "virkning": {
                                "from": "2014-05-19 11:11:11",
                                "to": "infinity",
                            },
                        }
                    ],
                    "ejer": [
                        {
                            "uuid": ejer_uuid,
                            "virkning": {
                                "from": "2014-05-19 22:22:32",
                                "to": "infinity",
                            },
                        }
                    ],
                },
            },
        )
        return uuid

    def test_multi_uuid_list(self):
        """
        Test getting multiple objects (by their UUID) in one call.
        """
        r = self.perform_request(
            "/klassifikation/klasse",
            params=dict(uuid=[self.a_a, self.a_b, self.b_b]),
            method="GET",
        )
        self.assertCountEqual(
            [x["id"] for x in r.json()["results"][0]],
            [self.a_a, self.a_b, self.b_b],
        )

    def test_multi_relation_search(self):
        """
        Test getting multiple objects (by their relations) in one call.
        """
        self.assertCountEqual(
            self.get(
                "/klassifikation/klasse",
                ansvarlig=self.a,
            ),
            [self.a_a, self.a_b, self.a_c],
        )
        self.assertCountEqual(
            self.get(
                "/klassifikation/klasse",
                ejer=self.b,
            ),
            [self.a_b, self.b_b, self.c_b],
        )
        self.assertCountEqual(
            self.get(
                "/klassifikation/klasse",
                ansvarlig=[self.a, self.b],
            ),
            [self.a_a, self.a_b, self.a_c, self.b_a, self.b_b, self.b_c],
        )

        self.assertCountEqual(
            self.get(
                "/klassifikation/klasse",
                ansvarlig=[self.a, self.c],
                ejer=[self.b, self.c],
            ),
            [self.a_b, self.a_c, self.c_b, self.c_c],
        )
