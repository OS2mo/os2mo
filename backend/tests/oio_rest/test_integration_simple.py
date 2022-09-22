# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.util import DBTestCase


UUID_PATTERN = "{uuid}"
CONTENT_PATH_PATTERN = "{content_path}"


class Tests(DBTestCase):
    maxDiff = None

    def test_site_map(self):
        self.assertRequestResponse(
            "/site-map",
            {
                "site-map": [
                    "/",
                    "/autocomplete/bruger",
                    "/autocomplete/organisationsenhed",
                    "/docs",
                    "/docs/oauth2-redirect",
                    "/klassifikation/classes",
                    "/klassifikation/facet",
                    "/klassifikation/facet/fields",
                    "/klassifikation/facet/schema",
                    "/klassifikation/facet/" + UUID_PATTERN,
                    "/klassifikation/klasse",
                    "/klassifikation/klasse/fields",
                    "/klassifikation/klasse/schema",
                    "/klassifikation/klasse/" + UUID_PATTERN,
                    "/klassifikation/klassifikation",
                    "/klassifikation/klassifikation/fields",
                    "/klassifikation/klassifikation/schema",
                    "/klassifikation/klassifikation/" + UUID_PATTERN,
                    "/kubernetes/live",
                    "/kubernetes/ready",
                    # "/metrics",
                    "/openapi.json",
                    "/organisation/bruger",
                    "/organisation/bruger/fields",
                    "/organisation/bruger/schema",
                    "/organisation/bruger/" + UUID_PATTERN,
                    "/organisation/classes",
                    "/organisation/interessefaellesskab",
                    "/organisation/interessefaellesskab/fields",
                    "/organisation/interessefaellesskab/schema",
                    "/organisation/interessefaellesskab/" + UUID_PATTERN,
                    "/organisation/itsystem",
                    "/organisation/itsystem/fields",
                    "/organisation/itsystem/schema",
                    "/organisation/itsystem/" + UUID_PATTERN,
                    "/organisation/organisation",
                    "/organisation/organisation/fields",
                    "/organisation/organisation/schema",
                    "/organisation/organisation/" + UUID_PATTERN,
                    "/organisation/organisationenhed",
                    "/organisation/organisationenhed/fields",
                    "/organisation/organisationenhed/schema",
                    "/organisation/organisationenhed/" + UUID_PATTERN,
                    "/organisation/organisationfunktion",
                    "/organisation/organisationfunktion/fields",
                    "/organisation/organisationfunktion/schema",
                    "/organisation/organisationfunktion/" + UUID_PATTERN,
                    "/redoc",
                    "/site-map",
                    "/testing/db-reset",
                    "/testing/db-setup",
                    "/testing/db-teardown",
                    "/version",
                ]
            },
            method="GET",
        )

    def test_organisation(self):
        self.assertRequestResponse(
            "/organisation/organisation?bvn=%",
            {
                "results": [
                    [],
                ],
            },
        )

    def test_finding_nothing(self):
        endpoints = [
            endpoint.rsplit("/", 1)[0]
            for endpoint in self.client.get("/site-map").json()["site-map"]
            if endpoint.endswith(UUID_PATTERN)
        ]

        self.assertEqual(
            [
                "/klassifikation/facet",
                "/klassifikation/klasse",
                "/klassifikation/klassifikation",
                "/organisation/bruger",
                "/organisation/interessefaellesskab",
                "/organisation/itsystem",
                "/organisation/organisation",
                "/organisation/organisationenhed",
                "/organisation/organisationfunktion",
            ],
            endpoints,
        )

        for endpoint in endpoints:
            req = endpoint + "?bvn=%"

            with self.subTest(req):
                self.assertRequestResponse(
                    req,
                    {
                        "results": [
                            [],
                        ],
                    },
                )

    def test_return_400_on_value_errors(self):
        self.assertRequestFails("/klassifikation/klasse?facet=invalid", 400)
        self.assertRequestFails("/organisation/organisation?tilhoerer=invalid", 400)
        self.assertRequestFails("/organisation/organisation?virkningfra=xyz", 400)
