# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date


def get_at_date_sql(at: date | None = None):
    if at is not None:
        return "to_timestamp(:at_datetime, 'YYYY-MM-DD HH24:MI:SS')", {
            "at_datetime": at.isoformat()
        }

    return "now()", {}
