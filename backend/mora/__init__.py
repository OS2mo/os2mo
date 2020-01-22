# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

__version__ = "1.4.0"

import logging
from logging.handlers import RotatingFileHandler

from . import settings


logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("pika").setLevel(logging.INFO)

log_level = settings.config["log"]["log_level"]
logger = logging.getLogger()

logger.setLevel(log_level)
logger.setLevel(min(logger.getEffectiveLevel(), logging.INFO))

log_format = logging.Formatter(
    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
)

stdout_log_handler = logging.StreamHandler()
stdout_log_handler.setFormatter(log_format)
stdout_log_handler.setLevel(log_level)  # this can be higher
logger.addHandler(stdout_log_handler)

# The trace log contains debug statements (in context with everything
# higher precedens!) and is intended to be read by humans (tm) when
# something goes wrong. Please *do* write tracebacks and perhaps even
# pprint.pformat these messages.
file_log_handler = RotatingFileHandler(
    filename=settings.config["log"]["log_path"],
    maxBytes=1000000,
)
file_log_handler.setFormatter(log_format)
file_log_handler.setLevel(log_level)
logger.addHandler(file_log_handler)

# The activity log is for everything that isn't debug information. Only
# write single lines and no exception tracebacks here as it is harder to
# parse.
activity_log_handler = RotatingFileHandler(
    filename=settings.config["log"]["activity_log_path"],
    maxBytes=1000000,
)
activity_log_handler.setFormatter(log_format)
activity_log_handler.setLevel(logging.INFO)
logger.addHandler(activity_log_handler)
