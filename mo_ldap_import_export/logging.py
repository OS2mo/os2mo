# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import structlog

from .processors import mask_cpr

logger = structlog.wrap_logger(structlog.get_logger(), processors=[mask_cpr])
