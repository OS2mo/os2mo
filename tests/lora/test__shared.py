#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime
from typing import List
from typing import Union
from uuid import uuid4

import pytest
from pydantic import BaseModel
from pydantic import ValidationError

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
    fail_int = 1
    fail_str = "fail"
    accept_dt: List[Union[str, datetime]] = [
        "infinity",
        "-infinity",
        "2011-06-26",
        datetime(2060, 12, 15),
    ]

    def test_init(self):
        # Unfortunately, this currently works just fine :(
        assert InfiniteDatetime(self.fail_int)
        assert InfiniteDatetime(self.fail_str)

    def test_from_value(self):
        # This should always work
        for dt in self.accept_dt:
            assert InfiniteDatetime.from_value(dt)

        # but this shouldn't
        with pytest.raises(TypeError, match="string or datetime required"):
            InfiniteDatetime.from_value(self.fail_int)  # type: ignore

        # and this string cannot be parsed
        with pytest.raises(
            ValueError,
            match=f"Unable to parse '{self.fail_str}' as an ISO-8601 datetime string",
        ):
            InfiniteDatetime.from_value(self.fail_str)

    def test_in_model(self):
        class DTModel(BaseModel):
            dt: InfiniteDatetime

        # Same values should work
        for dt in self.accept_dt:
            assert DTModel(dt=dt)

        # But fail values should raise validation errors
        with pytest.raises(ValidationError):
            for err_dt in [self.fail_int, self.fail_str]:
                DTModel(dt=err_dt)

    def test_infinity_ordering(self):
        pos_inf_dt = InfiniteDatetime("infinity")
        neg_inf_dt = InfiniteDatetime("-infinity")
        assert neg_inf_dt < pos_inf_dt
        assert (neg_inf_dt < neg_inf_dt) is False
        assert (pos_inf_dt < pos_inf_dt) is False
