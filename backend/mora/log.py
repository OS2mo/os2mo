# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.types import EventDict
from structlog.types import Processor
from uvicorn.protocols.utils import get_path_with_query_string


def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """Remove `color_message` from uvicorn logs.

    Uvicorn logs the message a second time in the extra `color_message`, but we
    don't need it.
    """

    event_dict.pop("color_message", None)
    return event_dict


class AccesslogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        self.app = app
        self.access_logger = structlog.stdlib.get_logger("api.access")
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter_ns()

        response = await call_next(request)

        process_time = round((time.perf_counter_ns() - start_time) / 10**9, 3)

        status_code = response.status_code
        path = get_path_with_query_string(request.scope)
        client_host = request.client.host
        client_port = request.client.port
        http_method = request.method

        self.access_logger.info(
            "Request",
            path=path,
            status_code=status_code,
            method=http_method,
            network={"client": {"ip": client_host, "port": client_port}},
            duration=process_time,
        )

        return response


def init(log_level: str, json: bool = True):
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
    else:
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
    root_logger.addHandler(handler)
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
