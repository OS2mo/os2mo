# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
from typing import TypeVar
from urllib.parse import urlencode

import freezegun
import pytest
from fastapi import Request

from oio_rest import oio_base
from oio_rest.custom_exceptions import BadRequestException
from oio_rest.db import db_helpers
from oio_rest.oio_base import OIORestObject
from tests.oio_rest.util import ExtTestCase

CallableReturnType = TypeVar("CallableReturnType")


class TestClassRestObject(OIORestObject):
    pass


class TestOIORestObject(ExtTestCase):
    db_struct = {
        "testclassrestobject": {
            "attributter": {"egenskaber": ["attribut"]},
            "tilstande": {"tilstand": ["tilstand1", "tilstand2"]},
            "relationer_nul_til_en": ["relation_en"],
            "relationer_nul_til_mange": ["relation_mange"],
        }
    }

    @pytest.fixture(autouse=True)
    def setup_helpers(self):
        self.testclass = TestClassRestObject()
        db_helpers._attribute_fields = {}
        db_helpers._attribute_names = {}
        db_helpers._relation_names = {}

    def create_request(self, method=None, params=None, headers=None, data=None):
        params = params or {}
        method = method or "GET"
        data = data or ""
        headers = headers or []

        responses = [
            {
                "type": "http.request",
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": "/",
                "query_string": urlencode(params, True),
                "root_path": "",
                "headers": headers,
                "body": data.encode("utf-8"),
                "client": ("127.0.0.1", 1),
                "server": ("127.0.0.1", 2),
            }
        ]

        async def receive():
            if responses:
                return responses.pop(0)
            return None

        request = Request(
            {
                "type": "http",
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": "/",
                "query_string": urlencode(params, True),
                "headers": headers,
                "client": ("127.0.0.1", 1),
                "server": ("127.0.0.1", 2),
            },
            receive,
        )
        return request

    def test_gather_registration(self):
        # Arrange
        attrs = {"attribut": [{"whatever": "123"}]}
        states = {"tilstand": [{"whatever": "123"}]}
        rels = {"relation": [{"whatever": "123"}]}

        input = {"attributter": attrs, "tilstande": states, "relationer": rels}

        expected = {"attributes": attrs, "states": states, "relations": rels}

        # Act
        actual = self.testclass.gather_registration(input)

        # Assert
        assert expected == actual

    def test_gather_registration_empty_input(self):
        # Arrange
        input = {}

        expected = {"attributes": {}, "states": {}, "relations": {}}

        # Act
        actual = self.testclass.gather_registration(input)

        # Assert
        assert expected == actual

    def test_gather_registration_empty_lists(self):
        # Arrange
        input = {"attributter": {}, "tilstande": {}, "relationer": {}}

        expected = {"attributes": {}, "states": {}, "relations": {}}

        # Act
        actual = self.testclass.gather_registration(input)

        # Assert
        assert expected == actual

    def test_gather_registration_raises_on_bad_attributter_input(self):
        # Arrange
        input = {
            "attributter": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)

    def test_gather_registration_raises_on_bad_tilstande_input(self):
        # Arrange
        input = {
            "tilstande": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)

    def test_gather_registration_raises_on_bad_relationer_input(self):
        # Arrange
        input = {
            "relationer": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)


class TestOIORest:
    def test_typed_get_returns_value(self):
        # Arrange
        expected_result = "value"
        testkey = "testkey"
        d = {testkey: expected_result}

        # Act
        actual_result = oio_base.typed_get(d, testkey, "default")

        # Assert
        assert expected_result == actual_result

    def test_typed_get_returns_default_if_value_none(self):
        # Arrange
        expected_result = "default"
        testkey = "testkey"
        d = {testkey: None}

        # Act
        actual_result = oio_base.typed_get(d, testkey, expected_result)

        # Assert
        assert expected_result == actual_result

    def test_typed_get_raises_on_wrong_type(self):
        # Arrange
        default = 1234

        testkey = "testkey"
        d = {testkey: "value"}

        # Act & Assert
        with pytest.raises(BadRequestException):
            oio_base.typed_get(d, testkey, default)

    def test_get_virkning_dates_virkningstid(self):
        # Arrange
        args = {
            "virkningstid": "2020-01-01",
        }

        expected_from = datetime.datetime(2020, 1, 1)
        expected_to = expected_from + datetime.timedelta(microseconds=1)

        # Act
        actual_from, actual_to = oio_base.get_virkning_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_virkning_dates_from_to(self):
        # Arrange
        args = {
            "virkningfra": "2006-01-01",
            "virkningtil": "2020-01-01",
        }

        expected_from = "2006-01-01"
        expected_to = "2020-01-01"

        # Act
        actual_from, actual_to = oio_base.get_virkning_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_get_virkning_dates_defaults(self):
        # Arrange
        args = {}

        expected_from = datetime.datetime(2017, 1, 1, 1)
        expected_to = expected_from + datetime.timedelta(microseconds=1)

        # Act
        actual_from, actual_to = oio_base.get_virkning_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_virkning_dates_raises_on_invalid_args_combination(self):
        # Arrange
        args = {
            "virkningstid": "2020-01-01",
            "virkningfra": "2006-01-01",
            "virkningtil": "2020-01-01",
        }

        # Act
        with pytest.raises(BadRequestException):
            oio_base.get_virkning_dates(args)

    def test_get_registreret_dates_registreringstid(self):
        # Arrange
        args = {
            "registreringstid": "2020-01-01",
        }

        expected_from = datetime.datetime(2020, 1, 1)
        expected_to = expected_from + datetime.timedelta(microseconds=1)

        # Act
        actual_from, actual_to = oio_base.get_registreret_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_registreret_dates_from_to(self):
        # Arrange
        args = {
            "registreretfra": "2006-01-01",
            "registrerettil": "2020-01-01",
        }

        expected_from = "2006-01-01"
        expected_to = "2020-01-01"

        # Act
        actual_from, actual_to = oio_base.get_registreret_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_get_registreret_dates_defaults(self):
        # Arrange
        args = {}

        expected_from = None
        expected_to = None

        # Act
        actual_from, actual_to = oio_base.get_registreret_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_registreret_dates_raises_on_invalid_args_combination(self):
        # Arrange
        args = {
            "registreringstid": "2020-01-01",
            "registreretfra": "2006-01-01",
            "registrerettil": "2020-01-01",
        }

        # Act
        with pytest.raises(BadRequestException):
            oio_base.get_registreret_dates(args)
