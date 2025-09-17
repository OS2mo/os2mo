# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from uuid import uuid4

import structlog
from fastapi import Request
from fastapi import Response
from starlette_context import context
from starlette_context import request_cycle_context
from structlog.contextvars import bound_contextvars
from structlog.types import EventDict
from structlog.types import Processor
from uvicorn.protocols.utils import get_path_with_query_string

from mora.config import get_settings

logger = structlog.get_logger()


def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """Remove `color_message` from uvicorn logs.

    Uvicorn logs the message a second time in the extra `color_message`, but we
    don't need it.
    """

    event_dict.pop("color_message", None)
    return event_dict


def gen_accesslog_middleware() -> Callable[[Request, Any], Awaitable[Response]]:
    access_logger = structlog.stdlib.get_logger("api.access")

    async def accesslog_middleware(request: Request, call_next) -> Response:
        with bound_contextvars(request_id=str(uuid4())):
            response = await call_next(request)

        status_code = response.status_code
        path = get_path_with_query_string(request.scope)
        client_host = request.client.host
        client_port = request.client.port
        http_method = request.method

        if status_code >= 400:
            access_logger.warning(
                "Access log",
                path=path,
                status_code=status_code,
                method=http_method,
                network={"client": {"ip": client_host, "port": client_port}},
            )

        return response

    return accesslog_middleware


def init(log_level: str, json: bool = True) -> None:
    # Heavily inspired by https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        _drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json:
        # Format the exception only for JSON logs, as we want to pretty-print
        # them when using the ConsoleRenderer.
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if json:
        log_renderer = structlog.processors.JSONRenderer()
    else:  # pragma: no cover
        log_renderer = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level.upper())

    for _log in ("uvicorn", "uvicorn.error"):
        # Clear the log handlers for uvicorn loggers, and enable propagation so
        # the messages are caught by our root logger and formatted correctly by
        # structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    # Since we re-create the access logs ourselves in AccesslogMiddleware, to
    # add all information in the structured log, we clear the handlers and
    # prevent the logs to propagate to a logger higher up in the hierarchy
    # (effectively rendering them silent).
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False


_CANONICAL_LOG_KEY = "canonical"
_CANONICAL_GQL_KEY = "gql"


async def canonical_log_dependency():
    data = {**context, _CANONICAL_LOG_KEY: {}}
    with request_cycle_context(data):
        yield
        logger_function = (
            logger.warning
            if data[_CANONICAL_LOG_KEY].get("gql", {}).get("errors")
            else logger.info
        )
        logger_function("Canonical log line", **data[_CANONICAL_LOG_KEY])


def canonical_log_context() -> dict:
    if get_settings().is_under_test() and _CANONICAL_LOG_KEY not in context:
        return {}
    return context[_CANONICAL_LOG_KEY]


def canonical_gql_context() -> dict:
    log_context = canonical_log_context()
    return log_context.setdefault(_CANONICAL_GQL_KEY, {})
