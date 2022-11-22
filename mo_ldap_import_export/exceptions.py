# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from fastapi import HTTPException


class MultipleObjectsReturnedException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class NoObjectsReturnedException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class CprNoNotFound(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


class IncorrectMapping(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)
