#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
__version__ = "1.4.0"

import os

import logging
from logging.handlers import RotatingFileHandler

from . import settings


logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("pika").setLevel(logging.INFO)

log_format = logging.Formatter(
    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
)


stdout_log_handler = logging.StreamHandler()
stdout_log_handler.setFormatter(log_format)
stdout_log_handler.setLevel(logging.DEBUG)  # this can be higher
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(stdout_log_handler)


if os.getenv("FLASK_ENV", False) == "production":
    # The activity log is for everything that isn't debug information. Only
    # write single lines and no exception tracebacks here as it is harder to
    # parse.
    activity_log_handler = RotatingFileHandler(
        filename=settings.config["log"]["activity_log_path"],
        maxBytes=1000000,
    )
    activity_log_handler.setFormatter(log_format)
    activity_log_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(activity_log_handler)

    # The trace log contains debug statements (in context with everything
    # higher precedens!) and is intended to be read by humans (tm) when
    # something goes wrong. Please *do* write tracebacks and perhaps even
    # pprint.pformat these messages.
    trace_log_handler = RotatingFileHandler(
        filename=settings.config["log"]["trace_log_path"],
        maxBytes=1000000,
    )
    trace_log_handler.setFormatter(log_format)
    trace_log_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(trace_log_handler)
