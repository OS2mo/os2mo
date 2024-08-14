# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import structlog

from mo_ldap_import_export.processors import _hide_cpr

logger = structlog.get_logger()


def test_hide_cpr():
    cpr_string = (
        "my cpr no. is 010101-1234. "
        "My wife's cpr no. is 0102011235. "
        "This is not a cpr-no, but a telephone number: 500203-1236"
    )

    masked_string = _hide_cpr(cpr_string)

    assert "1234" not in masked_string
    assert "1235" not in masked_string
    assert "1236" in masked_string
