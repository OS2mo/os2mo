#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import lora
from . import util


class TestWritingIntegration(util.LoRATestCase):
    maxDiff = None

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_effect_shortening(self):
        expected = {
            "relationer": {
                "myndighed": [
                    {
                        "urn": "urn:dk:kommune:751",
                        "virkning": {
                            "to": "infinity",
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "from_included": True
                        }
                    }
                ]
            },
            "attributter": {
                "organisationegenskaber": [
                    {
                        "organisationsnavn": "Aarhus Universitet",
                        "brugervendtnoegle": "AU",
                        "virkning": {
                            "to": "infinity",
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "from_included": True
                        }
                    }
                ]
            },
            "note": "Automatisk indl\u00e6sning",
            "tilstande": {
                "organisationgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "to": "infinity",
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "from_included": True
                        }
                    }
                ]
            }
        }

        uuid = lora.create('organisation/organisation', expected)
        current = lora.organisation.get(uuid)

        del current['fratidspunkt']
        del current['tiltidspunkt']
        del current['livscykluskode']
        del current['brugerref']

        self.assertEqual(expected, current)

        lora.delete('organisation/organisation', uuid)

        import time
        time.sleep(1)

        # these are the only changes made by deletion!
        deleted = expected.copy()
        deleted['livscykluskode'] = 'Slettet'
        del deleted['note']

        current = lora.organisation.get(uuid,
                                        virkningfra='-infinity',
                                        virkningtil='infinity')

        del current['fratidspunkt']
        del current['tiltidspunkt']
        del current['brugerref']

        self.assertEqual(current, deleted)

        # totally new thing! (-ish...)
        expected = {
            "relationer": {
            },
            "attributter": {
                "organisationegenskaber": [
                    {
                        "organisationsnavn": "HEST",
                        "brugervendtnoegle": "hest",
                        "virkning": {
                            "from": "2016-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "2016-06-01 00:00:00+01",
                            "to_included": False,
                        },
                    },
                    {
                        "organisationsnavn": "NAAAAAAAAM",
                        "brugervendtnoegle": "NM",
                        "virkning": {
                            "to": "2017-06-01 00:00:00+01",
                            "to_included": False,
                            "from": "2016-06-01 00:00:00+01",
                            "from_included": True
                        },
                    },
                ],
            },
            "note": "Automatisk indl\u00e6sning",
            "tilstande": {
                "organisationgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "to": "2017-06-01 00:00:00+01",
                            "to_included": False,
                            "from": "2016-06-01 00:00:00+01",
                            "from_included": True
                        }
                    }
                ]
            }
        }

        lora.create('organisation/organisation', expected, uuid)

        current = lora.organisation.get(uuid,
                                        virkningfra='-infinity',
                                        virkningtil='infinity')

        del current['fratidspunkt']
        del current['tiltidspunkt']
        del current['livscykluskode']
        del current['brugerref']

        self.assertEqual({
            "attributter": {
                "organisationegenskaber": [
                    {
                        # revived :(
                        "virkning": {
                            "from_included": True,
                            "from": "2017-06-01 01:00:00+02",
                            "to_included": False,
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "AU",
                        "organisationsnavn": "Aarhus Universitet"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "from": "2016-01-01 00:00:00+01",
                            "to_included": False,
                            "to": "2016-06-01 01:00:00+02"
                        },
                        "brugervendtnoegle": "hest",
                        "organisationsnavn": "HEST"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "from": "2016-06-01 01:00:00+02",
                            "to_included": False,
                            "to": "2017-06-01 01:00:00+02"
                        },
                        "brugervendtnoegle": "NM",
                        "organisationsnavn": "NAAAAAAAAM"
                    },
                ]
            },
            "note": "Automatisk indl\u00e6sning",
            "tilstande": {
                "organisationgyldighed": [
                    {
                        "virkning": {
                            "from_included": True,
                            "from": "2016-01-01 00:00:00+01",
                            "to_included": False,
                            "to": "2016-06-01 01:00:00+02"
                        },
                        "gyldighed": "Aktiv"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "from": "2016-06-01 01:00:00+02",
                            "to_included": False,
                            "to": "2017-06-01 01:00:00+02"
                        },
                        "gyldighed": "Aktiv"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "from": "2017-06-01 01:00:00+02",
                            "to_included": False,
                            "to": "infinity"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "relationer": {
                "myndighed": [
                    {
                        "urn": "urn:dk:kommune:751",
                        "virkning": {
                            "to": "infinity",
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "from_included": True
                        }
                    }
                ]
            },
        }, current)
