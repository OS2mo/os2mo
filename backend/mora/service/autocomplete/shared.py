# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import time
from uuid import UUID

from more_itertools import one
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import Row

from mora import util
from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.address_handler.email import EmailAddressHandler

UUID_SEARCH_MIN_PHRASE_LENGTH = 7


def get_at_date_sql(at: date | None = None):
    if at is not None:
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


def get_graphql_equivalent_by_uuid(
    graphql_data_objects: list[dict], lookup_uuid: UUID, at: date | None
) -> dict | None:
    at = at if at is not None else util.now().date()
    at_dt = datetime.combine(at, time.min).astimezone(util.DEFAULT_TIMEZONE)

    for gql_data_object in graphql_data_objects:
        if gql_data_object["uuid"] != str(lookup_uuid):
            continue

        # single result
        if len(gql_data_object["objects"]) == 1:
            return one(gql_data_object["objects"])
        # coverage: pause
        # more than one result - filter by valid validity
        objs_in_validity = list(
            filter(
                lambda o: gql_object_validity_valid(o, at_dt),
                gql_data_object["objects"],
            )
        )
        if len(objs_in_validity) == 1:
            return one(objs_in_validity)

        # No objects with valid validity - default to "current"
        return gql_data_object["current"]
        # coverage: unpause
    # coverage: pause
    return None
    # coverage: unpause


async def string_to_urn(urn_string: str) -> str:
    if util.is_uuid(urn_string):
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


def gql_object_validity_valid(gql_obj: dict, at_date: date | None) -> bool | None:  # pragma: no cover
    if at_date is None:
        return None

    from_date = gql_obj["validity"].get("from", None)
    from_date = (
        datetime.fromisoformat(from_date) if from_date else util.NEGATIVE_INFINITY
    )

    to_date = gql_obj["validity"].get("to", None)
    to_date = datetime.fromisoformat(to_date) if to_date else util.POSITIVE_INFINITY

    return from_date <= at_date <= to_date
