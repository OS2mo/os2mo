# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging

import structlog
from structlog.types import EventDict
from structlog.types import Processor

from .processors import mask_cpr


def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """Remove `color_message` from uvicorn logs.

    Uvicorn logs the message a second time in the extra `color_message`, but we
    don't need it.
    """

    event_dict.pop("color_message", None)
    return event_dict


def init(log_level: str, production_mode: bool = True):
    # Heavily inspired by OS2mo

    # NOTE: We intentionally do not log timestamps, as we rely on the container runtime
    #       to add timestamps to our logs. With docker simply add `-t` to logs.

    shared_processors: list[Processor] = [
        # Merge asyncio bound logging variables
        structlog.contextvars.merge_contextvars,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Add extra attributes to the event dictionary
        structlog.stdlib.ExtraAdder(),
        _drop_color_message_key,
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        structlog.processors.format_exc_info,
        # If some value is in bytes, decode it to a Unicode str.
        structlog.processors.UnicodeDecoder(),
        # Mask CPR numbers in logging output
        mask_cpr,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.stdlib.BoundLogger,
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Effectively freeze configuration after creating the first bound
        # logger.
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    if not production_mode:  # pragma: no cover
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

    for _log in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        # Clear the log handlers for uvicorn loggers, and enable propagation so
        # the messages are caught by our root logger and formatted correctly by
        # structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True
