# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import json
import types
from typing import TypeVar
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from urllib.parse import urlencode

import freezegun
import pytest
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from oio_rest import db
from oio_rest import oio_base
from oio_rest import organisation
from oio_rest.custom_exceptions import BadRequestException
from oio_rest.custom_exceptions import GoneException
from oio_rest.custom_exceptions import NotFoundException
from oio_rest.db import db_helpers
from oio_rest.oio_base import ConfiguredDBInterface
from oio_rest.oio_base import OIORestObject
from oio_rest.oio_base import OIOStandardHierarchy
from oio_rest.oio_base import _get_args_from_request
from oio_rest.oio_base import _get_json_from_request
from oio_rest.oio_base import _process_args

from tests.oio_rest.util import ExtTestCase

CallableReturnType = TypeVar("CallableReturnType")


async def get_args(request: Request, as_lists=False):
    return _process_args(await _get_args_from_request(request), as_lists)


class TestClassRestObject(OIORestObject):
    pass


class TestClassStandardHierarchy(OIOStandardHierarchy):
    _name = "TestClass"
    _classes = []


class TestOIORestObjectCreateApi:
    @pytest.fixture(autouse=True)
    def setup_testclass(self) -> None:
        self.testclass = TestClassRestObject

    def assert_api_rule(self, router: APIRouter, name: str, method: str, function) -> None:
        # Check for existence of rule in args list
        endpoints = router.routes
        endpoints = filter(lambda route: method in route.methods, endpoints)
        endpoints = filter(lambda route: function == route.endpoint, endpoints)
        endpoints = filter(lambda route: name == route.name, endpoints)

        rule = next(endpoints, None)
        assert rule is not None, f"Expected {method} {name}"

    def test_create_api_call_returns_router(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)

    def test_create_api_has_get_objects_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_get_objects",
            "GET",
            self.testclass.get_objects,
        )

    def test_create_api_adds_get_object_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_get_object",
            "GET",
            self.testclass.get_object,
        )

    def test_create_api_adds_put_object_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_put_object",
            "PUT",
            self.testclass.put_object,
        )

    def test_create_api_adds_patch_object_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_patch_object",
            "PATCH",
            self.testclass.patch_object,
        )

    def test_create_api_adds_create_object_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_create_object",
            "POST",
            self.testclass.create_object,
        )

    def test_create_api_adds_delete_object_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_delete_object",
            "DELETE",
            self.testclass.delete_object,
        )

    def test_create_api_adds_fields_rule(self) -> None:
        router = self.testclass.create_api(hierarchy="Hierarchy")
        assert isinstance(router, APIRouter)
        self.assert_api_rule(
            router,
            "TestClassRestObject_fields",
            "GET",
            self.testclass.get_fields,
        )


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
    def setup_helpers(self) -> None:
        self.testclass = TestClassRestObject()
        db_helpers._search_params = {}
        db_helpers._attribute_fields = {}
        db_helpers._attribute_names = {}
        db_helpers._relation_names = {}
        db_helpers._state_names = {}

    def create_request(self, method=None, params=None, headers=None, data=None) -> Request:
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

    async def test_get_args_lowercases_arg_keys(self):
        # Arrange
        params = {"KEY1": "Value1", "Key2": "VALUE2"}

        expected_result = {
            "key1": "Value1",
            "key2": "VALUE2",
        }

        # Act
        request = self.create_request(method="POST", params=params)
        actual_result = await get_args(request)

        # Assert
        assert expected_result == actual_result

    async def test_get_args_returns_dict_as_default(self):
        # Arrange
        params = {"key1": "value1", "key2": ["value2", "value3"]}

        expected_result = {"key1": "value1", "key2": "value2"}

        # Act
        request = self.create_request(method="POST", params=params)
        actual_result = await get_args(request)

        # Assert
        assert expected_result == actual_result

    async def test_get_args_returns_as_lists(self):
        # Arrange
        params = {"key1": "value1", "key2": ["value2", "value3"]}

        expected_result = {"key1": ["value1"], "key2": ["value2", "value3"]}

        # Act
        request = self.create_request(method="POST", params=params)
        actual_result = await get_args(request, as_lists=True)

        # Assert
        assert expected_result == actual_result

    async def test_get_args_from_json_lowercases_arg_keys(self):
        # Arrange
        params = {"KEY1": "Value1", "Key2": "VALUE2"}

        expected_result = {
            "key1": "Value1",
            "key2": "VALUE2",
        }

        # Act
        request = self.create_request(
            method="GET",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(params),
        )
        actual_result = await get_args(request)

        # Assert
        assert expected_result == actual_result

    async def test_get_args_from_json_returns_dict_as_default(self):
        # Arrange
        params = {"key1": "value1", "key2": ["value2", "value3"]}

        expected_result = {"key1": "value1", "key2": "value2"}

        # Act
        request = self.create_request(
            method="GET",
            headers=[
                ("Content-Type", "application/json"),
            ],
            data=json.dumps(params),
        )
        actual_result = await get_args(request)

        # Assert
        assert expected_result == actual_result

    async def test_get_args_from_json_returns_as_lists(self):
        # Arrange
        params = {"key1": "value1", "key2": ["value2", "value3"]}

        expected_result = {"key1": ["value1"], "key2": ["value2", "value3"]}

        # Act
        request = self.create_request(
            method="GET",
            headers=[
                ("Content-Type", "application/json"),
            ],
            data=json.dumps(params),
        )
        actual_result = await get_args(request, as_lists=True)

        # Assert
        assert expected_result == actual_result

    async def test_get_json_returns_json_if_request_json(self):
        # Arrange
        expected_json = {"testkey": "testvalue"}

        # Act
        request = self.create_request(
            method="POST",
            headers=[["accept", "application/json"]],
            data=json.dumps(expected_json),
        )
        actual_json = await _get_json_from_request(request)

        # Assert
        assert expected_json == actual_json

    async def test_get_json_returns_json_if_form_json(self):
        # Arrange
        expected_json = {"testkey": "testvalue"}

        request = self.create_request(
            method="POST",
            headers=[[b"content-type", b"application/x-www-form-urlencoded"]],
            data=urlencode({"json": json.dumps(expected_json)}),
        )
        actual_json = await _get_json_from_request(request)

        # Assert
        assert expected_json == actual_json

    async def test_get_json_returns_badrequest_if_malformed_form_json(self):
        # Arrange
        # Act
        request = self.create_request(
            method="POST",
            headers=[[b"content-type", b"application/x-www-form-urlencoded"]],
            data=urlencode({"json": "{123123123}"}),
        )

        with pytest.raises(HTTPException):
            await _get_json_from_request(request)

    async def test_get_json_returns_none_if_request_json_is_none(self):
        # Arrange
        expected_json = None

        request = self.create_request(
            method="POST",
            data=json.dumps(expected_json),
        )
        actual_json = await _get_json_from_request(request)

        # Assert
        assert expected_json == actual_json

    @patch("oio_rest.db.create_or_import_object")
    async def test_create_object_with_input_returns_uuid_and_code_201(self, mock):
        # Arrange
        uuid = "c98d1e8b-0655-40a0-8e86-bb0cc07b0d59"

        expected_data = {"uuid": uuid}

        mock.return_value = uuid

        data = {
            "note": "NOTE",
            "attributter": {
                "organisationegenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "organisationsnavn": "name",
                        "virkning": {"from": "2017-01-01 12:00:00", "to": "infinity"},
                    }
                ]
            },
            "tilstande": {
                "organisationgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {"from": "2017-01-01 12:00:00", "to": "infinity"},
                    }
                ]
            },
        }

        # Act
        request = self.create_request(
            method="POST",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await organisation.Organisation.create_object(request)

        # Assert
        assert expected_data == actual_data

    async def test_create_object_with_no_input_returns_uuid_none_and_code_400(self):
        # Arrange
        expected_data = {"uuid": None}

        # Act
        request = self.create_request(
            method="POST",
        )
        with pytest.raises(HTTPException) as exp:
            await self.testclass.create_object(request)
            # Assert
            assert exp.detail == expected_data
            assert exp.status_code == 400

    async def test_create_object_raises_on_unknown_args(self):
        # Arrange
        params = {"a": "b"}

        # Act
        request = self.create_request(
            method="POST",
            params=params,
        )
        with pytest.raises(BadRequestException):
            await self.testclass.create_object(request)

    async def test_get_fields(self):
        # Arrange
        expected_fields = ["field1", "field2"]
        db_structure = {"testclassrestobject": expected_fields, "garbage": ["garbage"]}

        request = self.create_request()
        async with self.patch_db_struct(db_structure):
            # Act
            actual_fields = await self.testclass.get_fields(request)

            # Assert
            assert expected_fields == actual_fields

    async def test_get_fields_raises_on_unknown_args(self):
        # Arrange
        params = {"a": "b"}

        # Act
        request = self.create_request(params=params)
        with pytest.raises(BadRequestException):
            await self.testclass.get_fields(request)

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    @patch("oio_rest.db.list_objects")
    @ExtTestCase.patch_db_struct(db_struct)
    async def test_get_objects_list_uses_default_params(self, mock_list):
        # Arrange
        data = ["1", "2", "3"]

        mock_list.return_value = data

        virkning_fra = datetime.datetime.now()
        virkning_to = datetime.datetime.now() + datetime.timedelta(microseconds=1)

        expected_args = (
            "TestClassRestObject",
            None,
            virkning_fra,
            virkning_to,
            None,
            None,
        )

        expected_result = {"results": data}

        # Act
        request = self.create_request()
        actual_result = await self.testclass.get_objects(request)

        # Assert
        actual_args = mock_list.call_args[0]

        assert expected_args == actual_args
        assert expected_result == actual_result

    @patch("oio_rest.db.list_objects")
    @ExtTestCase.patch_db_struct(db_struct)
    async def test_get_objects_list_uses_supplied_params(self, mock):
        # Arrange
        data = ["1", "2", "3"]

        mock.return_value = data

        uuids = [
            "942f2aae-6151-4894-ac47-842ab93b161b",
            "18ac08a3-8158-4b68-81aa-adacb1ea0fb3",
        ]
        virkning_fra = "virkning_fra"
        virkning_til = "virkning_til"
        registreret_fra = "registreret_fra"
        registreret_til = "registreret_til"

        expected_args = (
            "TestClassRestObject",
            uuids,
            virkning_fra,
            virkning_til,
            registreret_fra,
            registreret_til,
        )

        expected_result = {"results": data}

        request_params = {
            "uuid": uuids,
            "virkningfra": virkning_fra,
            "virkningtil": virkning_til,
            "registreretfra": registreret_fra,
            "registrerettil": registreret_til,
        }

        # Act
        request = self.create_request(params=request_params)
        actual_result = await self.testclass.get_objects(request)

        # Assert
        actual_args = mock.call_args[0]

        assert expected_args == actual_args
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(db_struct)
    async def test_get_objects_multiple_of_same_relation(self):
        # Arrange
        mock_searcher = MagicMock(search_objects=AsyncMock(return_value=None))
        relation_en_uuids = [
            "942f2aae-6151-4894-ac47-842ab93b161b",
            "18ac08a3-8158-4b68-81aa-adacb1ea0fb3",
        ]
        relation_mange_uuids = [
            "17980c1f-1bf4-4568-aa6e-d176728029dd",
            "9dac59d0-b3c8-44a1-8a13-3dad322f9517",
            "b13163d7-e333-43ab-b3c9-5df2d478db14",
        ]
        request_params = {
            "relation_en": relation_en_uuids,
            "relation_mange": relation_mange_uuids,
            "virkningfra": "virkning_fra",
            "virkningtil": "virkning_til",
            "registreretfra": "registreret_fra",
            "registrerettil": "registreret_til",
        }

        # Act
        request = self.create_request(params=request_params)
        with patch.object(ConfiguredDBInterface, "searcher", mock_searcher):
            await self.testclass.get_objects(request)

        # Assert
        relations = mock_searcher.search_objects.call_args.kwargs["registration"][
            "relations"
        ]
        assert relation_en_uuids == [r["uuid"] for r in relations["relation_en"]]
        assert relation_mange_uuids == [r["uuid"] for r in relations["relation_mange"]]

    @patch("oio_rest.db.list_objects")
    @ExtTestCase.patch_db_struct(db_struct)
    async def test_get_objects_returns_empty_list_on_no_results(self, mock):
        # Arrange

        mock.return_value = None

        # Act
        request = self.create_request()
        actual_result = await self.testclass.get_objects(request)

        expected_result = {"results": []}

        assert expected_result == actual_result

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.oio_base.build_registration")
    async def test_get_objects_search_uses_default_params(self, mock_br):
        # Arrange
        data = ["1", "2", "3"]
        mock_searcher = MagicMock(search_objects=AsyncMock(return_value=data))

        mock_br.return_value = "REGISTRATION"

        virkning_fra = datetime.datetime.now()
        virkning_to = datetime.datetime.now() + datetime.timedelta(microseconds=1)

        expected_args = dict(
            class_name="TestClassRestObject",
            uuid=None,
            registration="REGISTRATION",
            virkning_fra=virkning_fra,
            virkning_til=virkning_to,
            registreret_fra=None,
            registreret_til=None,
            life_cycle_code=None,
            user_ref=None,
            note=None,
            any_attr_value_arr=None,
            any_rel_uuid_arr=None,
            first_result=None,
            max_results=None,
        )

        expected_result = {"results": data}

        request_params = {
            # Send a non list-arg argument to trigger search
            "attribut": "123",
        }

        # Act
        request = self.create_request(params=request_params)
        with patch.object(ConfiguredDBInterface, "searcher", mock_searcher):
            actual_result = await self.testclass.get_objects(request)

        # Assert
        actual_args = mock_searcher.search_objects.call_args.kwargs
        assert expected_args == actual_args
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.oio_base.build_registration")
    async def test_get_objects_search_uses_supplied_params(self, mock_br):
        # Arrange
        data = ["1", "2", "3"]
        mock_searcher = MagicMock(search_objects=AsyncMock(return_value=data))

        registration = "REGISTRATION"
        mock_br.return_value = registration

        uuid = "17b9a711-5fb4-43aa-8f8d-fe929d23ea68"
        virkning_fra = "virkning_fra"
        virkning_til = "virkning_til"
        registreret_fra = "registreret_fra"
        registreret_til = "registreret_til"
        livscykluskode = "livscykluskode"
        brugerref = "brugerref"
        notetekst = "notetekst"
        vilkaarligattr = ["vilkaarligattr"]
        vilkaarligrel = ["vilkaarligrel"]
        foersteresultat = 100
        maximalantalresultater = 100

        expected_args = dict(
            class_name="TestClassRestObject",
            uuid=uuid,
            registration=registration,
            virkning_fra=virkning_fra,
            virkning_til=virkning_til,
            registreret_fra=registreret_fra,
            registreret_til=registreret_til,
            life_cycle_code=livscykluskode,
            user_ref=brugerref,
            note=notetekst,
            any_attr_value_arr=vilkaarligattr,
            any_rel_uuid_arr=vilkaarligrel,
            first_result=foersteresultat,
            max_results=maximalantalresultater,
        )

        expected_result = {"results": data}

        request_params = {
            "uuid": uuid,
            "virkningfra": virkning_fra,
            "virkningtil": virkning_til,
            "registreretfra": registreret_fra,
            "registrerettil": registreret_til,
            "livscykluskode": livscykluskode,
            "brugerref": brugerref,
            "notetekst": notetekst,
            "vilkaarligattr": vilkaarligattr,
            "vilkaarligrel": vilkaarligrel,
            "foersteresultat": foersteresultat,
            "maximalantalresultater": maximalantalresultater,
        }

        # Act
        request = self.create_request(params=request_params)
        with patch.object(ConfiguredDBInterface, "searcher", mock_searcher):
            actual_result = await self.testclass.get_objects(request)

        # Assert
        actual_args = mock_searcher.search_objects.call_args.kwargs
        assert expected_args == actual_args
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.oio_base.build_registration")
    @patch("oio_rest.db.search_objects")
    async def test_get_objects_search_raises_exception_on_multi_uuid(
        self, mock_search, mock_br
    ):
        # Arrange
        data = ["1", "2", "3"]

        mock_search.return_value = data

        mock_br.return_value = {}

        uuids = [
            "94d42aaa-884d-42ba-8ced-964ee34b65c4",
            "23dd27c8-09dd-4da2-bfe4-b152f97dad59",
        ]

        request_params = {
            "uuid": uuids,
            "brugerref": "99809e77-ede6-48f2-b170-2366bdcd20e5",
        }

        # Act
        request = self.create_request(params=request_params)
        with pytest.raises(BadRequestException):
            await self.testclass.get_objects(request)

    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.db.search_objects")
    async def test_get_objects_search_raises_exception_on_unknown_args(
        self, mock_search
    ):
        # Arrange
        mock_search.return_value = {}

        request_params = {"a": "b"}

        # Act
        request = self.create_request(params=request_params)
        with pytest.raises(BadRequestException):
            await self.testclass.get_objects(request)

    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.db.list_objects")
    async def test_get_objects_filters_deleted_objects(self, mock_list):
        # Arrange
        uuid = "d5995ed0-d527-4841-9e33-112b22aaade1"
        data = [
            {
                "id": uuid,
                "registreringer": [{"livscykluskode": db.Livscyklus.SLETTET.value}],
            }
        ]
        request_params = {"uuid": "d5995ed0-d527-4841-9e33-112b22aaade1"}

        mock_list.return_value = [data]

        # Act
        request = self.create_request(params=request_params)
        results = await self.testclass.get_objects(request)
        assert results == {"results": []}

    @patch("oio_rest.db.list_objects")
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    async def test_get_object_uses_default_params(self, mock_list):
        # Arrange
        data = [{"registreringer": [{"livscykluskode": "whatever"}]}]
        uuid = "d5995ed0-d527-4841-9e33-112b22aaade1"

        mock_list.return_value = [data]

        virkning_fra = datetime.datetime.now()
        virkning_to = datetime.datetime.now() + datetime.timedelta(microseconds=1)

        expected_args = (
            "TestClassRestObject",
            [uuid],
            virkning_fra,
            virkning_to,
            None,
            None,
        )

        expected_result = {uuid: data}

        # Act
        request = self.create_request()
        actual_result = await self.testclass.get_object(uuid, request)

        # Assert
        actual_args = mock_list.call_args[0]

        assert expected_args == actual_args
        assert expected_result == actual_result

    @patch("oio_rest.db.list_objects")
    async def test_get_object_uses_supplied_params(self, mock):
        # Arrange
        data = [{"registreringer": [{"livscykluskode": "whatever"}]}]
        uuid = "9a543ba1-c36b-4e47-9f0f-3463ce0e297c"
        virkningfra = datetime.datetime(2012, 1, 1)
        virkningtil = datetime.datetime(2015, 1, 1)
        registreretfra = datetime.datetime(2012, 1, 1)
        registrerettil = datetime.datetime(2015, 1, 1)

        mock.return_value = [data]

        expected_args = (
            "TestClassRestObject",
            [uuid],
            str(virkningfra),
            str(virkningtil),
            str(registreretfra),
            str(registrerettil),
        )

        expected_result = {uuid: data}

        request_params = {
            "virkningfra": virkningfra,
            "virkningtil": virkningtil,
            "registreretfra": registreretfra,
            "registrerettil": registrerettil,
        }

        # Act
        request = self.create_request(params=request_params)
        actual_result = await self.testclass.get_object(uuid, request)

        # Assert
        actual_args = mock.call_args[0]

        assert expected_args == actual_args
        assert expected_result == actual_result

    @patch("oio_rest.db.list_objects")
    async def test_get_object_raises_on_no_results(self, mock):
        # Arrange
        data = []
        uuid = "4efbbbde-e197-47be-9d40-e08f1cd00259"

        mock.return_value = data

        # Act
        request = self.create_request()
        with pytest.raises(NotFoundException):
            await self.testclass.get_object(uuid, request)

    @patch("oio_rest.db.list_objects")
    async def test_get_object_raises_on_deleted_object(self, mock_list):
        # Arrange
        data = [{"registreringer": [{"livscykluskode": db.Livscyklus.SLETTET.value}]}]
        uuid = "d5995ed0-d527-4841-9e33-112b22aaade1"

        mock_list.return_value = [data]

        # Act
        request = self.create_request()
        with pytest.raises(GoneException):
            await self.testclass.get_object(uuid, request)

    @ExtTestCase.patch_db_struct(db_struct)
    @patch("oio_rest.db.list_objects")
    async def test_get_object_raises_on_unknown_args(self, mock_list):
        # Arrange
        uuid = "4efbbbde-e197-47be-9d40-e08f1cd00259"
        mock_list.return_value = []

        params = {"a": "b"}

        # Act
        request = self.create_request(params=params)
        with pytest.raises(BadRequestException):
            await self.testclass.get_object(uuid, request)

    async def test_put_object_with_no_input_returns_uuid_none_and_code_400(self):
        # Arrange
        expected_data = {"uuid": None}

        uuid = "092285a1-6dbd-4a22-be47-5dddbbec80e3"

        # Act
        request = self.create_request(method="PUT")
        with pytest.raises(HTTPException) as exp:
            await self.testclass.put_object(uuid, request)
            # Assert
            assert exp.detail == expected_data
            assert exp.status_code == 400

    @patch("oio_rest.db.object_exists")
    @patch("oio_rest.db.create_or_import_object")
    async def test_put_object_create_if_not_exists(self, mock_create, mock_exists):
        # type: (MagicMock, MagicMock) -> None
        # Arrange
        uuid = "d321b784-2bbc-40b7-aa1b-c74d931cd535"
        expected_data = {"uuid": uuid}

        mock_exists.return_value = False

        virkning = {
            "from": "2017-01-01",
            "from_included": True,
            "to": "2019-12-31",
            "to_included": False,
        }

        data = {
            "attributter": {
                "organisationegenskaber": [
                    {
                        "brugervendtnoegle": "magenta",
                        "organisationsnavn": "Magenta ApS",
                        "virkning": virkning,
                    }
                ]
            },
            "tilstande": {
                "organisationgyldighed": [{"gyldighed": "Aktiv", "virkning": virkning}]
            },
        }

        # Act
        request = self.create_request(
            method="POST",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await organisation.Organisation.put_object(uuid, request)

        # Assert
        mock_create.assert_called()
        assert expected_data == actual_data

    @patch("oio_rest.db.get_life_cycle_code")
    @patch("oio_rest.db.object_exists")
    @patch("oio_rest.db.update_object")
    @patch("oio_rest.validate.validate")
    async def test_patch_object_update_if_deleted_or_passive(
        self, mock_validate, mock_update, mock_exists, mock_life_cycle
    ):
        # type: (MagicMock, MagicMock, MagicMock) -> None
        from oio_rest.db import Livscyklus

        # Arrange
        uuid = "fa3c6c47-9594-48e3-918e-cb1208e0144c"
        expected_data = {"uuid": uuid}

        mock_exists.return_value = True

        mock_life_cycle.return_value = Livscyklus.PASSIVERET.value

        data = {"note": "NOTE"}

        # Act
        request = self.create_request(
            method="PUT",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await self.testclass.patch_object(uuid, request)

        # Assert
        mock_update.assert_called()
        assert expected_data == actual_data

    @patch("oio_rest.db.get_life_cycle_code")
    @patch("oio_rest.db.object_exists")
    @patch("oio_rest.db.update_object")
    @patch("oio_rest.validate.validate")
    async def test_patch_object_update_if_not_deleted_or_passive(
        self, mock_validate, mock_update, mock_exists, mock_life_cycle
    ):
        # type: (MagicMock, MagicMock, MagicMock) -> None
        from oio_rest.db import Livscyklus

        # Arrange
        uuid = "4b4be464-ace2-49d7-9589-04d279b0fe79"
        expected_data = {"uuid": uuid}

        mock_exists.return_value = True
        mock_life_cycle.return_value = Livscyklus.OPSTAAET.value

        data = {"note": "NOTE"}

        # Act
        request = self.create_request(
            method="PATCH",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await self.testclass.patch_object(uuid, request)

        # Assert
        mock_update.assert_called()
        assert expected_data == actual_data

    @patch("oio_rest.db.get_life_cycle_code")
    @patch("oio_rest.db.object_exists")
    @patch("oio_rest.db.passivate_object")
    @patch("oio_rest.validate.validate")
    async def test_patch_object_passivate_if_livscyklus_passiv(
        self, mock_validate, mock_passivate, mock_exists, mock_life_cycle
    ):
        # type: (MagicMock, MagicMock, MagicMock) -> None
        from oio_rest.db import Livscyklus

        # Arrange
        uuid = "b1dfa53f-89a7-4277-8c3d-86703bf87a87"
        expected_data = {"uuid": uuid}

        mock_exists.return_value = True
        mock_life_cycle.return_value = Livscyklus.OPSTAAET.value

        data = {"livscyklus": "passiv"}

        # Act
        request = self.create_request(
            method="PUT",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await self.testclass.patch_object(uuid, request)

        # Assert
        mock_passivate.assert_called()
        assert expected_data == actual_data

    async def test_put_object_raises_on_unknown_args(self):
        # Arrange
        params = {"a": "b"}

        uuid = "2b9bfc6a-f1c1-459e-a16a-79f464c075a8"

        # Act
        request = self.create_request(method="PUT", params=params)
        with pytest.raises(BadRequestException):
            await self.testclass.put_object(uuid, request)

    @patch("oio_rest.db.delete_object")
    async def test_delete_object_returns_expected_result_and_202(self, mock_delete):
        # type: (MagicMock) -> None
        # Arrange
        uuid = "cb94b2ec-33a5-4730-b87e-520e2b82fa9a"
        expected_data = {"uuid": uuid}

        data = {"note": "NOTE"}

        # Act
        request = self.create_request(
            method="PUT",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        actual_data = await self.testclass.delete_object(uuid, request)
        # Assert
        assert expected_data == actual_data

    @patch("oio_rest.db.delete_object")
    async def test_delete_object_called_with_empty_reg_and_uuid(self, mock_delete):
        # type: (MagicMock) -> None
        # Arrange
        uuid = "cb94b2ec-33a5-4730-b87e-520e2b82fa9a"

        data = {"note": "NOTE"}

        # Act
        request = self.create_request(
            method="PUT",
            headers=[["accept", "application/json"]],
            data=json.dumps(data),
        )
        await self.testclass.delete_object(uuid, request)

        # Assert
        mock_delete.assert_called()
        actual_uuid = mock_delete.call_args[0][2]
        assert uuid == actual_uuid

    async def test_delete_object_raises_on_unknown_args(self):
        # Arrange
        params = {"a": "b"}

        uuid = "2b9bfc6a-f1c1-459e-a16a-79f464c075a8"

        # Act
        request = self.create_request(method="PUT", params=params)
        with pytest.raises(BadRequestException):
            await self.testclass.delete_object(uuid, request)

    def test_gather_registration(self) -> None:
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

    def test_gather_registration_empty_input(self) -> None:
        # Arrange
        input = {}

        expected = {"attributes": {}, "states": {}, "relations": {}}

        # Act
        actual = self.testclass.gather_registration(input)

        # Assert
        assert expected == actual

    def test_gather_registration_empty_lists(self) -> None:
        # Arrange
        input = {"attributter": {}, "tilstande": {}, "relationer": {}}

        expected = {"attributes": {}, "states": {}, "relations": {}}

        # Act
        actual = self.testclass.gather_registration(input)

        # Assert
        assert expected == actual

    def test_gather_registration_raises_on_bad_attributter_input(self) -> None:
        # Arrange
        input = {
            "attributter": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)

    def test_gather_registration_raises_on_bad_tilstande_input(self) -> None:
        # Arrange
        input = {
            "tilstande": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)

    def test_gather_registration_raises_on_bad_relationer_input(self) -> None:
        # Arrange
        input = {
            "relationer": "not a dict",
        }

        # Act
        with pytest.raises(BadRequestException):
            self.testclass.gather_registration(input)


class TestOIOStandardHierarchy(ExtTestCase):
    @pytest.fixture(autouse=True)
    def setup_and_reset(self) -> None:
        self.testclass = TestClassStandardHierarchy()
        TestClassStandardHierarchy._classes = []

    def test_setup_api_calls_create_api_on_classes(self) -> None:
        # Arrange
        cls1 = MagicMock()
        cls2 = MagicMock()
        TestClassStandardHierarchy._classes = [cls1, cls2]

        # Act
        self.testclass.setup_api()

        # Assert
        cls1.create_api.assert_called_once()
        cls2.create_api.assert_called_once()

    def test_setup_api_call_router_has_expected_endpoint(self) -> None:
        # Arrange
        TestClassStandardHierarchy._classes = [MagicMock()]

        # Act
        router = self.testclass.setup_api()
        routes = router.routes
        routes = filter(lambda route: route.path == "/testclass/classes", routes)
        route = next(routes)

        # Assert
        assert "GET" in route.methods
        assert route.path == "/testclass/classes"
        assert route.name == "testclass_classes"
        assert isinstance(route.endpoint, types.FunctionType)

    async def test_setup_api_get_classes_returns_correct_result(self):
        # Arrange
        cls1 = MagicMock()
        cls1.__name__ = "name1"
        cls2 = MagicMock()
        cls2.__name__ = "name2"
        TestClassStandardHierarchy._classes = [cls1, cls2]

        expected_result = {"name1": "value1", "name2": "value2"}

        db_structure = expected_result.copy()
        db_structure.update({"garbage": "1234"})

        async with self.patch_db_struct(db_structure):
            # Act
            router = self.testclass.setup_api()
            routes = router.routes
            routes = filter(lambda route: route.path == "/testclass/classes", routes)
            route = next(routes)
            get_classes = route.endpoint

            actual_result = await get_classes()
            assert expected_result == actual_result


class TestOIORest:
    def test_typed_get_returns_value(self) -> None:
        # Arrange
        expected_result = "value"
        testkey = "testkey"
        d = {testkey: expected_result}

        # Act
        actual_result = oio_base.typed_get(d, testkey, "default")

        # Assert
        assert expected_result == actual_result

    def test_typed_get_returns_default_if_value_none(self) -> None:
        # Arrange
        expected_result = "default"
        testkey = "testkey"
        d = {testkey: None}

        # Act
        actual_result = oio_base.typed_get(d, testkey, expected_result)

        # Assert
        assert expected_result == actual_result

    def test_typed_get_raises_on_wrong_type(self) -> None:
        # Arrange
        default = 1234

        testkey = "testkey"
        d = {testkey: "value"}

        # Act & Assert
        with pytest.raises(BadRequestException):
            oio_base.typed_get(d, testkey, default)

    def test_get_virkning_dates_virkningstid(self) -> None:
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

    def test_get_virkning_dates_from_to(self) -> None:
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
    def test_get_virkning_dates_defaults(self) -> None:
        # Arrange
        args = {}

        expected_from = datetime.datetime(2017, 1, 1, 1)
        expected_to = expected_from + datetime.timedelta(microseconds=1)

        # Act
        actual_from, actual_to = oio_base.get_virkning_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_virkning_dates_raises_on_invalid_args_combination(self) -> None:
        # Arrange
        args = {
            "virkningstid": "2020-01-01",
            "virkningfra": "2006-01-01",
            "virkningtil": "2020-01-01",
        }

        # Act
        with pytest.raises(BadRequestException):
            oio_base.get_virkning_dates(args)

    def test_get_registreret_dates_registreringstid(self) -> None:
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

    def test_get_registreret_dates_from_to(self) -> None:
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
    def test_get_registreret_dates_defaults(self) -> None:
        # Arrange
        args = {}

        expected_from = None
        expected_to = None

        # Act
        actual_from, actual_to = oio_base.get_registreret_dates(args)

        # Assert
        assert expected_from == actual_from
        assert expected_to == actual_to

    def test_get_registreret_dates_raises_on_invalid_args_combination(self) -> None:
        # Arrange
        args = {
            "registreringstid": "2020-01-01",
            "registreretfra": "2006-01-01",
            "registrerettil": "2020-01-01",
        }

        # Act
        with pytest.raises(BadRequestException):
            oio_base.get_registreret_dates(args)
