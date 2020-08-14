# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import unittest

import freezegun
import notsouid
from unittest.mock import patch

from mora import lora
from . import util

mock_uuid = 'f494ad89-039d-478e-91f2-a63566554bd6'


org_unit_type_facet = {
    'description': '',
    'user_key': 'org_unit_type',
    'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'
}
org_unit_level_facet = {
    'description': '',
    'user_key': 'org_unit_level',
    'uuid': '77c39616-dd98-4cf5-87fb-cdb9f3a0e455'
}


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('mora.service.orgunit.uuid.uuid4', new=lambda: mock_uuid)
@patch('mora.conf_db.get_configuration',
       new=lambda *x: {})
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_org_unit_temporality(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=past',

            [{
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Fremtidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        'user_key': 'inst',
                        "top_level_facet": org_unit_type_facet,
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2016-01-01', 'to': '2016-12-31'}
            }],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=present',

            [{
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Samtidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            'user_key': 'inst',
                            "top_level_facet": org_unit_type_facet,
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2017-01-01', 'to': '2017-12-31'}
            }],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=future',

            [{
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Fortidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2018-01-01', 'to': '2018-12-31'}
            }],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=past&at=2020-01-01',
            [{
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Fremtidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2016-01-01', 'to': '2016-12-31'}
            }, {
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Samtidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2017-01-01', 'to': '2017-12-31'}
            }, {
                'location': 'Overordnet Enhed\\Humanistisk fakultet'
                            '\\Historisk Institut',
                'name': 'Afdeling for Fortidshistorik',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                "org_unit_level": None,
                'parent': {
                    'location': 'Overordnet Enhed\\Humanistisk fakultet',
                    'name': 'Historisk Institut',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    "org_unit_level": None,
                    'parent': {
                        'location': 'Overordnet Enhed',
                        'name': 'Humanistisk fakultet',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Institut',
                            'name': 'Institut',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                        },
                        "org_unit_level": None,
                        'parent': {
                            'location': '',
                            'name': 'Overordnet Enhed',
                            'org': {
                                'name': 'Aarhus Universitet',
                                'user_key': 'AU',
                                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                            },
                            'org_unit_type': {
                                'example': None,
                                "facet": org_unit_type_facet,
                                'full_name': 'Afdeling',
                                'name': 'Afdeling',
                                'scope': None,
                                "top_level_facet": org_unit_type_facet,
                                'user_key': 'afd',
                                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                            },
                            "org_unit_level": None,
                            'parent': None,
                            'time_planning': None,
                            'user_key': 'root',
                            'user_settings': {'orgunit': {}},
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None
                            }
                        },
                        'time_planning': None,
                        'user_key': 'hum',
                        'user_settings': {'orgunit': {}},
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hist',
                    'user_settings': {'orgunit': {}},
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'}
                },
                'time_planning': None,
                'user_key': 'frem',
                'user_settings': {'orgunit': {}},
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'validity': {'from': '2018-01-01', 'to': '2018-12-31'}
            }],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=present&at=2020-01-01',
            [],
        )

        self.assertRequestResponse(
            '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/details/org_unit?validity=future&at=2020-01-01',
            [],
        )

    @util.mock('aabogade.json', allow_mox=True)
    def test_create_org_unit(self, m):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Fake Corp",
            "integration_data": {"fakekey": 42},
            "time_planning": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52",
            },
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "org_unit_level": {
                'uuid': "0f015b67-f250-43bb-9160-043ec19fad48"
            },
            "details": [
                {
                    "type": "address",
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefon",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    "validity": {
                        "from": "2016-02-04",
                        "to": "2017-10-21",
                    },
                    "value": "11223344"
                },
                {
                    "type": "address",
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                            "scope": "DAR",
                            "user_key": "Adresse",
                            "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    "validity": {
                        "from": "2016-02-04",
                        "to": "2017-10-21",
                    },
                    "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2016-02-04",
                "to": "2017-10-21",
            }
        }

        r = self.request('/service/ou/create', json=payload)
        unitid = r.json

        expected = {
            "livscykluskode": "Importeret",
            "note": "Oprettet i MO",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "brugervendtnoegle": unitid,
                        "enhedsnavn": "Fake Corp",
                        "integrationsdata": '{"fakekey": 42}'
                    }
                ]
            },
            "relationer": {
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "objekttype": "tidsregistrering",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                    }
                ],
                "overordnet": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
                    }
                ],
                "tilhoerer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "enhedstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                    }
                ],
                'niveau': [{
                    'uuid': '0f015b67-f250-43bb-9160-043ec19fad48',
                    'virkning': {
                        'from': '2016-02-04 00:00:00+01',
                        'from_included': True,
                        'to': '2017-10-22 00:00:00+02',
                        'to_included': False
                    }
                }],
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-10-22 00:00:00+02",
                            "from_included": True,
                            "from": "2016-02-04 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
        }

        actual_org_unit = c.organisationenhed.get(unitid)

        self.assertRegistrationsEqual(expected, actual_org_unit)

        self.assertRequestResponse(
            '/service/ou/{}/'.format(unitid),
            {
                "location": "Overordnet Enhed",
                "name": "Fake Corp",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                'org_unit_level': {
                    'example': None,
                    "facet": org_unit_level_facet,
                    'full_name': 'Niveau 10',
                    'name': 'Niveau 10',
                    'scope': None,
                    "top_level_facet": org_unit_level_facet,
                    'user_key': 'orgunitlevel10',
                    'uuid': '0f015b67-f250-43bb-9160-043ec19fad48'
                },
                "time_planning": {
                    "example": None,
                    "facet": org_unit_type_facet,
                    "full_name": "Institut",
                    "name": "Institut",
                    "scope": None,
                    "top_level_facet": org_unit_type_facet,
                    "user_key": "inst",
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                },
                "org_unit_type": {
                    "example": None,
                    "facet": org_unit_type_facet,
                    "full_name": "Institut",
                    "name": "Institut",
                    "scope": None,
                    "top_level_facet": org_unit_type_facet,
                    "user_key": "inst",
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "parent": {
                    "location": "",
                    "name": "Overordnet Enhed",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    'org_unit_level': None,
                    "time_planning": None,
                    "org_unit_type": {
                        "example": None,
                        "facet": org_unit_type_facet,
                        "full_name": "Afdeling",
                        "name": "Afdeling",
                        "scope": None,
                        "top_level_facet": org_unit_type_facet,
                        "user_key": "afd",
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                    },
                    "parent": None,
                    "user_key": "root",
                    "user_settings": {"orgunit": {}},
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "validity": {
                        "from": "2016-01-01",
                        "to": None
                    }
                },
                "user_key": unitid,
                "user_settings": {"orgunit": {}},
                "uuid": unitid,
                "validity": {
                    "from": "2016-02-04",
                    "to": "2017-10-21"
                }
            },
            amqp_topics={
                'org_unit.org_unit.create': 1,
                'org_unit.address.create': 2,
            },
        )

    def test_create_org_unit_fails_validation_outside_org_unit(self):
        """Validation should fail when date range is outside of org unit
        range """
        self.load_sample_structures()

        payload = {
            "name": "Fake Corp",
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "addresses": [
                {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefon",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "value": "11 22 33 44",
                },
                {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "Adresse",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2010-02-04",
                "to": "2017-10-21",
            }
        }

        expected = {
            'description': 'Date range exceeds validity '
                           'range of associated org unit.',
            'error': True,
            'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
            'org_unit_uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            'status': 400,
            'valid_from': '2016-01-01',
            'valid_to': None,
            'wanted_valid_from': '2010-02-04',
            'wanted_valid_to': '2017-10-21'
        }

        self.assertRequestResponse(
            '/service/ou/create',
            expected,
            json=payload,
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/ou/create?force=0',
            expected,
            json=payload,
            status_code=400,
        )

        self.assertRequest(
            '/service/ou/create?force=1',
            json=payload,
            amqp_topics={'org_unit.org_unit.create': 1},
        )

    def test_edit_org_unit_overwrite(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = [{
            "type": "org_unit",
            "original": {
                "validity": {
                    "from": "2016-01-01 00:00:00+01",
                    "to": None
                },
                "parent": {
                    'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                'time_planning': None,
                "org_unit_type": {
                    'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "name": "Filosofisk Institut",
                "uuid": org_unit_uuid,
            },
            "data": {
                "org_unit_type": {
                    'uuid': "79e15798-7d6d-4e85-8496-dcc8887a1c1a"
                },
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [org_unit_uuid],
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    }
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    },
                    {
                        "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_read_root(self):
        self.load_sample_structures(minimal=True)

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                "location": "",
                "name": "Overordnet Enhed",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                'time_planning': None,
                'org_unit_level': None,
                "org_unit_type": {
                    "example": None,
                    "facet": org_unit_type_facet,
                    "full_name": "Afdeling",
                    "name": "Afdeling",
                    "scope": None,
                    "top_level_facet": org_unit_type_facet,
                    "user_key": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                },
                'user_settings': {'orgunit': {}},
                "parent": None,
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None,
                },
            },
        )

    def test_edit_missing_org_unit(self):
        self.load_sample_structures()

        req = [{
            "type": "org_unit",
            "data": {
                "org_unit_type": {
                    'uuid': "79e15798-7d6d-4e85-8496-dcc8887a1c1a"
                },
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Missing uuid',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'uuid',
                'obj': req[0]['data'],
                'status': 400,
            },
            json=req,
            status_code=400,
        )

    def test_edit_org_unit(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = [{
            "type": "org_unit",
            "data": {
                "uuid": org_unit_uuid,
                "org_unit_type": {
                    'uuid': "79e15798-7d6d-4e85-8496-dcc8887a1c1a"
                },
                "org_unit_level": {
                    'uuid': "d329c924-0cd1-4599-aca8-1d89cca2bff2"
                },
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [org_unit_uuid],
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                'niveau': [{
                    'uuid': 'd329c924-0cd1-4599-aca8-1d89cca2bff2',
                    'virkning': {
                        'from': '2017-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2017-01-01 00:00:00+01"
                        }
                    },
                    {
                        "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    @freezegun.freeze_time('2010-01-01')
    def test_edit_org_unit_earlier_start(self):
        """ Test setting the start date to something earlier (#23182)
        """

        self.load_sample_structures()

        org_unit_uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        with self.subTest('too soon'):
            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Date range exceeds validity range of '
                    'associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'status': 400,
                    'valid_from': '2016-01-01',
                    'valid_to': None,
                    'wanted_valid_from': '2010-01-01',
                    'wanted_valid_to': None,
                },
                status_code=400,
                json={
                    "type": "org_unit",
                    "data": {
                        "uuid": org_unit_uuid,
                        "validity": {
                            "from": "2010-01-01",
                        },
                    },
                },
            )

        with self.subTest('too soon, with parent'):
            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Date range exceeds validity range of '
                    'associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'status': 400,
                },
                status_code=400,
                json={
                    "type": "org_unit",
                    "data": {
                        "uuid": org_unit_uuid,
                        'parent': {
                            'name': 'Overordnet Enhed',
                            'user_key': 'root',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                        "validity": {
                            "from": "2010-01-01",
                        },
                    },
                },
            )

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid, json={
                "type": "org_unit",
                "data": {
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2016-06-01",
                    },
                },
            },
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        self.assertRequest(
            '/service/ou/' + org_unit_uuid +
            '/?at=2016-06-01',
            200,
            "should exist on 2016-06-01",
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        self.assertRequest(
            '/service/ou/' + org_unit_uuid +
            '/?at=2016-05-31',
            404,
            "should not exist before start",
            amqp_topics={'org_unit.org_unit.update': 1},
        )

    @freezegun.freeze_time('2016-01-01')
    @util.mock('aabogade.json', allow_mox=True)
    def test_edit_org_unit_extending_end(self, m):
        self.load_sample_structures()

        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"
        topics = {}

        def check_future_names(*names):
            self.assertEqual(
                list(names),
                [
                    (d["name"], d["validity"]["from"], d["validity"]["to"])
                    for d in self.assertRequest(
                        "/service/ou/{}/details/org_unit?validity=future"
                        .format(unitid),
                        amqp_topics=topics,
                    )
                ],
            )

        with self.subTest("prerequisites"):
            check_future_names(
                ('Afdeling for Samtidshistorik', '2017-01-01', '2017-12-31'),
                ('Afdeling for Fortidshistorik', '2018-01-01', '2018-12-31'),
            )

        self.assertRequestFails(
            "/service/details/edit",
            400,
            "Editing without clamp should fail",
            json={
                "type": "org_unit",
                "data": {
                    "name": "Institut for Vrøvl",
                    "uuid": unitid,
                    "validity": {
                        "from": "2018-06-01",
                    },
                },
            },
        )

        topics = {"org_unit.org_unit.update": 1}
        self.assertRequestResponse(
            "/service/details/edit",
            unitid,
            "Editing with clamp should succeed",
            json={
                "type": "org_unit",
                "data": {
                    "name": "Institut for Vrøvl",
                    "uuid": unitid,
                    "clamp": True,
                    "validity": {
                        "from": "2018-03-01",
                    },
                },
            },
            amqp_topics=topics,
        )

        topics["org_unit.org_unit.update"] += 1
        self.assertRequestResponse(
            "/service/details/edit",
            unitid,
            "Editing with clamp should succeed",
            json={
                "type": "org_unit",
                "data": {
                    "name": "Institut for Sludder",
                    "uuid": unitid,
                    "clamp": True,
                    "validity": {
                        "from": "2018-06-01",
                        "to": "2018-09-30",
                    },
                },
            },
            amqp_topics=topics,
        )

        check_future_names(
            ('Afdeling for Samtidshistorik', '2017-01-01', '2017-12-31'),
            ('Afdeling for Fortidshistorik', '2018-01-01', '2018-02-28'),
            ('Institut for Vrøvl', '2018-03-01', '2018-05-31'),
            ('Institut for Sludder', '2018-06-01', '2018-09-30'),
            ('Institut for Vrøvl', '2018-10-01', '2018-12-31'),
        )

    @freezegun.freeze_time('2016-01-01')
    @util.mock('aabogade.json', allow_mox=True)
    def test_edit_org_unit_earlier_start_on_created(self, m):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "type": "org_unit",
            "name": "Fake Corp",
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "addresses": [
                {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefon",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "value": "11 22 33 44",
                },
                {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "Adresse",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2017-01-01",
                "to": "2017-12-31",
            }
        }

        org_unit_uuid = self.assertRequest(
            '/service/ou/create',
            json=payload,
            amqp_topics={
                'org_unit.org_unit.create': 1,
            },
        )

        req = {
            "type": "org_unit",
            "data": {
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2016-06-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json=req,
            amqp_topics={
                'org_unit.org_unit.create': 1,
                'org_unit.org_unit.update': 1,
            },
        )

        expected = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'brugervendtnoegle': org_unit_uuid,
                        'enhedsnavn': 'Fake Corp',
                        'integrationsdata': '{}',
                        'virkning': {
                            'from': '2016-06-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
            },
            'livscykluskode': 'Rettet',
            'note': 'Rediger organisationsenhed',
            'relationer': {
                'enhedstype': [
                    {
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                        'virkning': {
                            'from': '2016-06-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                'overordnet': [
                    {
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'virkning': {
                            'from': '2016-06-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                'tilhoerer': [
                    {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'virkning': {
                            'from': '2016-06-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
            },
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2016-06-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    @notsouid.freeze_uuid('ec93e37e-774e-40b4-953c-05ca41b80372')
    def test_create_missing_parent(self):
        self.load_sample_structures()

        payload = {
            "name": "Fake Corp",
            "parent": {
                'uuid': "00000000-0000-0000-0000-000000000000"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "addresses": [],
            "validity": {
                "from": "2017-01-01",
                "to": "2018-01-01",
            }
        }

        self.assertRequestResponse(
            '/service/ou/create',
            {
                'description': 'Org unit not found.',
                'error': True,
                'error_key': 'E_ORG_UNIT_NOT_FOUND',
                'org_unit_uuid': '00000000-0000-0000-0000-000000000000',
                'status': 404
            },
            json=payload,
            status_code=404,
        )

    def test_create_root_unit(self):
        self.load_sample_structures(minimal=True)

        unitid = "00000000-0000-0000-0000-000000000000"
        orgid = "456362c4-0ee4-4e5e-a72c-751239745e62"

        roots = [
            {
                'child_count': 0,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {'from': '2016-01-01', 'to': None},
            },
        ]

        with self.subTest('prerequisites'):
            self.assertRequestResponse('/service/o/{}/children'.format(orgid),
                                       roots)

        self.assertRequestResponse(
            '/service/ou/create',
            unitid,
            json={
                "name": "Fake Corp",
                "uuid": unitid,
                "user_key": "fakefakefake",
                "parent": {
                    'uuid': orgid,
                },
                'time_planning': None,
                "org_unit_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825",
                },
                "validity": {
                    "from": "2017-01-01",
                    "to": "2018-01-01",
                }
            },
            amqp_topics={'org_unit.org_unit.create': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/'.format(unitid),
            {
                "location": "",
                "name": "Fake Corp",
                "user_key": "fakefakefake",
                "uuid": unitid,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": orgid
                },
                'time_planning': None,
                "org_unit_type": {
                    "example": None,
                    "facet": org_unit_type_facet,
                    "full_name": "Afdeling",
                    "name": "Afdeling",
                    "scope": None,
                    "top_level_facet": org_unit_type_facet,
                    "user_key": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "org_unit_level": None,
                "parent": None,
                "validity": {
                    "from": "2017-01-01",
                    "to": "2018-01-01"
                },
                "user_settings": {'orgunit': {}},
            },
            amqp_topics={'org_unit.org_unit.create': 1},
        )

        roots.insert(0, {
            "child_count": 0,
            "name": "Fake Corp",
            "user_key": "fakefakefake",
            "uuid": unitid,
            "validity": {
                "from": "2017-01-01",
                "to": "2018-01-01"
            }
        })

        self.assertRequestResponse(
            '/service/o/{}/children'.format(orgid),
            roots,
            amqp_topics={'org_unit.org_unit.create': 1},
        )

    def test_rename_org_unit(self):
        # A generic example of editing an org unit

        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        req = {
            "type": "org_unit",
            "data": {
                "name": "Filosofisk Institut II",
                "user_key": "højrespidseskilning",
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2018-01-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "2018-01-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "fil",
                        "enhedsnavn": "Filosofisk Institut"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "højrespidseskilning",
                        "enhedsnavn": "Filosofisk Institut II"
                    },
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_edit_time_planning(self):
        self.load_sample_structures()

        org_unit_uuid = '85715fc7-925d-401b-822d-467eb4b163b6'

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json={
                "type": "org_unit",
                "data": {
                    "time_planning": {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                    },
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        response = self.assertRequest(
            '/service/ou/{}/details/org_unit?validity=present'
            .format(org_unit_uuid),
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            'example': None,
            "facet": org_unit_type_facet,
            'full_name': 'Fakultet',
            'name': 'Fakultet',
            'scope': None,
            "top_level_facet": org_unit_type_facet,
            'user_key': 'fak',
            'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
        }

        actual = response[-1].get('time_planning')

        self.assertEqual(expected, actual)

    @unittest.expectedFailure
    @freezegun.freeze_time('2016-01-01')
    def test_rename_org_unit_early(self):
        """ This test fails due to validity records being
            fractioned in lora due to integration_data added
            the results are not wrong, just fractioned (#25200)
        """
        # Test that we can rename a unit to a date *earlier* than its
        # creation date. We are expanding the validity times on the
        # object, so we insert a separate copy as to not 'taint' the
        # fixtures, as LoRa is unable to properly delete objects
        # without the validities bleeding through.

        self.load_sample_structures()

        org_unit_uuid = 'cbe3016f-b0ab-4c14-8265-ba4c1b3d17f6'

        util.load_fixture(
            'organisation/organisationenhed',
            'create_organisationenhed_samf.json', org_unit_uuid)

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid, json={
                "type": "org_unit",
                "data": {
                    "name": "Whatever",
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2016-01-01",
                    },
                },
            },
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'
            '?validity=past'.format(org_unit_uuid),
            [],
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'.format(org_unit_uuid),
            [{
                'name': 'Whatever',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'time_planning': None,
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Fakultet',
                    'name': 'Fakultet',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'parent': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'validity': {
                        'from': '2016-01-01',
                        'to': None,
                    },
                },
                'user_key': 'samf',
                'uuid': org_unit_uuid,
                'validity': {
                    'from': '2016-01-01', 'to': None,
                },
            }],
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/org_unit'
            '?validity=future'.format(org_unit_uuid),
            [],
            amqp_topics={'org_unit.org_unit.update': 1},
        )

    def test_rename_root_org_unit(self):
        # Test renaming root units

        self.load_sample_structures()

        org_unit_uuid = '2874e1dc-85e6-4269-823a-e1125484dfd3'

        req = {
            "type": "org_unit",
            "data": {
                "name": "Whatever",
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2018-01-01T00:00:00+01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            'attributter': {
                'organisationenhedegenskaber': [{
                    'brugervendtnoegle': 'root',
                    'enhedsnavn': 'Whatever',
                    'virkning': {
                        'from': '2018-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }, {
                    'brugervendtnoegle': 'root',
                    'enhedsnavn': 'Overordnet '
                                  'Enhed',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': '2018-01-01 '
                              '00:00:00+01',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Rettet',
            'note': 'Rediger organisationsenhed',
            'relationer': {
                'enhedstype': [{
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    'virkning': {
                        'from': '2016-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'overordnet': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2016-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilhoerer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2016-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationenhedgyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2016-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_move_org_unit(self):
        'Test successfully moving organisational units'

        self.load_sample_structures()

        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        req = {
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-07-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected = {
            "note": "Rediger organisationsenhed",
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "hum",
                        "enhedsnavn": "Humanistisk fakultet",
                        "integrationsdata": "{}",
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "overordnet": [
                    {
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'virkning': {
                            'from': '2016-01-01 00:00:00+01',
                            'from_included': True,
                            'to': '2017-07-01 00:00:00+02',
                            'to_included': False
                        }
                    },
                    {
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                        'virkning': {
                            'from': '2017-07-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2016-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertRegistrationsEqual(expected, actual)

    def test_move_org_unit_should_fail_validation(self):
        """Should fail validation when trying to move an org unit to one of
        its children """

        self.load_sample_structures()

        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        req = {
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-07-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Org unit cannot be moved to '
                               'one of its own child units',
                'error': True,
                'error_key': 'V_ORG_UNIT_MOVE_TO_CHILD',
                'org_unit_uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'status': 400
            },
            status_code=400,
            json=req,
        )

    def test_move_org_unit_to_root_fails(self):
        """Should fail validation when trying to move an org unit to the root
        level"""

        self.load_sample_structures()

        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        req = {
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-07-01T00:00:00+02",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Moving an org unit to the root '
                               'level is not allowed',
                'error': True,
                'error_key': 'V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL',
                'status': 400
            },
            status_code=400,
            json=req)

    @freezegun.freeze_time('2010-01-01')
    def test_cannot_extend_beyond_parent(self):
        """Should fail validation since the new validity period extends beyond
        that of the parent. (#23155)"""

        self.load_sample_structures()

        org_unit_uuid = '04c78fc2-72d2-4d02-b55f-807af19eac48'

        with self.subTest('too late'):
            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Date range exceeds validity range of '
                    'associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'status': 400,
                    'valid_from': '2016-01-01',
                    'valid_to': '2018-12-31',
                    'wanted_valid_from': '2016-01-01',
                    'wanted_valid_to': None
                },
                status_code=400,
                json={
                    "type": "org_unit",
                    "data": {
                        "uuid": org_unit_uuid,
                        "validity": {
                            "from": "2016-01-01",
                            "to": None,
                        },
                    },
                })

        with self.subTest('too soon'):
            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Date range exceeds validity range of '
                    'associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'status': 400,
                    'valid_from': '2016-01-01',
                    'valid_to': '2018-12-31',
                    'wanted_valid_from': '2010-01-01',
                    'wanted_valid_to': '2018-12-31',
                },
                status_code=400,
                json={
                    "type": "org_unit",
                    "data": {
                        "uuid": org_unit_uuid,
                        "validity": {
                            "from": "2010-01-01",
                            "to": "2018-12-31",
                        },
                    },
                })

    def test_move_org_unit_should_fail_when_moving_root_unit(self):
        """Should fail validation when trying to move the root org unit"""

        self.load_sample_structures()

        org_unit_uuid = '2874e1dc-85e6-4269-823a-e1125484dfd3'

        req = {
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-07-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Moving the root org unit is not allowed',
                'error': True,
                'error_key': 'V_CANNOT_MOVE_ROOT_ORG_UNIT',
                'status': 400
            },
            status_code=400,
            json=req)

    def test_move_org_unit_wrong_org(self):
        'Verify that we cannot move a unit into another organisation'

        self.load_sample_structures()

        org_unit_uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'
        other_org_uuid = util.load_fixture(
            'organisation/organisation',
            'create_organisation_AU.json',
        )

        c = lora.Connector()

        other_unit = util.get_fixture('create_organisationenhed_root.json')
        other_unit['relationer']['tilhoerer'][0]['uuid'] = other_org_uuid
        other_unit['relationer']['overordnet'][0]['uuid'] = other_org_uuid

        other_unit_uuid = c.organisationenhed.create(other_unit)

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Unit belongs to an organisation different '
                'from the current one.',
                'error': True,
                'error_key': 'V_UNIT_OUTSIDE_ORG',
                'org_unit_uuid': other_unit_uuid,
                'current_org_uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'target_org_uuid': other_org_uuid,
                'status': 400,
            },
            status_code=400,
            json={
                "type": "org_unit",
                "data": {
                    "parent": {
                        'uuid': other_unit_uuid,
                    },
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
        )

    def test_move_org_autoparent(self):
        "Verify that we cannot create cycles when moving organisational units"

        self.load_sample_structures()

        root_uuid = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        org_unit_uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        c = lora.Connector()
        c.organisationenhed.update(
            {
                'relationer': {
                    'overordnet': [{
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                        'virkning': {
                            'from': '2016-01-01',
                            'to': 'infinity',
                        },
                    }],
                },
            },
            root_uuid,
        )

        self.assertEqual(
            c.organisationenhed.get(root_uuid)['relationer']['overordnet'],
            [{
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                },
            }],
        )

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Org unit cannot be moved to one of its own '
                'child units',
                'error': True,
                'error_key': 'V_ORG_UNIT_MOVE_TO_CHILD',
                'status': 400,
                'org_unit_uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            },
            status_code=400,
            json={
                "type": "org_unit",
                "data": {
                    "parent": {
                        'uuid': root_uuid,
                    },
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
        )

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Org unit cannot be moved to one of its own '
                'child units',
                'error': True,
                'error_key': 'V_ORG_UNIT_MOVE_TO_CHILD',
                'status': 400,
                'org_unit_uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
            status_code=400,
            json={
                "type": "org_unit",
                "data": {
                    "parent": {
                        'uuid': root_uuid,
                    },
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
        )

    def test_move_org_nowhere(self):
        "Verify that we cannot move units to places that don't exist"

        self.load_sample_structures()

        org_unit_uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'Org unit not found.',
                'error': True,
                'error_key': 'E_ORG_UNIT_NOT_FOUND',
                'org_unit_uuid': '00000000-0000-0000-0000-000000000001',
                'status': 404,
            },
            status_code=404,
            json={
                "type": "org_unit",
                "data": {
                    "parent": {
                        'uuid': "00000000-0000-0000-0000-000000000001",
                    },
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
        )

    def test_edit_org_unit_should_fail_validation_when_end_before_start(self):
        """Should fail validation when trying to edit an org unit with the
        to-time being before the from-time """

        self.load_sample_structures()

        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        req = {
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-07-01",
                    "to": "2015-07-01",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            {
                'description': 'End date is before start date.',
                'error': True,
                'error_key': 'V_END_BEFORE_START',
                'status': 400,
                'obj': req['data'],
            },
            status_code=400,
            json=req)

    def test_terminate_org_unit(self):
        self.load_sample_structures()

        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"

        payload = {
            "validity": {
                "to": "2016-10-21"
            }
        }

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(unitid),
            unitid,
            json=payload,
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=past',
            [{
                'location': 'Overordnet Enhed\\Humanistisk fakultet',
                'name': 'Filosofisk Institut',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'org_unit_level': None,
                'org_unit_type': {
                    'example': None,
                    "facet": org_unit_type_facet,
                    'full_name': 'Institut',
                    'name': 'Institut',
                    'scope': None,
                    "top_level_facet": org_unit_type_facet,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                },
                'parent': {
                    'location': 'Overordnet Enhed',
                    'name': 'Humanistisk fakultet',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'org_unit_level': None,
                    'org_unit_type': {
                        'example': None,
                        "facet": org_unit_type_facet,
                        'full_name': 'Institut',
                        'name': 'Institut',
                        'scope': None,
                        "top_level_facet": org_unit_type_facet,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
                    },
                    'parent': {
                        'location': '',
                        'name': 'Overordnet Enhed',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'org_unit_level': None,
                        'org_unit_type': {
                            'example': None,
                            "facet": org_unit_type_facet,
                            'full_name': 'Afdeling',
                            'name': 'Afdeling',
                            'scope': None,
                            "top_level_facet": org_unit_type_facet,
                            'user_key': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                        },
                        'parent': None,
                        'time_planning': None,
                        'user_key': 'root',
                        'user_settings': {'orgunit': {}},
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'validity': {'from': '2016-01-01', 'to': None}
                    },
                    'time_planning': None,
                    'user_key': 'hum',
                    'user_settings': {'orgunit': {}},
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'validity': {'from': '2016-01-01', 'to': None}
                },
                'time_planning': None,
                'user_key': 'fil',
                'user_settings': {'orgunit': {}},
                'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                'validity': {'from': '2016-01-01', 'to': '2016-10-21'}
            }],
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        # Verify that we are no longer able to see org unit
        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=present',
            [],
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

    def test_terminate_org_unit_validations(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "00000000-0000-0000-0000-000000000000",
            ),
            {
                'error': True,
                'error_key': 'E_ORG_UNIT_NOT_FOUND',
                'description': 'Org unit not found.',
                'org_unit_uuid': '00000000-0000-0000-0000-000000000000',
                'status': 404,
            },
            status_code=404,
            json={
                "validity": {
                    "to": "2016-12-31"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            ),
            {
                'error': True,
                'status': 400,
                'error_key': 'V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES',
                'description': 'Cannot terminate unit with '
                               'active children and roles.',
                'roles': 'Relateret Enhed',
                'child_count': 1,
            },
            status_code=400,
            json={
                "validity": {
                    "to": "2017-01-01"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'status': 400,
                'error_key': 'V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES',
                'description': 'Cannot terminate unit with '
                               'active children and roles.',

                'roles': 'Engagement, Leder, Relateret Enhed, Rolle, '
                         'Tilknytning',
                'child_count': 2,
            },
            status_code=400,
            json={
                "validity": {
                    "to": "2017-05-31"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'status': 400,
                'error_key': 'V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES',
                'description': 'Cannot terminate unit with '
                               'active children and roles.',

                'roles': 'Engagement, Leder, Relateret Enhed, Rolle, '
                         'Tilknytning',
                'child_count': 1,
            },
            status_code=400,
            json={
                "validity": {
                    "to": "2018-12-31"
                }
            },
        )

        for unitid in (
            '85715fc7-925d-401b-822d-467eb4b163b6',
        ):
            self.assertRequestResponse(
                '/service/ou/{}/terminate'.format(
                    unitid,
                ),
                unitid,
                json={
                    "validity": {
                        "to": "2018-12-31"
                    }
                },
                amqp_topics={'org_unit.org_unit.delete': 1},
            )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'error': True,
                'status': 400,
                'error_key': 'V_TERMINATE_UNIT_WITH_ROLES',
                'description': 'Cannot terminate unit with active roles.',
                'roles': 'Engagement, Leder, Relateret Enhed, Rolle, '
                         'Tilknytning',
            },
            status_code=400,
            json={
                "validity": {
                    # inclusion of timestamp is deliberate
                    "to": "2018-12-31T00:00:00+01"
                }
            },
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            ),
            {
                'description': 'Date range exceeds validity range of '
                'associated org unit.',
                'error': True,
                'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                'status': 400,
                'org_unit_uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'valid_from': '2016-01-01',
                'valid_to': None,
                'wanted_valid_from': '1999-12-31',
                'wanted_valid_to': '1999-12-31',
            },
            status_code=400,
            json={
                "validity": {
                    "to": "1999-12-31"
                }
            },
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "04c78fc2-72d2-4d02-b55f-807af19eac48",
            ),
            {
                'description': 'Date range exceeds validity range of '
                'associated org unit.',
                'error': True,
                'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                'status': 400,
                'org_unit_uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'valid_from': '2016-01-01',
                'valid_to': '2018-12-31',
                'wanted_valid_from': '2099-12-31',
                'wanted_valid_to': '2099-12-31',
            },
            status_code=400,
            json={
                "validity": {
                    "to": "2099-12-31"
                }
            },
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(
                "04c78fc2-72d2-4d02-b55f-807af19eac48",
            ),
            {
                'description': 'Date range exceeds validity range of '
                'associated org unit.',
                'error': True,
                'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                'status': 400,
                'org_unit_uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                'valid_from': '2016-01-01',
                'valid_to': '2018-12-31',
                'wanted_valid_from': '2015-12-31',
                'wanted_valid_to': '2015-12-31',
            },
            status_code=400,
            json={
                "validity": {
                    "to": "2015-12-31"
                }
            },
            amqp_topics={'org_unit.org_unit.delete': 1},
            message='No terminating on creation date!'
        )

    @unittest.expectedFailure
    @freezegun.freeze_time('2018-09-11', tz_offset=2)
    def test_terminating_complex_org_unit(self):
        self.load_sample_structures()

        # alas, this import fails due to overzealous validation :(
        unitid = util.load_fixture('organisation/organisationenhed',
                                   'very-edited-unit.json')

        with self.subTest('prerequisites'):
            self.assertRequestResponse(
                '/service/ou/{}'.format(unitid) +
                '/details/org_unit?validity=past',
                [
                    {
                        "name": "AlexTestah",
                        "org": {
                            "name": "Aarhus Universitet",
                            "user_key": "AU",
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                        },
                        'time_planning': None,
                        "org_unit_type": {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Afdeling",
                            "name": "Afdeling",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "afd",
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                        },
                        "parent": {
                            "name": "Overordnet Enhed",
                            "user_ky": "root",
                            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "user_key":
                        "AlexTestah 95c30cd4-1a5c-4025-a23d-430acf018178",
                        "uuid": unitid,
                        "validity": {
                            "from": "2018-08-01",
                            "to": "2018-08-22"
                        }
                    },
                    {
                        "name": "AlexTestikah",
                        "org": {
                            "name": "Aarhus Universitet",
                            "user_key": "AU",
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                        },
                        'time_planning': None,
                        "org_unit_type": {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Afdeling",
                            "name": "Afdeling",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "afd",
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                        },
                        "parent": {
                            "name": "Overordnet Enhed",
                            "user_key": "root",
                            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "user_key": "AlexTestah "
                        "95c30cd4-1a5c-4025-a23d-430acf018178",
                        "uuid": unitid,
                        "validity": {
                            "from": "2018-08-23",
                            "to": "2018-08-23"
                        }
                    },
                    {
                        "name": "AlexTestikah",
                        "org": {
                            "name": "Aarhus Universitet",
                            "user_key": "AU",
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                        },
                        'time_planning': None,
                        "org_unit_type": {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Fakultet",
                            "name": "Fakultet",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "fak",
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                        },
                        "parent": {
                            "name": "Samfundsvidenskabelige fakultet",
                            "user_key": "samf",
                            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                            "validity": {
                                "from": "2017-01-01",
                                "to": None
                            }
                        },
                        "user_key":
                        "AlexTestah 95c30cd4-1a5c-4025-a23d-430acf018178",
                        "uuid": unitid,
                        "validity": {
                            "from": "2018-08-24",
                            "to": "2018-08-31"
                        }
                    }
                ],
            )

            self.assertRequestResponse(
                '/service/ou/{}'.format(unitid) +
                '/details/org_unit?validity=present',
                [{
                    "name": "AlexTest",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    'time_planning': None,
                    "org_unit_type": {
                        "example": None,
                        "facet": org_unit_type_facet,
                        "full_name": "Fakultet",
                        "name": "Fakultet",
                        "scope": None,
                        "top_level_facet": org_unit_type_facet,
                        "user_key": "fak",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                    },
                    "parent": {
                        "name": "Samfundsvidenskabelige fakultet",
                        "user_key": "samf",
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "validity": {
                            "from": "2017-01-01",
                            "to": None
                        }
                    },
                    "user_key":
                    "AlexTestah 95c30cd4-1a5c-4025-a23d-430acf018178",
                    "uuid": unitid,
                    "validity": {
                        "from": "2018-09-01",
                        "to": None,
                    }
                }],
            )

            self.assertRequestResponse(
                '/service/ou/{}'.format(unitid) +
                '/details/org_unit?validity=future',
                [],
            )

        payload = {
            "validity": {
                "to": "2018-09-30"
            }
        }

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(unitid),
            unitid,
            json=payload,
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=present',
            [{
                "name": "AlexTest",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                'time_planning': None,
                "org_unit_type": {
                    "example": None,
                    "facet": org_unit_type_facet,
                    "full_name": "Fakultet",
                    "name": "Fakultet",
                    "scope": None,
                    "top_level_facet": org_unit_type_facet,
                    "user_key": "fak",
                    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                },
                "parent": {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "validity": {
                        "from": "2017-01-01",
                        "to": None
                    }
                },
                "user_key":
                "AlexTestah 95c30cd4-1a5c-4025-a23d-430acf018178",
                "uuid": unitid,
                "validity": {
                    "from": "2018-09-01",
                    "to": "2018-09-30",
                }
            }],
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

        self.assertRequestResponse(
            '/service/ou/{}'.format(unitid) +
            '/details/org_unit?validity=future',
            [],
            amqp_topics={'org_unit.org_unit.delete': 1},
        )

    @freezegun.freeze_time('2016-01-01', tz_offset=2)
    def test_get_integration_data(self):
        self.load_sample_structures()
        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        self.assertRequestResponse(
            '/service/ou/{}/integration-data'.format(org_unit_uuid),
            {
                'integration_data': {},
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'validity': {
                    'from': '2016-01-01',
                    'to': None
                }
            }
        )

    @freezegun.freeze_time('2016-01-01', tz_offset=2)
    def test_edit_integration_data(self):
        self.load_sample_structures()
        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'

        req = {
            "type": "org_unit",
            "data": {
                "uuid": org_unit_uuid,
                "integration_data": {"baywatchname": "Hasselhoff"},
                "validity": {
                    "from": "2016-01-01",
                    "to": "2016-01-02",
                },
            },
        }

        self.assertRequestResponse(
            '/service/details/edit',
            org_unit_uuid,
            json=req,
            amqp_topics={'org_unit.org_unit.update': 1},
        )

        expected_organisationenhedegenskaber = [{
            'brugervendtnoegle': 'hum',
            'enhedsnavn': 'Humanistisk fakultet',
            'integrationsdata': '{"baywatchname": "Hasselhoff"}',
            'virkning': {
                'from': '2016-01-01 00:00:00+01',
                'from_included': True,
                'to': '2016-01-03 00:00:00+01',
                'to_included': False
            }
        }, {
            'brugervendtnoegle': 'hum',
            'enhedsnavn': 'Humanistisk fakultet',
            'integrationsdata': '{}',
            'virkning': {
                'from': '2016-01-03 00:00:00+01',
                'from_included': True,
                'to': 'infinity',
                'to_included': False
            }
        }]

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual = c.organisationenhed.get(org_unit_uuid)

        self.assertEqual(
            expected_organisationenhedegenskaber,
            sorted(actual['attributter']['organisationenhedegenskaber'],
                   key=lambda attrs: attrs['virkning']['from']),
        )

    def test_tree(self):
        self.load_sample_structures()

        for path, expected in util.get_fixture('test_trees.json').items():
            with self.subTest(path):
                self.assertRequestResponse(path, expected)
