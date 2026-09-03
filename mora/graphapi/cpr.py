# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import re
from textwrap import dedent

import httpx
import strawberry
import structlog

from mora import config
from mora import serviceplatformen
from mora import util
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo

logger = structlog.stdlib.get_logger()


@strawberry.input(description="CPR filter.")
class CPRFilter:
    cpr_number: str = strawberry.field(description="The CPR number to look up.")


@strawberry.type(description="Person found by CPR lookup.")
class CPRPerson:
    name: str = strawberry.field(
        description=dedent(
            """\
            Name of the person.

            Example: "John Doe"
            """
        )
    )
    cpr_number: str = strawberry.field(
        description=dedent(
            """\
            CPR number of the person.

            Example: "6101501234"
            """
        )
    )


async def cpr_resolver(info: MOInfo, filter: CPRFilter) -> CPRPerson:
    cpr = filter.cpr_number

    session: AsyncSession = info.context.session
    access_log(
        session,
        settings=info.context.settings,
        operation="lookup_cpr",
        class_name="CPRPerson",
        arguments={"filter": filter},
        # No UUIDs are logged, as the person is read from Serviceplatformen rather than MO.
        uuids=[],
    )

    settings = info.context.settings
    if not settings.enable_sp:
        logger.error("Serviceplatformen not enabled")
        raise ValueError(
            dedent(
                """\
                CPR number lookup is not possible, because the 'serviceplatformen'
                integration is disabled.
                """
            )
        )

    if not util.is_cpr_number(cpr):
        logger.error("CPR number not valid")
        raise ValueError("The given CPR number is not valid.")

    if fictitious := _handle_erstatningspersonnummer(cpr):
        return fictitious

    # Run the sync Serviceplatformen call (httpx.post + Jinja render) in a thread
    # to avoid blocking the event loop while waiting for the SOAP response.
    return await asyncio.to_thread(_get_citizen, cpr, settings)


def _handle_erstatningspersonnummer(cpr: str) -> CPRPerson | None:
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

    if not match:  # pragma: no cover
        logger.warning(event="Could not parse CPR", value=cpr)
        return None

    parsed: dict = {k: int(v) for k, v in match.groupdict().items()}
    day: int = parsed["day"]
    if 61 <= day <= 91:
        logger.debug(event="Detected 'erstatningspersonnummer'")
        return CPRPerson(name="", cpr_number=cpr)

    logger.debug(event="Detected normal CPR")
    return None


def _get_citizen(cpr: str, settings: config.Settings) -> CPRPerson:
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
        sp_data = serviceplatformen.get_citizen(
            sp_uuids,
            certificate,
            cpr,
            production=sp_production,
            api_version=sp_api_version,
        )
    except httpx.HTTPStatusError as e:
        if "PNRNotFound" in e.response.text:
            logger.exception("CPR person not found", exception=e)
            raise ValueError(
                "No person was found that matches the given CPR number."
            ) from e
        else:  # pragma: no cover
            logger.exception("Unexpected HTTP error during CPR lookup", exception=e)
            raise
    except httpx.TimeoutException as e:
        logger.exception("HTTP timeout during CPR lookup", exception=e)
        raise ValueError(
            dedent(
                """\
                CPR number lookup is not possible, because the 'serviceplatformen'
                integration could not be reached.
                """
            )
        ) from e
    except httpx.ConnectError as e:
        logger.exception("HTTP connection error", exception=e)
        raise ValueError(
            dedent(
                """\
                CPR number lookup is not possible, because the 'serviceplatformen'
                integration could not be reached.
                """
            )
        ) from e
    except Exception as e:  # pragma: no cover
        logger.exception("Unexpected error during CPR lookup", exception=e)
        raise

    # handle edge case where serviceplatformen.get_citizen returns an error dict.
    # This can happen if an HTTP request succeded but returned a code other than 200
    if error := sp_data.get("Error"):  # pragma: no cover
        exception = RuntimeError(error)
        logger.error("Unexpected error during CPR lookup", error=error)
        raise exception

    first_name = sp_data.get("fornavn")
    middle_name = sp_data.get("mellemnavn")
    last_name = sp_data.get("efternavn")

    name = " ".join(
        segment for segment in [first_name, middle_name, last_name] if segment
    )

    return CPRPerson(name=name, cpr_number=cpr)
