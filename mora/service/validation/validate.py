# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from fastapi import Body

from ... import exceptions
from ... import lora
from ... import mapping
from ... import util
from .. import facet
from ..address_handler import base
from . import validator

_router = APIRouter()


# important to include AFTER path_operations are in place
router = APIRouter()
router.include_router(_router, prefix="/validate")
