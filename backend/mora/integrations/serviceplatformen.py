#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import random

import service_person_stamdata_udvidet
import logging
import pathlib
import requests

from .. import util
from .. import settings
from .. import exceptions


def check_config(config):
    UUID_EMPTY = "00000000-0000-0000-0000-000000000000"
    DUMMY_MODE = config.get("DUMMY_MODE", False)
    if isinstance(DUMMY_MODE, str) and DUMMY_MODE.lower() in ['true', 'false']:
        if DUMMY_MODE.lower() == 'true':
            DUMMY_MODE = True
        else:
            DUMMY_MODE = False
        config["DUMMY_MODE"] = DUMMY_MODE

    if DUMMY_MODE:
        return True

    missing = []
    for uuid in [
        "SP_SERVICE_UUID",
        "SP_SERVICE_AGREEMENT_UUID",
        "SP_MUNICIPALITY_UUID",
        "SP_SYSTEM_UUID"
    ]:
        # check for both 0's and uuid-length
        if (
            config.get(uuid, UUID_EMPTY) == UUID_EMPTY or
            len(config.get(uuid, "")) != len(UUID_EMPTY)
        ):
            missing.append(uuid)

    if len(missing):
        raise ValueError(
            "Serviceplatformen uuids must be valid: {}".format(
                ", ".join(missing)
            )
        )

    SP_CERTIFICATE_PATH = config.get("SP_CERTIFICATE_PATH", "")
    if not SP_CERTIFICATE_PATH:
        raise ValueError(
            "Serviceplatformen certificate path must be configured: "
            "SP_CERTIFICATE_PATH"
        )

    p = pathlib.Path(SP_CERTIFICATE_PATH)
    if not p.exists():
        raise FileNotFoundError(
            "Serviceplatformen certificate not found: "
            "SP_CERTIFICATE_PATH"
        )
    if not p.stat().st_size:
        raise ValueError(
            "Serviceplatformen certificate can not be empty: "
            "SP_CERTIFICATE_PATH"
        )

    return True


def get_citizen(cpr):
    if not util.is_cpr_number(cpr):
        raise ValueError('invalid CPR number!')

    if settings.DUMMY_MODE:
        return _get_citizen_stub(cpr)
    else:
        sp_uuids = {
            'service_agreement': settings.SP_SERVICE_AGREEMENT_UUID,
            'user_system': settings.SP_SYSTEM_UUID,
            'user': settings.SP_MUNICIPALITY_UUID,
            'service': settings.SP_SERVICE_UUID
        }
        certificate = settings.SP_CERTIFICATE_PATH
        try:
            return service_person_stamdata_udvidet.get_citizen(
                sp_uuids, certificate, cpr)
        except requests.HTTPError as e:
            if "PNRNotFound" in e.response.text:
                raise KeyError("CPR not found")
            else:
                logging.getLogger(__name__).exception(e)
                raise e
        except requests.exceptions.SSLError as e:
            logging.getLogger(__name__).exception(e)
            exceptions.ErrorCodes.E_SP_SSL_ERROR()


MALE_FIRST_NAMES = [
    'William',
    'Oliver',
    'Noah',
    'Emil',
    'Victor',
    'Magnus',
    'Frederik',
    'Mikkel',
    'Lucas',
    'Alexander',
    'Oscar',
    'Mathias',
    'Sebastian',
    'Malthe',
    'Elias',
    'Christian',
    'Mads',
    'Gustav',
    'Villads',
    'Tobias',
    'Anton',
    'Carl',
    'Silas',
    'Valdemar',
    'Benjamin',
    'Nikolaj',
    'Marcus',
    'August',
    'Sander',
    'Jacob',
    'Jonas',
    'Adam',
    'Andreas',
    'Simon',
    'Jonathan',
    'Alfred',
    'Philip',
    'Storm',
    'Nicklas',
    'Rasmus',
    'Felix',
    'Aksel',
    'Johan',
    'Daniel',
    'Tristan',
    'Bertram',
    'Liam',
    'Kasper',
    'Laurits',
    'Marius',
]

FEMALE_FIRST_NAMES = [
    'Emma',
    'Ida',
    'Clara',
    'Laura',
    'Isabella',
    'Sofia',
    'Sofie',
    'Anna',
    'Mathilde',
    'Freja',
    'Caroline',
    'Lærke',
    'Maja',
    'Josefine',
    'Liva',
    'Alberte',
    'Karla',
    'Victoria',
    'Olivia',
    'Alma',
    'Mille',
    'Sarah',
    'Frida',
    'Julie',
    'Emilie',
    'Marie',
    'Ella',
    'Nanna',
    'Signe',
    'Agnes',
    'Nicoline',
    'Malou',
    'Filippa',
    'Johanne',
    'Cecilie',
    'Silje',
    'Lea',
    'Asta',
    'Astrid',
    'Naja',
    'Celina',
    'Tilde',
    'Emily',
    'Luna',
    'Ellen',
    'Katrine',
    'Esther',
    'Merle',
    'Selma',
    'Liv',
]

LAST_NAMES = [
    'Nielsen',
    'Jensen',
    'Hansen',
    'Pedersen',
    'Andersen',
    'Christensen',
    'Larsen',
    'Sørensen',
    'Rasmussen',
    'Jørgensen',
    'Petersen',
    'Madsen',
    'Kristensen',
    'Olsen',
    'Thomsen',
    'Christiansen',
    'Poulsen',
    'Johansen',
    'Møller',
    'Mortensen',
]

# as of 2018, the oldest living Dane was born in 1908...
EARLIEST_BIRTHDATE = util.parsedatetime('1901-01-01')


def _get_citizen_stub(cpr):
    # Seed random with CPR number to ensure consistent output
    random.seed(cpr)

    # disallow future CPR numbers and people too old to occur
    # (interestingly, the latter also avoids weirdness related to
    # Denmark using Copenhagen solar time in the 19th century...)
    if not EARLIEST_BIRTHDATE < util.get_cpr_birthdate(cpr) < util.now():
        raise KeyError('CPR not found')

    if (int(cpr[-1]) % 2) == 0:
        first_name = random.choice(FEMALE_FIRST_NAMES)
    else:
        first_name = random.choice(MALE_FIRST_NAMES)

    return {
        'fornavn': first_name,
        'efternavn': random.choice(LAST_NAMES)
    }
