# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from typing import Any

import httpx
import structlog

from mora import config
from mora import exceptions
from mora import mapping
from mora import serviceplatformen

logger = structlog.stdlib.get_logger()


def _handle_erstatningspersonnummer(cpr: str) -> dict | None:
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


def _get_citizen(cpr: str, settings: config.Settings) -> dict[str, Any]:
    assert settings.sp_settings is not None
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
        return serviceplatformen.get_citizen(
            sp_uuids,
            certificate,
            cpr,
            production=sp_production,
            api_version=sp_api_version,
        )
    except httpx.HTTPStatusError as e:  # pragma: no cover
        if "PNRNotFound" in e.response.text:
            raise KeyError("CPR not found")
        else:
            logger.exception(event="HTTPStatusError", exception=e)
            raise e
    except httpx.ConnectError as e:  # pragma: no cover
        logger.exception(event="ConnectError", exception=e)
        exceptions.ErrorCodes.E_SP_SSL_ERROR()
