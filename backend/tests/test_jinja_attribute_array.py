#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import List

from parameterized import parameterized

from oio_rest import db

# --------------------------------------------------------------------------------------
# Test for Jinja render/.db.__init__ adapt
# --------------------------------------------------------------------------------------


class TestJinjaAttributeArray:
    @parameterized.expand(
        [
            (
                "organisationegenskaber",
                [
                    [
                        "AU",
                        "Aarhus Universitet",
                        None,
                        {"from": "2016-01-01 00:00:00+01:00", "to": "infinity"},
                    ]
                ],
                (
                    "ARRAY[\n   "
                    "     ROW('AU',\n            'Aarhus Universitet',\n"
                    "            NULL,\n            ROW(\n              "
                    "  '[2016-01-01 00:00:00+01:00, infinity)',\n       "
                    "     NULL,\n            NULL,\n            ''\n    "
                    "        )\n         :: Virkning\n            )\n    "
                    "    ] :: organisationegenskaberAttrType[]\n"
                ),
            ),
            (
                "itsystemegenskaber",
                [
                    [
                        "SAP",
                        "SAP",
                        None,
                        None,
                        None,
                        {
                            "from": "2002-02-14T00:00:00+01:00",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    ]
                ],
                (
                    "ARRAY[\n   "
                    "     ROW('SAP',\n            'SAP',\n           "
                    " NULL,\n            NULL,\n            NULL,\n   "
                    "         ROW(\n                '[2002-02-14T00:00:00+01:00, infinity)',\n"
                    "            NULL,\n            NULL,\n           "
                    " ''\n            )\n         :: Virkning\n          "
                    "  )\n        ] :: itsystemegenskaberAttrType[]\n"
                ),
            ),
            (
                "klasseegenskaber",
                [
                    [
                        "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                        None,
                        None,
                        None,
                        "\x02",
                        None,
                        None,
                        None,
                        None,
                        {"from": "-infinity", "to": "infinity"},
                    ]
                ],
                (
                    "ARRAY[\n   "
                    "     ROW('23d891b5-85aa-4eee-bec7-e84fe21883c5',\n"
                    "            NULL,\n            NULL,\n          "
                    "  NULL,\n            'x02',\n            NULL,\n  "
                    "          NULL,\n            NULL,\n           "
                    " NULL,\n            ROW(\n               "
                    " '[-infinity, infinity)',\n            NULL,\n   "
                    "         NULL,\n            ''\n            )\n   "
                    "      :: Virkning\n            )\n      "
                    "  ] :: klasseegenskaberAttrType[]\n"
                ),
            ),
            (
                "klasseegenskaber",
                [
                    [
                        "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                        None,
                        None,
                        None,
                        "\x00",
                        None,
                        None,
                        None,
                        None,
                        {"from": "-infinity", "to": "infinity"},
                    ]
                ],
                (
                    "ARRAY[\n    "
                    "    ROW('23d891b5-85aa-4eee-bec7-e84fe21883c5',\n   "
                    "         NULL,\n            NULL,\n         "
                    "   NULL,\n            'x00',\n            NULL,\n   "
                    "         NULL,\n            NULL,\n          "
                    "  NULL,\n            ROW(\n               "
                    " '[-infinity, infinity)',\n            NULL,\n     "
                    "       NULL,\n            ''\n            )\n       "
                    "  :: Virkning\n            )\n      "
                    "  ] :: klasseegenskaberAttrType[]\n"
                ),
            ),
        ]
    )
    def test_sql_attribute_array(
        self, attribute: str, periods: List[List[Any]], sql_ref: str
    ):
        sql = db.sql_attribute_array(attribute, periods)

        """
        Removing first chars "-- SPDX..."
        as they interfere with copyright compliance check
        """
        sql_no_spdx = sql[sql.find("ARRAY") :]
        assert sql_ref == sql_no_spdx
