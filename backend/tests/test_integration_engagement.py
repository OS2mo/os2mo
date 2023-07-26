# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from fastapi.testclient import TestClient
from more_itertools import one

from mora import lora
from tests.cases import assert_registrations_equal


userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
userid2 = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"
engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "operation,payload,expected",
    [
        # Base case
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "primary": {"uuid": "d60d1fd6-e561-463c-9a43-2fa99d27c7a3"},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": "1234",
                "fraction": 10,
                "extension_1": "test1",
                "extension_7": "test7",
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            {
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
                    "primær": [
                        {
                            "uuid": "d60d1fd6-e561-463c-9a43-2fa99d27c7a3",
                            "virkning": {
                                "from": "2017-12-01 00:00:00+01",
                                "from_included": True,
                                "to": "2017-12-02 00:00:00+01",
                                "to_included": False,
                            },
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
                            "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                        }
                    ],
                    "opgaver": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
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
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
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
                            "funktionsnavn": "Engagement",
                        }
                    ],
                    "organisationfunktionudvidelser": [
                        {
                            "fraktion": 10,
                            "udvidelse_1": "test1",
                            "udvidelse_7": "test7",
                            "virkning": {
                                "from": "2017-12-01 " "00:00:00+01",
                                "from_included": True,
                                "to": "2017-12-02 " "00:00:00+01",
                                "to_included": False,
                            },
                        }
                    ],
                },
            },
        ),
        # From unit
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": unitid},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            {
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
                    "opgaver": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
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
                            "brugervendtnoegle": mock_uuid,
                            "funktionsnavn": "Engagement",
                        }
                    ]
                },
            },
        ),
        # No valid to
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                },
            },
            {
                "livscykluskode": "Importeret",
                "tilstande": {
                    "organisationfunktiongyldighed": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "infinity",
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
                                "to": "infinity",
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
                                "to": "infinity",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": userid,
                        }
                    ],
                    "opgaver": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "infinity",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
                        }
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "infinity",
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
                                "to": "infinity",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        }
                    ],
                },
                "attributter": {
                    "organisationfunktionegenskaber": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "infinity",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "brugervendtnoegle": mock_uuid,
                            "funktionsnavn": "Engagement",
                        }
                    ]
                },
            },
        ),
        # No job function
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            {
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
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
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
                            "brugervendtnoegle": mock_uuid,
                            "funktionsnavn": "Engagement",
                        }
                    ]
                },
            },
        ),
        # No overwrite
        (
            "edit",
            {
                "type": "engagement",
                "uuid": engagement_uuid,
                "data": {
                    "primary": {"uuid": "cdb026cc-dea9-45e9-98b3-0ccf50537ce4"},
                    "fraction": 30,
                    "extension_7": "test7",
                    "org_unit": {"uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"},
                    "user_key": "regnormsberiger",
                    "job_function": {"uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                    "engagement_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger engagement",
                "relationer": {
                    "opgaver": [
                        {
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                    ],
                    "primær": [
                        {
                            "uuid": "cdb026cc-dea9-45e9-98b3-0ccf50537ce4",
                            "virkning": {
                                "from": "2018-04-01 00:00:00+02",
                                "from_included": True,
                                "to": "infinity",
                                "to_included": False,
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
                            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                    ],
                    "tilknyttedebrugere": [
                        {
                            "uuid": userid2,
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
                                "to": "2018-04-01 00:00:00+02",
                            },
                            "brugervendtnoegle": "bvn",
                            "funktionsnavn": "Engagement",
                        },
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "regnormsberiger",
                            "funktionsnavn": "Engagement",
                        },
                    ],
                    "organisationfunktionudvidelser": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                            "udvidelse_1": "test1",
                            "udvidelse_2": "test2",
                            "udvidelse_9": "test9",
                        },
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                            "fraktion": 30,
                            "udvidelse_1": "test1",
                            "udvidelse_2": "test2",
                            "udvidelse_7": "test7",
                            "udvidelse_9": "test9",
                        },
                    ],
                },
            },
        ),
        # Overwrite
        (
            "edit",
            {
                "type": "engagement",
                "uuid": engagement_uuid,
                "original": {
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                    "person": {"uuid": userid2},
                    "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "job_function": {"uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
                    "engagement_type": {"uuid": "32547559-cfc1-4d97-94c6-70b192eff825"},
                },
                "data": {
                    "job_function": {"uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                    "engagement_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger engagement",
                "relationer": {
                    "opgaver": [
                        {
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
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
                            "uuid": userid2,
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
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
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
                            "funktionsnavn": "Engagement",
                        }
                    ],
                    "organisationfunktionudvidelser": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "udvidelse_1": "test1",
                            "udvidelse_2": "test2",
                            "udvidelse_9": "test9",
                        },
                    ],
                },
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_engagement(
    service_client: TestClient,
    operation: str,
    payload: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
        response = service_client.request(
            "POST", f"/service/details/{operation}", json=payload
        )
        assert response.status_code == 201 if operation == "create" else 200
        engagementid = response.json()

    actual_engagement = await c.organisationfunktion.get(engagementid)
    assert actual_engagement is not None
    assert_registrations_equal(actual_engagement, expected)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_terminate_engagement_via_employee(service_client: TestClient) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {"validity": {"to": "2017-11-30"}}

    response = service_client.request(
        "POST", f"/service/e/{userid2}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid2

    expected = {
        "note": "Afsluttet",
        "relationer": {
            "opgaver": [
                {
                    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "organisatoriskfunktionstype": [
                {
                    "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
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
                    "uuid": userid2,
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
                    "funktionsnavn": "Engagement",
                }
            ],
            "organisationfunktionudvidelser": [
                {
                    "udvidelse_1": "test1",
                    "udvidelse_2": "test2",
                    "udvidelse_9": "test9",
                    "virkning": {
                        "from": "2017-01-01 " "00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
    }

    actual_engagement = await c.organisationfunktion.get(engagement_uuid)
    assert actual_engagement is not None
    assert_registrations_equal(expected, actual_engagement)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "operation,payload,status_code,expected",
    [
        # Empty payload
        (
            "create",
            {
                "type": "engagement",
            },
            400,
            lambda obj: {
                "description": "Missing org_unit",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "org_unit",
                "obj": obj,
                "status": 400,
            },
        ),
        # Invalid payload
        (
            "edit",
            {
                "type": "engagement",
                "uuid": "00000000-0000-0000-0000-000000000000",
            },
            400,
            lambda obj: {
                "description": "Missing data",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "status": 400,
                "key": "data",
                "obj": obj,
            },
        ),
        # Missing unit
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            404,
            lambda _: {
                "description": "Org unit not found.",
                "error": True,
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
        ),
        # Missing person
        (
            "create",
            {
                "type": "engagement",
                "person": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            404,
            lambda _: {
                "description": "User not found.",
                "error": True,
                "error_key": "E_USER_NOT_FOUND",
                "employee_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_engagement_fails(
    service_client: TestClient,
    operation: str,
    payload: dict[str, Any],
    status_code: int,
    expected: Callable[[dict[str, Any]], dict[str, Any]],
) -> None:
    response = service_client.request(
        "POST", f"/service/details/{operation}", json=payload
    )
    assert response.status_code == status_code
    assert response.json() == expected(payload)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_terminate_engagement_with_both_from_and_to_date(
    service_client: TestClient,
) -> None:
    # Terminate engagement for Anders And employed at humanistisk fak
    employee_uuid = userid2

    payload = {
        "type": "engagement",
        "uuid": engagement_uuid,
        "validity": {"from": "2018-10-22", "to": "2018-10-25"},
    }
    response = service_client.request(
        "POST", "/service/details/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == engagement_uuid

    # Assert termination request is persisted correctly in the past
    response = service_client.request(
        "GET",
        f"/service/e/{employee_uuid}/details/engagement",
        params={"validity": "past", "at": "2021-10-08"},
    )
    assert response.status_code == 200
    validity = one(response.json())["validity"]
    assert validity == {"from": "2017-01-01", "to": "2018-10-21"}

    # Assert termination request is persisted correctly in the present
    response = service_client.request(
        "GET",
        f"/service/e/{employee_uuid}/details/engagement",
        params={"validity": "present", "at": "2021-10-08"},
    )
    assert response.status_code == 200
    validity = one(response.json())["validity"]
    assert validity == {"from": "2018-10-26", "to": None}


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_reading_engagement_only_primary_uuid(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/engagement",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    actual = one(response.json())

    engagement_type = actual.get("engagement_type")
    assert engagement_type.keys() == {"uuid"}

    job_function = actual.get("job_function")
    assert job_function.keys() == {"uuid"}

    org_unit = actual.get("org_unit")
    assert org_unit.keys() == {"uuid"}

    person = actual.get("person")
    assert person.keys() == {"uuid"}


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_reading_engagement_calculate_primary(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/e/236e0a78-11a0-4ed9-8545-6286bb8611c7/details/engagement",
        params={"calculate_primary": 1},
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2
    assert result[0]["is_primary"] is False
    assert result[1]["is_primary"] is True
