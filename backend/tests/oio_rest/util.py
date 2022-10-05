# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import contextlib
import json
import os
import pprint
import types
import unittest
import uuid
from contextlib import suppress
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from oio_rest.app import create_app
from oio_rest.auth.oidc import auth
from oio_rest.db.testing import reset_testing_database
from oio_rest.db.testing import setup_testing_database

TESTS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(TESTS_DIR)
FIXTURE_DIR = os.path.join(TESTS_DIR, "fixtures")


async def mock_auth():
    return {
        "acr": "1",
        "allowed-origins": ["http://localhost:5000"],
        "azp": "vue",
        "email": "bruce@kung.fu",
        "email_verified": False,
        "exp": 1621779689,
        "family_name": "Lee",
        "given_name": "Bruce",
        "iat": 1621779389,
        "iss": "http://keycloak:8080/auth/realms/lora",
        "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
        "name": "Bruce Lee",
        "preferred_username": "bruce",
        "scope": "email profile",
        "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
        "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
        "typ": "Bearer",
    }


def get_fixture(fixture_name, mode="rt", as_text=True):
    """Reads data from fixture folder. If the file name ends with
    ``.json``, we parse it, otherwise, we just return it as text.
    """
    with open(os.path.join(FIXTURE_DIR, fixture_name), mode) as fp:
        if os.path.splitext(fixture_name)[1] == ".json" and as_text:
            return json.load(fp)
        else:
            return fp.read()


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    """Basic testcase without database support, but with various helper functions."""

    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

        # Bypass Keycloak per default
        self.app.dependency_overrides[auth] = mock_auth

    def setup(self):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)

        for p in (
            mock.patch("oio_rest.settings.FILE_UPLOAD_FOLDER", "./mox-upload"),
            mock.patch("oio_rest.settings.LOG_AMQP_SERVER", None),
        ):
            stack.enter_context(p)

    def assertRequestResponse(
        self, path, expected, message=None, status_code=None, drop_keys=(), **kwargs
    ):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        **kwargs is passed directly to the test client -- see the
        documentation for werkzeug.test.EnvironBuilder for details.

        One addition is that we support a 'json' argument that
        automatically posts the given JSON data.

        """
        r = self.perform_request(path, **kwargs)
        actual = r.text
        if r.headers.get("content-type", "") == "application/json":
            actual = json.loads(actual)

        for k in drop_keys:
            with suppress((IndexError, KeyError, TypeError)):
                actual.pop(k)

        if not message:
            status_message = "request {!r} failed with status {}".format(
                path,
                r.status_code,
            )
            content_message = "request {!r} yielded an unexpected result".format(
                path,
            )
        else:
            status_message = content_message = message

        try:
            if status_code is None:
                self.assertOK(r, status_message)
            else:
                assert r.status_code == status_code, status_message

            assert expected == actual, content_message

        except AssertionError:
            print(path)
            print(r.status_code)
            pprint.pprint(actual)

            raise

    def assertRequestFails(self, path, code, message=None, **kwargs):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        **kwargs is passed directly to the test client -- see the
        documentation for werkzeug.test.EnvironBuilder for details.

        One addition is that we support a 'json' argument that
        automatically posts the given JSON data.
        """
        message = message or f"request {path!r} didn't fail properly"

        r = self.perform_request(path, **kwargs)

        assert r.status_code == code, (message + ": ") + r.text

    def perform_request(self, path, **kwargs):
        if "json" in kwargs:
            kwargs.setdefault("method", "POST")
            kwargs.setdefault("data", json.dumps(kwargs.pop("json"), indent=2))
            kwargs.setdefault("headers", {"Content-Type": "application/json"})
        kwargs.setdefault("method", "GET")
        return self.client.request(url=path, **kwargs)

    def assertRegistrationsEqual(self, expected, actual, message=None):
        def sort_inner_lists(obj):
            """Sort all inner lists and tuples by their JSON string value,
            recursively. This is quite stupid and slow, but works!

            This is purely to help comparison tests, as we don't care about the
            list ordering

            """
            if isinstance(obj, dict):
                return {k: sort_inner_lists(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return sorted(
                    map(sort_inner_lists, obj),
                    key=(lambda p: json.dumps(p, sort_keys=True)),
                )
            return obj

        # drop lora-generated timestamps & users
        if isinstance(expected, dict):
            expected.pop("fratidspunkt", None)
            expected.pop("tiltidspunkt", None)
            expected.pop("brugerref", None)

        if isinstance(actual, dict):
            actual.pop("fratidspunkt", None)
            actual.pop("tiltidspunkt", None)
            actual.pop("brugerref", None)

        # Sort all inner lists and compare
        assert sort_inner_lists(expected) == sort_inner_lists(actual), message

    def assertOK(self, response, message=None):
        assert 200 <= response.status_code < 300, (
            message or f"request failed with {response.status_code}!"
        )

    def assertUUID(self, s):
        try:
            uuid.UUID(s)
        except (TypeError, ValueError):
            self.fail(f"{s!r} is not a uuid!")

    def assert201(self, response):
        """
        Verify that the response from LoRa is 201 and contains the correct
        JSON.
        :param response: Response from LoRa when creating a new object
        """
        assert response.status_code == 201
        assert len(response.json()) == 1
        self.assertUUID(response.json()["uuid"])

    def get(self, path, **params):
        r = self.perform_request(path, params=params, method="GET")

        self.assertOK(r)

        d = r.json()["results"][0]

        if not d or not all(isinstance(v, dict) for v in d):
            return d

        assert len(d) == 1

        registrations = d[0]["registreringer"]

        if set(params.keys()) & {
            "registreretfra",
            "registrerettil",
            "registreringstid",
        }:
            return registrations
        else:
            assert len(registrations) == 1
            return registrations[0]

    def put(self, path, json):
        r = self.perform_request(path, json=json, method="PUT")
        self.assertOK(r)

        return r.json()["uuid"]

    def patch(self, path, json):
        r = self.perform_request(path, json=json, method="PATCH")
        self.assertOK(r)

        return r.json()["uuid"]

    def post(self, path, json):
        r = self.perform_request(path, json=json, method="POST")
        self.assertOK(r)

        return r.json()["uuid"]

    def delete(self, path, json):
        r = self.perform_request(path, json=json, method="DELETE")
        self.assertOK(r)

        return r.json()["uuid"]

    def assertQueryResponse(self, path, expected, **params):
        """Perform a request towards LoRa, and assert that it yields the
        expected output.

        Results are unpacked from the LoRa result structure and filtered of
        metadata before comparison

        **params are passed as part of the query string in the request.
        """

        actual = self.get(path, **params)

        print(json.dumps(actual, indent=2))

        self.assertRegistrationsEqual(expected, actual)

    def load_fixture(self, path, fixture_name, uuid=None):
        """Load a fixture, i.e. a JSON file in the 'fixtures' directory,
        into LoRA at the given path & UUID.
        """
        if uuid:
            method = "PUT"
            path = f"{path}/{uuid}"
        else:
            method = "POST"

        r = self.perform_request(
            path,
            json=get_fixture(fixture_name),
            method=method,
        )

        msg = f"write of {fixture_name!r} to {path!r} failed!"

        try:
            self.assertOK(r, msg)

            objid = r.json().get("uuid")

            assert objid
        except AssertionError:
            print(path)
            print(r.status)
            print(r.get_data(as_text=True))

            raise

        return objid


class ExtTestCase(BaseTestCase):
    """Testcase with extension helper functions, but no database access"""

    @classmethod
    @contextlib.contextmanager
    def patch_db_struct(cls, new: types.ModuleType | dict):
        """Context manager for overriding db_structures"""

        patches = [
            mock.patch("oio_rest.db.db_helpers._attribute_fields", {}),
            mock.patch("oio_rest.db.db_helpers._attribute_names", {}),
            mock.patch("oio_rest.db.db_helpers._relation_names", {}),
            mock.patch("oio_rest.validate.SCHEMAS", {}),
        ]

        if isinstance(new, types.ModuleType):
            patches.append(
                mock.patch(
                    "oio_rest.db.db_structure.REAL_DB_STRUCTURE",
                    new=new.REAL_DB_STRUCTURE,
                )
            )
        else:
            patches.append(
                mock.patch("oio_rest.db.db_structure.REAL_DB_STRUCTURE", new=new)
            )

        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)

            yield


@pytest.mark.integration_test
@pytest.mark.usefixtures("tests_setup_and_teardown")
class DBTestCase(BaseTestCase):
    """Testcase with database access"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Install 'actual_state' schema in testing database. Or if already
        # installed, truncate the tables in the 'actual_state' schema.
        setup_testing_database()

    def setUp(self):
        super().setUp()
        # Truncate tables before each test
        reset_testing_database()
