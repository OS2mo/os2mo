#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from pydantic import Field
from pydantic import ValidationError

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestRABase:
    def test_init(self):
        # RABase should not be able to be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            RABase()


class TestConfig:
    class ConfigClass(RABase):
        test_field: str = Field(alias="Field alias")

    def test_frozen(self):
        config_class = self.ConfigClass(test_field="test")

        # config_class should be immutable
        with pytest.raises(TypeError, match="immutable"):
            config_class.test_field = "new test"

        # and have a __hash__() method
        assert hasattr(config_class, "__hash__")

    def test_allow_population_by_field_name(self):
        # We should be able to populate using Field alias
        assert self.ConfigClass(**{"Field alias": "test"})

    def test_extra_forbid(self):
        # This is verboten
        with pytest.raises(ValidationError, match="extra fields not permitted"):
            self.ConfigClass(test_field="test", fail="oh no")
