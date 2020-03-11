# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import random

import service_person_stamdata_udvidet
import pathlib
import requests
import flask
from .. import util
from .. import exceptions
from .. import settings


def is_dummy_mode(app):
    if app.env != 'production':
        # force dummy during tests and development, and make it
        # configurable in production
        #
        # the underlying logic is that developers know how to edit
        # source code, wheras that's a big no-no in production
        return True

    return settings.config['dummy_mode']


def check_config(app):
    if is_dummy_mode(app):
        return True

    config = settings.config

    missing = [
        k
        for k in (
            "uuid",  # "SP_SERVICE_UUID",
            "agreement_uuid",  # "SP_SERVICE_AGREEMENT_UUID",
            "municipality_uuid",  # "SP_MUNICIPALITY_UUID",
            "system_uuid",  # "SP_SYSTEM_UUID",
        )
        if not util.is_uuid(config["service_platformen"][k])
    ]

    if missing:
        raise ValueError(
            "Serviceplatformen uuids must be valid: {}".format(
                ", ".join(missing)
            )
        )

    SP_CERTIFICATE_PATH = config["service_platformen"]["certificate_path"]
    if not SP_CERTIFICATE_PATH:
        raise ValueError(
            "Serviceplatformen certificate path must be configured"
        )

    p = pathlib.Path(SP_CERTIFICATE_PATH)
    if not p.exists():
        raise FileNotFoundError("Serviceplatformen certificate not found")
    if not p.stat().st_size:
        raise ValueError("Serviceplatformen certificate can not be empty")

    return True


def get_citizen(cpr):
    config = settings.config
    if not util.is_cpr_number(cpr):
        raise ValueError('invalid CPR number!')

    if is_dummy_mode(flask.current_app):
        return _get_citizen_stub(cpr)
    else:
        sp_uuids = {
            'service_agreement': config["service_platformen"]["agreement_uuid"],
            'user_system': config["service_platformen"]["system_uuid"],
            'user': config["service_platformen"]["municipality_uuid"],
            'service': config["service_platformen"]["uuid"]
        }
        certificate = config["service_platformen"]["certificate_path"]
        sp_production = config["service_platformen"]["sp_production"]
        try:
            return service_person_stamdata_udvidet.get_citizen(
                sp_uuids, certificate, cpr, production=sp_production)
        except requests.HTTPError as e:
            if "PNRNotFound" in e.response.text:
                raise KeyError("CPR not found")
            else:
                flask.current_app.logger.exception(e)
                raise e
        except requests.exceptions.SSLError as e:
            flask.current_app.logger.exception(e)
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
