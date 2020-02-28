# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from logging.handlers import RotatingFileHandler

from . import settings


def init():
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

    file_log_handler = RotatingFileHandler(
        filename=settings.config["log"]["log_path"] or settings.config["log"][
            "trace_log_path"],
        maxBytes=1000000,
    )
    file_log_handler.setFormatter(log_format)
    file_log_handler.setLevel(log_level)
    logger.addHandler(file_log_handler)
