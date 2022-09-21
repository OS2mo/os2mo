# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import random
from typing import Any
from typing import Union

import requests
import service_person_stamdata_udvidet
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field
from structlog import get_logger

from mora import config
from mora import exceptions
from mora import mapping
from mora import util
from mora.service.cpr import router as cpr_router

logger = get_logger()


def get_citizen(cpr: str) -> dict[str, Any]:
    settings = config.get_settings()
    if settings.is_dummy_mode():
        return _get_citizen_stub(cpr)

    sp_uuids = {
        "service_agreement": str(settings.sp_settings.sp_agreement_uuid),
        "user_system": str(settings.sp_settings.sp_user_system_uuid),
        "user": str(settings.sp_settings.sp_municipality_uuid),
        "service": str(settings.sp_settings.sp_service_uuid),
    }
    certificate = settings.sp_settings.sp_certificate_path
    sp_production = settings.sp_settings.sp_production
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


def _get_citizen_stub(cpr: str) -> dict[str, str]:
    # Seed random with CPR number to ensure consistent output
    random.seed(cpr)

    # If feature flag is set, check birthdate encoded in CPR number
    settings = config.get_settings()
    if settings.cpr_validate_birthdate:
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


class SearchCPRReturn(BaseModel):
    class Config:
        schema_extra = {"example": {"name": "John Doe", "cpr_no": "0101501234"}}

    name: str = Field(description="Name of the person.")
    cpr_no: str = Field(description="CPR number of the person.")


@cpr_router.get(
    "/e/cpr_lookup/",
    response_model=Union[SearchCPRReturn, dict[str, str]],
    response_model_exclude_unset=True,
    responses={
        "404": {"description": "No person found"},
        "400": {"description": "Invalid CPR number"},
        "500": {"description": "Unknown error"},
    },
)
def search_cpr(
    q: str = Query(..., description="The CPR number to search for")
) -> dict[str, str]:
    """Lookup a CPR number in Serviceplatformen and retrieve the name.

    This endpoint is only used when creating new employees through the MO GUI
    to get their names automatically from their CPR.
    You can still create employees, but all data has to be typed in manually.

    Args:
        q: The CPR number to search for

    Raises:
        V_NO_PERSON_FOR_CPR: If CPR match could be found.
        V_CPR_NOT_VALID: If the CPR number seems invalid.
        E_UNKNOWN: If an unexpected situation occurs.

    Returns:
        An empty dict if Serviceplatformen is disabled (`ENABLE_SP=false`).
        A SearchCPRReturn model if Serviceplatform is enabled.
    """
    if not config.get_settings().enable_sp:
        return {}

    cpr = q
    if not util.is_cpr_number(cpr):
        exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr)

    try:
        sp_data = get_citizen(cpr)
    except KeyError:
        exceptions.ErrorCodes.V_NO_PERSON_FOR_CPR(cpr=cpr)
    except ValueError:
        exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr)
    except Exception:
        exceptions.ErrorCodes.E_UNKNOWN(cpr=cpr)
    return format_cpr_response(sp_data, cpr)


def format_cpr_response(sp_data: dict[str, Any], cpr: str) -> dict[str, str]:
    """Convert a Serviceplatformen response to a SearchCPRReturn dict.

    Args:
        sp_data: Service platform response.
        cpr: CPR number of the person.

    Returns:
        A SearchCPRReturn model dict.
    """
    first_name = sp_data.get("fornavn")
    middle_name = sp_data.get("mellemnavn")
    last_name = sp_data.get("efternavn")

    # Filter empty name components, and construct full name string
    name = " ".join(filter(None, [first_name, middle_name, last_name]))

    return {mapping.NAME: name, mapping.CPR_NO: cpr}
