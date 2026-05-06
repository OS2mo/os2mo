# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from typing import Any

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

    sp_uuids = {
        "service_agreement": str(settings.sp_settings.sp_agreement_uuid),
        "user_system": str(settings.sp_settings.sp_system_uuid),
        "user": str(settings.sp_settings.sp_municipality_uuid),
        "service": str(settings.sp_settings.sp_service_uuid),
    }
    certificate = str(settings.sp_settings.sp_certificate_path)
    sp_production = settings.sp_settings.sp_production
    sp_api_version = settings.sp_settings.sp_api_version
    try:
        return service_person_stamdata_udvidet.get_citizen(
            sp_uuids,
            certificate,
            cpr,
            production=sp_production,
            api_version=sp_api_version,
        )
    except requests.HTTPError as e:  # pragma: no cover
        if "PNRNotFound" in e.response.text:
            raise KeyError("CPR not found")
        else:
            logger.exception(event="HTTPError", exception=e)
            raise e
    except requests.exceptions.SSLError as e:  # pragma: no cover
        logger.exception(event="SSLError", exception=e)
        exceptions.ErrorCodes.E_SP_SSL_ERROR()


def _handle_erstatningspersonnummer(cpr: str) -> dict:
    """Handle "erstatningspersonnummer" CPR numbers - that is, CPR numbers where the
    'day' part of the birthdate is in the range 61-91.

    Allowing such CPR numbers to be "looked" up means that customers will be able to
    create MO persons with fictitious CPR numbers. This is useful for service accounts,
    robots, etc., when the corresponding user in an external system uses the same
    fictitious CPR number.

    References:
    - https://cpr.dk/cpr-systemet/erstatningspersonnummer-i-eksterne-systemer
    - https://cpr.dk/media/12068/erstatningspersonnummerets-opbygning.pdf
    """

    # Parse CPR using a regular expression (rather than `mora.util.get_cpr_birthdate`,
    # which needs to construct a `datetime.datetime` object. This cannot be done for
    # CPRs where the 'day' part is between 61 and 91.)
    pattern: re.Pattern = re.compile(
        r"(?P<day>\d{2})(?P<month>\d{2})(?P<year>\d{2})[\-|\s]{0,1}(?P<code>\d{4})"
    )
    match: re.Match | None = re.match(pattern, cpr)
    if match:
        parsed: dict = {k: int(v) for k, v in match.groupdict().items()}
        day: int = parsed["day"]
        if 61 <= day <= 91:
            logger.debug(event="detected 'erstatningspersonnummer'")
            # Return the CPR number entered by the user, along with a blank name.
            return {mapping.NAME: "", mapping.CPR_NO: cpr}
        else:
            logger.debug(event="detected normal CPR")
    else:
        logger.warning(event="could not parse CPR", value=cpr)


class SearchCPRReturn(BaseModel):
    class Config:
        schema_extra = {"example": {"name": "John Doe", "cpr_no": "0101501234"}}

    name: str = Field(description="Name of the person.")
    cpr_no: str = Field(description="CPR number of the person.")


@cpr_router.get(
    "/e/cpr_lookup/",
    response_model=SearchCPRReturn | dict[str, str],
    response_model_exclude_unset=True,
    responses={
        "404": {"description": "No person found"},
        "400": {"description": "Invalid CPR number"},
        "500": {"description": "Unknown error"},
    },
)
def search_cpr(
    q: str = Query(..., description="The CPR number to search for"),
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
    cpr = q
    if not util.is_cpr_number(cpr):
        exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr)

    if not config.get_settings().enable_sp:
        return {}

    # Check for "erstatningspersonnummer"
    response: dict = _handle_erstatningspersonnummer(cpr)
    if response:
        return response
    # coverage: pause
    try:
        sp_data = get_citizen(cpr)
    except KeyError as e:
        logger.exception(event="no person found for cpr", exception=e)
        exceptions.ErrorCodes.V_NO_PERSON_FOR_CPR(cpr=cpr)
    except ValueError as e:
        logger.exception(event="invalid CPR", exception=e)
        exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr)
    except Exception as e:
        logger.exception(event="unknown error in cpr lookup", exception=e)
        exceptions.ErrorCodes.E_UNKNOWN(cpr=cpr)
    return format_cpr_response(sp_data, cpr)
    # coverage: unpause


def format_cpr_response(
    sp_data: dict[str, Any], cpr: str
) -> dict[str, str]:  # pragma: no cover
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
