# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import random
import service_person_stamdata_udvidet
import pathlib
import requests

from structlog import get_logger

from .. import util, config
from .. import exceptions

logger = get_logger()


def is_dummy_mode():
    settings = config.get_settings()
    if not config.is_production():
        # force dummy during tests and development, and make it
        # configurable in production
        #
        # the underlying logic is that developers know how to edit
        # source code, wheras that's a big no-no in production
        return True

    return settings.dummy_mode


def check_config():
    if is_dummy_mode():
        return True

    settings = config.get_settings()

    SP_CERTIFICATE_PATH = settings.sp_certificate_path
    if not SP_CERTIFICATE_PATH:
        raise ValueError("Serviceplatformen certificate path must be configured")

    p = pathlib.Path(SP_CERTIFICATE_PATH)
    if not p.exists():
        raise FileNotFoundError("Serviceplatformen certificate not found")
    if not p.stat().st_size:
        raise ValueError("Serviceplatformen certificate can not be empty")

    return True


def get_citizen(cpr):
    settings = config.get_settings()
    if not util.is_cpr_number(cpr):
        raise ValueError("invalid CPR number!")

    if is_dummy_mode():
        return _get_citizen_stub(cpr)
    else:
        sp_uuids = {
            "service_agreement": str(settings.sp_agreement_uuid),
            "user_system": str(settings.sp_user_system_uuid),
            "user": str(settings.sp_municipality_uuid),
            "service": str(settings.sp_service_uuid),
        }
        certificate = settings.sp_certificate_path
        sp_production = settings.sp_production
        try:
            return service_person_stamdata_udvidet.get_citizen(
                sp_uuids, certificate, cpr, production=sp_production
            )
        except requests.HTTPError as e:
            if "PNRNotFound" in e.response.text:
                raise KeyError("CPR not found")
            else:
                logger.exception(exception=e)
                raise e
        except requests.exceptions.SSLError as e:
            logger.exception(exception=e)
            exceptions.ErrorCodes.E_SP_SSL_ERROR()


MALE_FIRST_NAMES = [
    "William",
    "Oliver",
    "Noah",
    "Emil",
    "Victor",
    "Magnus",
    "Frederik",
    "Mikkel",
    "Lucas",
    "Alexander",
    "Oscar",
    "Mathias",
    "Sebastian",
    "Malthe",
    "Elias",
    "Christian",
    "Mads",
    "Gustav",
    "Villads",
    "Tobias",
    "Anton",
    "Carl",
    "Silas",
    "Valdemar",
    "Benjamin",
    "Nikolaj",
    "Marcus",
    "August",
    "Sander",
    "Jacob",
    "Jonas",
    "Adam",
    "Andreas",
    "Simon",
    "Jonathan",
    "Alfred",
    "Philip",
    "Storm",
    "Nicklas",
    "Rasmus",
    "Felix",
    "Aksel",
    "Johan",
    "Daniel",
    "Tristan",
    "Bertram",
    "Liam",
    "Kasper",
    "Laurits",
    "Marius",
]

FEMALE_FIRST_NAMES = [
    "Emma",
    "Ida",
    "Clara",
    "Laura",
    "Isabella",
    "Sofia",
    "Sofie",
    "Anna",
    "Mathilde",
    "Freja",
    "Caroline",
    "Lærke",
    "Maja",
    "Josefine",
    "Liva",
    "Alberte",
    "Karla",
    "Victoria",
    "Olivia",
    "Alma",
    "Mille",
    "Sarah",
    "Frida",
    "Julie",
    "Emilie",
    "Marie",
    "Ella",
    "Nanna",
    "Signe",
    "Agnes",
    "Nicoline",
    "Malou",
    "Filippa",
    "Johanne",
    "Cecilie",
    "Silje",
    "Lea",
    "Asta",
    "Astrid",
    "Naja",
    "Celina",
    "Tilde",
    "Emily",
    "Luna",
    "Ellen",
    "Katrine",
    "Esther",
    "Merle",
    "Selma",
    "Liv",
]

LAST_NAMES = [
    "Nielsen",
    "Jensen",
    "Hansen",
    "Pedersen",
    "Andersen",
    "Christensen",
    "Larsen",
    "Sørensen",
    "Rasmussen",
    "Jørgensen",
    "Petersen",
    "Madsen",
    "Kristensen",
    "Olsen",
    "Thomsen",
    "Christiansen",
    "Poulsen",
    "Johansen",
    "Møller",
    "Mortensen",
]

# as of 2018, the oldest living Dane was born in 1908...
EARLIEST_BIRTHDATE = util.parsedatetime("1901-01-01")


def _get_citizen_stub(cpr):
    # Seed random with CPR number to ensure consistent output
    random.seed(cpr)

    # disallow future CPR numbers and people too old to occur
    # (interestingly, the latter also avoids weirdness related to
    # Denmark using Copenhagen solar time in the 19th century...)
    if not EARLIEST_BIRTHDATE < util.get_cpr_birthdate(cpr) < util.now():
        raise KeyError("CPR not found")

    if (int(cpr[-1]) % 2) == 0:
        first_name = random.choice(FEMALE_FIRST_NAMES)
    else:
        first_name = random.choice(MALE_FIRST_NAMES)

    return {"fornavn": first_name, "efternavn": random.choice(LAST_NAMES)}
