# -*- coding: utf-8 -*-
import structlog

from .processors import mask_cpr

logger = structlog.wrap_logger(structlog.get_logger(), processors=[mask_cpr])
