from structlog.testing import capture_logs

from mo_ldap_import_export.logging import logger
from mo_ldap_import_export.processors import _hide_cpr


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
    with capture_logs() as cap_logs:
        logger.info("My cpr no is 010101-1234")
        logger.info("My telephone no is 6001011234")
        messages = [w for w in cap_logs if w["log_level"] == "info"]

        assert messages[0]["event"] == "My cpr no is 010101-xxxx"
        assert messages[1]["event"] == "My telephone no is 6001011234"

    cpr_no = "010101-1234"

    class CprClass:
        def __init__(self, cpr):
            self.cpr = cpr

        def __repr__(self):
            return f"cpr-no = {self.cpr}"

        def __str__(self):
            return self.cpr

    cpr_obj = CprClass(cpr_no)

    with capture_logs() as cap_logs:
        logger.info(f"My cpr no is {cpr_no}")
        logger.info("The cpr attribute is", cpr=cpr_no)
        logger.info("The cpr-no is hidden in this object", obj=cpr_obj)

        messages = [w for w in cap_logs if w["log_level"] == "info"]

        for message in messages:
            assert cpr_no not in str(message)
            assert "010101-xxxx" in str(message)
