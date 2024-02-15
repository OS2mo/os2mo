# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from fastapi.testclient import TestClient

from mora import lora
from tests.cases import assert_registrations_equal

userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
mock_uuid = "288ecae8-faa4-428f-872e-1ad1a466b330"
role_uuid = "1b20d0b9-96a0-42a6-b196-293bb86e62e8"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "operation,payload,expected",
    [
        # Base case
        (
            "create",
            {
                "type": "role",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "role_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": "1234",
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
                            "brugervendtnoegle": "1234",
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # On unit
        (
            "create",
            {
                "type": "role",
                "person": {"uuid": userid},
                "org_unit": {"uuid": unitid},
                "role_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # No valid to
        (
            "create",
            {
                "type": "role",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "role_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # No overwrite
        (
            "edit",
            {
                "type": "role",
                "uuid": role_uuid,
                "data": {
                    "role_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "org_unit": {"uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"},
                    "user_key": "bjørndrager",
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger rolle",
                "relationer": {
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
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
                                "to": "2018-04-01 00:00:00+02",
                            },
                            "brugervendtnoegle": "bvn",
                            "funktionsnavn": "Rolle",
                        },
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "bjørndrager",
                            "funktionsnavn": "Rolle",
                        },
                    ]
                },
            },
        ),
        # Minimal
        (
            "edit",
            {
                "type": "role",
                "uuid": role_uuid,
                "data": {
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger rolle",
                "relationer": {
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # Minimal Unit
        (
            "edit",
            {
                "type": "role",
                "uuid": role_uuid,
                "data": {
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger rolle",
                "relationer": {
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # Person
        (
            "edit",
            {
                "type": "role",
                "uuid": role_uuid,
                "data": {
                    "person": {
                        "uuid": userid,
                    },
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
            {
                "note": "Rediger rolle",
                "relationer": {
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
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
                                "to": "2018-01-01 00:00:00+01",
                            },
                        },
                        {
                            "uuid": userid,
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
        # Overwrite
        (
            "edit",
            {
                "type": "role",
                "uuid": role_uuid,
                "original": {
                    "validity": {"from": "2017-01-01", "to": None},
                    "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "role_type": {"uuid": "32547559-cfc1-4d97-94c6-70b192eff825"},
                },
                "data": {
                    "role_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "org_unit": {"uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger rolle",
                "relationer": {
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
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
                            "funktionsnavn": "Rolle",
                        }
                    ]
                },
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_role(
    service_client: TestClient,
    operation: str,
    payload: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
        response = service_client.request(
            "POST", f"/service/details/{operation}", json=payload
        )
        assert response.status_code == 201 if operation == "create" else 200
        roleid = response.json()

    actual_role = await c.organisationfunktion.get(roleid)
    assert actual_role is not None
    assert_registrations_equal(actual_role, expected)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_terminate_role(service_client: TestClient) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

    payload = {"validity": {"to": "2017-11-30"}}

    response = service_client.request(
        "POST", f"/service/e/{userid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid

    expected_role = {
        "note": "Afsluttet",
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
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
                    "funktionsnavn": "Rolle",
                }
            ]
        },
    }

    actual_role = await c.organisationfunktion.get(role_uuid)
    assert actual_role is not None
    assert_registrations_equal(actual_role, expected_role)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_reading(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/role",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "org_unit": {
                "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "role_type": {
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
            "uuid": role_uuid,
            "user_key": "bvn",
            "validity": {"from": "2017-01-01", "to": None},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "missing,expected",
    [
        (
            "org_unit",
            {
                "description": "Org unit not found.",
                "error": True,
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
        ),
        (
            "user",
            {
                "description": "User not found.",
                "employee_uuid": "00000000-0000-0000-0000-000000000000",
                "error": True,
                "error_key": "E_USER_NOT_FOUND",
                "status": 404,
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_role_missing(
    service_client: TestClient, missing: str, expected: dict[str, Any]
) -> None:
    # Check the POST request
    zeroid = "00000000-0000-0000-0000-000000000000"

    payload = {
        "type": "role",
        "person": {"uuid": userid if missing != "user" else zeroid},
        "org_unit": {"uuid": unitid if missing != "org_unit" else zeroid},
        "role_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "validity": {
            "from": "2017-12-01",
            "to": "2017-12-01",
        },
    }
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 404
    assert response.json() == expected
