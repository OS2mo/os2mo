# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import structlog
from fastapi import HTTPException

from .types import DN

logger = structlog.stdlib.get_logger()


class AcknowledgeException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=200, detail=message)


class RequeueException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=409, detail=message)


class MultipleObjectsReturnedException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=409, detail=message)


class NoObjectsReturnedException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=500, detail=message)


class IncorrectMapping(HTTPException):
    """Raised when the integration is improperly configured."""

    def __init__(self, message: str) -> None:
        super().__init__(status_code=500, detail=message)


class ReadOnlyException(HTTPException):
    """Raised when the integration would write if not in read-only mode."""

    def __init__(
        self,
        message: str,
        dn: DN,
        requested_state: dict[str, list],
        old_state: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=200,  # acknowledge event
            detail={
                "message": message,
                "dn": dn,
                "requested_state": requested_state,
                "old_state": old_state,
            },
        )


class UUIDNotFoundException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=404, detail=message)


class IgnoreChanges(HTTPException):
    """Exception raised if the import/export checks reject a message."""

    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=200,  # acknowledge event
            detail=message,
        )


class InvalidCPR(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=200,  # acknowledge event
            detail=message,
        )


class DryRunException(HTTPException):
    def __init__(self, message: str, dn: DN, details: dict[str, Any]) -> None:
        assert "dn" not in details
        assert "message" not in details
        super().__init__(
            status_code=451, detail={"message": message, "dn": dn, **details}
        )


class SkipObject(Exception):
    """Exception raised if the ldap_to_mo object should be skipped."""
