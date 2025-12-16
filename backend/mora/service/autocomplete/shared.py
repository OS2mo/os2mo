# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from mora import util
from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.address_handler.email import EmailAddressHandler
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import Row

UUID_SEARCH_MIN_PHRASE_LENGTH = 7


def get_at_date_sql(at: date | None = None):
    if at is not None:  # pragma: no cover
        return "to_timestamp(:at_datetime, 'YYYY-MM-DD HH24:MI:SS')", {
            "at_datetime": at.isoformat()
        }

    return "now()", {}


def read_sqlalchemy_result(result: Result) -> [Row]:
    rows = []
    while True:
        chunk = result.fetchmany(1000)
        if not chunk:
            break

        for row in chunk:
            rows.append(row)

    return rows


async def string_to_urn(urn_string: str) -> str:
    if util.is_uuid(urn_string):  # pragma: no cover
        return urn_string

    # EMAIL urn handling
    try:
        await EmailAddressHandler.validate_value(urn_string)
        return EmailAddressHandler(
            value=urn_string, visibility=None
        ).urn  # pragma: no cover
    except HTTPException as e:
        if e.key != ErrorCodes.V_INVALID_ADDRESS_EMAIL:  # pragma: no cover
            raise e
        else:
            pass

    # Default/fallback urn handling
    return util.urnquote(urn_string)
