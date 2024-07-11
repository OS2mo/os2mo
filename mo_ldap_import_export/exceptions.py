# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from fastapi import HTTPException


class MultipleObjectsReturnedException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=409, detail=message)


class NoObjectsReturnedException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class AttributeNotFound(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class IncorrectMapping(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=500, detail=message)


class NotSupportedException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=501, detail=message)


class ReadOnlyException(HTTPException):
    """Raised when the integration would write if not in read-only mode."""

    def __init__(self, message):
        super().__init__(status_code=501, detail=message)


class InvalidNameException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=422, detail=message)


class UUIDNotFoundException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class TimeOutException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=408, detail=message)


class IgnoreChanges(HTTPException):
    """Exception raised if the import/export checks reject a message."""

    def __init__(self, message):
        super().__init__(status_code=400, detail=message)


class InvalidChangeDict(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=422, detail=message)


class InvalidCPR(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=422, detail=message)


class DNNotFound(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)
