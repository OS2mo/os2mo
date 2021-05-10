#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
# from datetime import datetime
from uuid import uuid4

import pytest

from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora._shared import LoraBase

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestLoraBase:
    def test_init(self):
        # LoraBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            LoraBase()

    def test_fields(self):
        # Subclasses of LoraBase should have a UUID field
        class LoraSub(LoraBase):
            pass

        assert LoraSub.__fields__.get("uuid")

    def test_validators(self):
        class LoraSub(LoraBase):
            pass

        # UUIDs should be auto-generated
        lora_sub = LoraSub()
        assert lora_sub.uuid.version == 4

        # But we should also be able to set them explicitly
        test_uuid = uuid4()
        lora_sub_with_uuid = LoraSub(uuid=test_uuid)
        assert lora_sub_with_uuid.uuid == test_uuid


class TestInfiniteDatetime:
    def test_init(self):
        print(InfiniteDatetime(inf_dt=None))
        assert False
