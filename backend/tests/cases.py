# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from contextlib import suppress
from unittest import IsolatedAsyncioTestCase
from unittest.case import TestCase

import httpx
import pytest
from asgi_lifespan import LifespanManager
from starlette.testclient import TestClient
from structlog import get_logger

from mora import app
from mora import config
from mora import service
from mora.auth.keycloak.oidc import auth
from tests.conftest import fake_auth
from tests.conftest import get_keycloak_token


logger = get_logger()

# Global variables for test optimizations
base_test_app = None


def sort_inner_lists(obj):
    """Sort all inner lists and tuples by their JSON string value,
    recursively. This is quite stupid and slow, but works!

    This is purely to help comparison tests, as we don't care
    about the list ordering

    """
    if isinstance(obj, dict):
        return {k: sort_inner_lists(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return sorted(
            map(sort_inner_lists, obj),
            key=(lambda p: json.dumps(p, sort_keys=True)),
        )
    return obj


def assert_registrations_equal(expected, actual, message=None) -> None:
    # drop lora-generated timestamps & users
    for k in "fratidspunkt", "tiltidspunkt", "brugerref":
        expected.pop(k, None)
        actual.pop(k, None)

    actual = sort_inner_lists(actual)
    expected = sort_inner_lists(expected)

    # Sort all inner lists and compare
    assert expected == actual, message


def assert_registrations_not_equal(expected, actual, message=None) -> None:
    # drop lora-generated timestamps & users
    for k in "fratidspunkt", "tiltidspunkt", "brugerref":
        expected.pop(k, None)
        actual.pop(k, None)

    actual = sort_inner_lists(actual)
    expected = sort_inner_lists(expected)

    # Sort all inner lists and compare
    assert expected != actual, message


def assert_sorted_equal(expected, actual, message=None) -> None:
    """Sort all inner-lists before comparison"""
    expected = sort_inner_lists(expected)
    actual = sort_inner_lists(actual)

    assert expected == actual, message


class MixinTestCase(TestCase):
    def create_app(self, overrides=None):
        global base_test_app
        if not base_test_app:
            service.org.ConfiguredOrganisation.valid = False
            base_test_app = app.create_app(self.app_settings_overrides)

        return base_test_app

    def assertRegistrationsEqual(self, expected, actual, message=None):
        assert_registrations_equal(expected, actual, message)

    def assertRegistrationsNotEqual(self, expected, actual, message=None):
        assert_registrations_not_equal(expected, actual, message)

    def assertSortedEqual(self, expected, actual, message=None):
        assert_sorted_equal(expected, actual, message)


@pytest.mark.integration_test
class AsyncLoRATestCase(MixinTestCase, IsolatedAsyncioTestCase):
    """Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    """

    maxDiff = None
    app_settings_overrides = {}

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.app = self.create_app()
        self.lifespanmanager = LifespanManager(self.app)
        await self.lifespanmanager.__aenter__()

        self.client = httpx.AsyncClient(
            app=self.app,
            base_url="http://localhost:5000",
            timeout=config.get_settings().httpx_timeout,
        )

        # Bypass Keycloak per default
        self.app.dependency_overrides[auth] = fake_auth

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.client.aclose()
        await self.lifespanmanager.__aexit__()

    async def assertRequest(
        self,
        path,
        status_code=None,
        message=None,
        *,
        drop_keys=(),
        amqp_topics=(),
        set_auth_header=False,
        **kwargs,
    ):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        :return: The result of the request, as a string or object, if
                 JSON.

        """

        # Get OIDC token from Keycloak and add an auth request header
        if set_auth_header:
            kwargs.setdefault("headers", {}).update(
                {"Authorization": "bearer " + get_keycloak_token()}
            )

        r = await self.request(path, **kwargs)

        if r.headers.get("content-type") == "application/json":
            actual = r.json()
        else:
            actual = r.text

        if status_code is None:
            if message is None:
                message = "status of {!r} was {}, not 2xx".format(
                    path,
                    r.status_code,
                )

            if not 200 <= r.status_code < 300:
                self.fail(message)

        else:
            if message is None:
                message = "status of {!r} was {}, not {}".format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                self.fail(message)

        for k in drop_keys:
            with suppress((IndexError, KeyError, TypeError)):
                actual.pop(k)

        return actual

    async def assertRequestResponse(
        self,
        path,
        expected,
        message=None,
        amqp_topics=(),
        set_auth_header=False,
        **kwargs,
    ):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        """

        actual = await self.assertRequest(
            path,
            message=message,
            amqp_topics=amqp_topics,
            set_auth_header=set_auth_header,
            **kwargs,
        )

        expected = sort_inner_lists(expected)
        actual = sort_inner_lists(actual)

        self.assertEqual(expected, actual, msg=message)

    async def assertRequestFails(
        self, path, code, message=None, set_auth_header=False, **kwargs
    ):
        """Issue a request and assert that it fails with the given status.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        """

        await self.assertRequest(
            path,
            message=message,
            status_code=code,
            set_auth_header=set_auth_header,
            **kwargs,
        )

    async def request(self, path, **kwargs):
        if "json" in kwargs:
            # "In the face of ambiguity, refuse the temptation to guess."
            # ...so check that the arguments we override don't exist
            assert kwargs.keys().isdisjoint({"method", "data"})

            # kwargs['method'] = 'POST'
            kwargs["content"] = json.dumps(kwargs.pop("json"), indent=2)
            kwargs.setdefault("headers", {}).update(
                {"Content-Type": "application/json"}
            )

            return await self.client.post(path, **kwargs)

        return await self.client.get(path, **kwargs)


@pytest.mark.integration_test
class LoRATestCase(MixinTestCase):
    """Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    """

    maxDiff = None
    app_settings_overrides = {}

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.app = self.create_app()
        self.client = TestClient(self.app)

        # Bypass Keycloak per default
        self.app.dependency_overrides[auth] = fake_auth

    def assertRequest(
        self,
        path,
        status_code=None,
        message=None,
        *,
        drop_keys=(),
        amqp_topics=(),
        set_auth_header=False,
        **kwargs,
    ):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        :return: The result of the request, as a string or object, if
                 JSON.

        """

        # Get OIDC token from Keycloak and add an auth request header
        if set_auth_header:
            kwargs.setdefault("headers", {}).update(
                {"Authorization": "bearer " + get_keycloak_token()}
            )

        r = self.request(path, **kwargs)

        if r.headers.get("content-type") == "application/json":
            actual = r.json()
        else:
            actual = r.text

        # actual = (
        #     json.loads(r.get_data(True))
        #     if r.mimetype == 'application/json'
        #     else r.get_data(True)
        # )

        if status_code is None:
            if message is None:
                message = "status of {!r} was {}, not 2xx".format(
                    path,
                    r.status_code,
                )

            if not 200 <= r.status_code < 300:
                self.fail(message)

        else:
            if message is None:
                message = "status of {!r} was {}, not {}".format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                self.fail(message)

        for k in drop_keys:
            with suppress((IndexError, KeyError, TypeError)):
                actual.pop(k)

        return actual

    def assertRequestResponse(
        self,
        path,
        expected,
        message=None,
        amqp_topics=(),
        set_auth_header=False,
        **kwargs,
    ):
        """Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        """

        actual = self.assertRequest(
            path,
            message=message,
            amqp_topics=amqp_topics,
            set_auth_header=set_auth_header,
            **kwargs,
        )

        expected = sort_inner_lists(expected)
        actual = sort_inner_lists(actual)

        self.assertEqual(expected, actual)

    def assertRequestFails(
        self, path, code, message=None, set_auth_header=False, **kwargs
    ):
        """Issue a request and assert that it fails with the given status.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        """

        self.assertRequest(
            path,
            message=message,
            status_code=code,
            set_auth_header=set_auth_header,
            **kwargs,
        )

    def request(self, path, **kwargs):
        with self.client as client:
            if "json" in kwargs:
                # "In the face of ambiguity, refuse the temptation to guess."
                # ...so check that the arguments we override don't exist
                self.assertNotIn("method", kwargs)
                self.assertNotIn("data", kwargs)

                # kwargs['method'] = 'POST'
                kwargs["data"] = json.dumps(kwargs.pop("json"), indent=2)
                kwargs.setdefault("headers", {}).update(
                    {"Content-Type": "application/json"}
                )
                return client.post(path, **kwargs)

            return client.get(path, **kwargs)
