# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

import tests.cases


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class Tests(tests.cases.LoRATestCase):
    def test_class_none_published(self):
        self.assertRequestResponse(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/association_type/",
            {
                "data": {
                    "offset": 0,
                    "total": 4,
                    "items": [
                        {
                            "uuid": "8eea787c-c2c7-46ca-bd84-2dd50f47801f",
                            "name": "-",
                            "user_key": "-",
                            "example": None,
                            "scope": None,
                            "owner": None,
                            "published": "IkkePubliceret",
                        },
                        {
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                            "name": "Medlem",
                            "user_key": "medl",
                            "example": None,
                            "scope": None,
                            "owner": None,
                            "published": "Publiceret",
                        },
                        {
                            "uuid": "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
                            "name": "Projektleder",
                            "user_key": "projektleder",
                            "example": None,
                            "scope": None,
                            "owner": None,
                            "published": "Publiceret",
                        },
                        {
                            "uuid": "45751985-321f-4d4f-ae16-847f0a633360",
                            "name": "Teammedarbejder",
                            "user_key": "teammedarbejder",
                            "example": None,
                            "scope": None,
                            "owner": None,
                            "published": "Publiceret",
                        },
                    ],
                },
                "description": "",
                "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                "/f/association_type/",
                "user_key": "association_type",
                "uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
            },
        )
