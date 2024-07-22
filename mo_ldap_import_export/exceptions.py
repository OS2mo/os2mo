# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from functools import wraps

import structlog
from fastapi import HTTPException
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage
from gql.transport.exceptions import TransportQueryError

logger = structlog.stdlib.get_logger()


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
    """Raised when the integration is improperly configured."""

    def __init__(self, message):
        super().__init__(status_code=500, detail=message)


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


def reject_on_failure(func):
    """
    Decorator to turn message into dead letter in case of exceptions.
    """

    @wraps(func)
    async def modified_func(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except RejectMessage as e:  # In case we explicitly reject the message: Abort
            logger.info(e)
            raise
        except (
            RequeueMessage
        ) as e:  # In case we explicitly requeued the message: Requeue
            logger.warning(e)
            raise
        except (
            # Misconfiguration
            # This is raised when the integration is improperly configured
            IncorrectMapping,
            # Temporary downtime
            # This is raised when a GraphQL query is invalid or has temporary downtime
            TransportQueryError,
            NoObjectsReturnedException,  # In case an object is deleted halfway: Abort
        ) as e:
            logger.warning(e)
            raise RequeueMessage() from e
        except (
            # This is raised if the import/export checks reject a message
            IgnoreChanges,
            ReadOnlyException,  # In case a feature is not enabled: Abort
        ) as e:
            logger.info(e)
            raise RejectMessage() from e

    modified_func.__wrapped__ = func  # type: ignore
    return modified_func
