# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from uuid import UUID
from more_itertools import one
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import Row

from mora import util
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
    graphql_data_elemtns: list[dict], org_unit_uuid: UUID
) -> dict | None:
    for element in graphql_data_elemtns:
        if element["uuid"] == str(org_unit_uuid):
            return one(element["objects"])

    return None


def string_to_urn(urn_string: str) -> str:
    if util.is_uuid(urn_string):
        return urn_string

    email_handler = EmailAddressHandler(value=urn_string, visibility=None)
    if email_handler.validate_value():
        return email_handler.urn

    return util.urnquote(urn_string)
