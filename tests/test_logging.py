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
