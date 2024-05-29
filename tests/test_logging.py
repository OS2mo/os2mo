# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import structlog

from mo_ldap_import_export.processors import _hide_cpr
from mo_ldap_import_export.processors import mask_cpr

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


def test_mask_cpr():
    cf = structlog.testing.CapturingLoggerFactory()
    structlog.configure(logger_factory=cf, processors=[mask_cpr])
    logger = structlog.stdlib.get_logger()

    logger.info("My cpr no is 010101-1234")
    logger.info("My telephone no is 6001011234")
    messages = [w.kwargs for w in cf.logger.calls]

    assert messages[0]["event"] == "My cpr no is 010101-xxxx"
    assert messages[1]["event"] == "My telephone no is 6001011234"


def test_mask_cpr2():
    cf = structlog.testing.CapturingLoggerFactory()
    structlog.configure(logger_factory=cf, processors=[mask_cpr])
    logger = structlog.stdlib.get_logger()

    cpr_no = "010101-1234"

    class CprClass:
        def __init__(self, cpr):
            self.cpr = cpr

        def __repr__(self):
            return f"cpr-no = {self.cpr}"

        def __str__(self):
            return self.cpr

    cpr_obj = CprClass(cpr_no)

    logger.info(f"My cpr no is {cpr_no}")
    logger.info("The cpr attribute is", cpr=cpr_no)
    logger.info("The cpr-no is hidden in this object", obj=cpr_obj)

    messages = [w.kwargs for w in cf.logger.calls]
    for message in messages:
        for entry in message.values():
            assert cpr_no not in entry
    assert "010101-xxxx" in str(messages[0]["event"])
    assert "010101-xxxx" in str(messages[1]["cpr"])
    assert "010101-xxxx" in str(messages[2]["obj"])
