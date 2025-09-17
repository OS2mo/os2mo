# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import ParamSpec
from typing import TypeVar

import structlog
from fastapi import HTTPException
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage
from gql.transport.exceptions import TransportQueryError

from mo_ldap_import_export.types import DN

logger = structlog.stdlib.get_logger()


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
            status_code=451,
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


class TimeOutException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=408, detail=message)


class IgnoreChanges(HTTPException):
    """Exception raised if the import/export checks reject a message."""

    def __init__(self, message: str) -> None:
        super().__init__(status_code=451, detail=message)


class InvalidCPR(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=422, detail=message)


class DryRunException(HTTPException):
    def __init__(self, message: str, dn: DN, details: dict[str, Any]) -> None:
        assert "dn" not in details
        assert "message" not in details
        super().__init__(
            status_code=451, detail={"message": message, "dn": dn, **details}
        )


class SkipObject(Exception):
    """Exception raised if the ldap_to_mo object should be skipped."""


Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def amqp_reject_on_failure(
    func: Callable[Params, Awaitable[ReturnType]],
) -> Callable[Params, Awaitable[ReturnType]]:
    """Decorator to convert the above exceptions into RAMQP exceptions.

    Args:
        func: The function to decorate.

    Returns:
        The decorated function, converting exceptions into RAMQP exceptions.
    """

    @wraps(func)
    async def modified_func(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
        try:
            return await func(*args, **kwargs)
        except RejectMessage as e:  # pragma: no cover
            # In case we explicitly reject the message: Abort
            logger.info(str(e))
            raise
        except RequeueMessage as e:
            # In case we explicitly requeued the message: Requeue
            logger.info(str(e))
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
            logger.exception("Exception during AMQP processing")
            raise RequeueMessage() from e
        except (
            # This is raised if the import/export checks reject a message
            IgnoreChanges,
            ReadOnlyException,  # In case a feature is not enabled: Abort
            InvalidCPR,  # We cannot lookup or sync users with invalid CPR numbers
        ) as e:
            logger.info(str(e))
            raise RejectMessage() from e
        except Exception as e:
            # This converts all unknown exceptions to RequeueMessage exceptions,
            # as we wish to catch these to requeue the message to the back of the queue,
            # instead of letting FastRAMQPI requeue it, which would be to the front of
            # the queue, effectively blocking the integration from processing any
            # messages until the troublesome message has been resolved.
            # This is very much a hack to workaround shortcomings in RabbitMQ.
            # In theory a workaround could have been made in FastRAMQPI, but we have
            # decided against doing the workaround there as we would rather just replace
            # AMQP with HTTP triggers instead of building workarounds atop workarounds.
            logger.exception("Exception during AMQP processing")
            raise RequeueMessage() from e

    # TODO: Why is this necessary?
    modified_func.__wrapped__ = func  # type: ignore
    return modified_func


def http_reject_on_failure(
    func: Callable[Params, Awaitable[ReturnType]],
) -> Callable[Params, Awaitable[ReturnType]]:
    """Decorator to convert the exceptions into HTTP exceptions.

    Args:
        func: The function to decorate.

    Returns:
        The decorated function, converting exceptions into HTTP exceptions.
    """

    @wraps(func)
    async def modified_func(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
        try:
            return await func(*args, **kwargs)
        except RejectMessage as e:
            # In case we explicitly reject the message: Abort
            logger.info(str(e))
            raise HTTPException(status_code=451, detail=str(e)) from e
        except RequeueMessage as e:
            # In case we explicitly requeued the message: Requeue
            logger.info(str(e))
            raise HTTPException(status_code=409, detail=str(e)) from e
        except TransportQueryError as e:
            # Temporary downtime
            # This is raised when a GraphQL query is invalid or has temporary downtime
            logger.exception("Exception during HTTP processing")
            raise HTTPException(status_code=500, detail=str(e)) from e
        except HTTPException:
            logger.exception("Exception during HTTP processing")
            raise
        except Exception as e:
            logger.exception("Exception during HTTP processing")
            raise HTTPException(status_code=500, detail=str(e)) from e

    # TODO: Why is this necessary?
    modified_func.__wrapped__ = func  # type: ignore
    return modified_func
