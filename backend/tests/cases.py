# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
import pprint
from unittest import IsolatedAsyncioTestCase
from unittest.case import TestCase
from unittest.mock import patch

import httpx
import pytest
import requests
from asgi_lifespan import LifespanManager
from starlette.testclient import TestClient
from structlog import get_logger

from mora import app
from mora import config
from mora import service
from mora.auth.keycloak.oidc import auth
from tests.conftest import fake_auth


logger = get_logger()


class _AsyncBaseTestCase(IsolatedAsyncioTestCase):
    """
    Async base class for MO testcases w/o LoRA access.
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

    def create_app(self, overrides=None):
        # make sure the configured organisation is always reset
        # every before test
        service.org.ConfiguredOrganisation.valid = False
        app_ = app.create_app(self.app_settings_overrides)

        return app_

    @property
    def lora_url(self):
        return config.get_settings().lora_url

    def get_token(self, use_client_secret: bool = False) -> str:
        """
        Get OIDC token from Keycloak to send with the request
        to the MO backend.

        :param use_client_secret: use client secret if true and password otherwise
        :return: Encoded OIDC token from Keycloak
        """

        data = {
            "grant_type": "password",
            "client_id": "mo",
            "username": "bruce",
            "password": "bruce",
        }
        if use_client_secret:
            data = {
                "grant_type": "client_credentials",
                "client_id": "dipex",
                "client_secret": "603f1c82-d012-4d04-9382-dbe659c533fb",
            }

        r = httpx.post(
            "http://keycloak:8080/auth/realms/mo/protocol/openid-connect/token",
            data=data,
        )

        logger.debug("Keycloak token: " + json.dumps(r.json()))

        return r.json()["access_token"]

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
            kwargs.setdefault("headers", dict()).update(
                {"Authorization": "bearer " + self.get_token()}
            )

        r = await self.request(path, **kwargs)

        if r.headers.get("content-type") == "application/json":
            actual = r.json()
        else:
            print(r.headers, r.content)  # TODO: Find r.raw alternative
            actual = r.text

        if status_code is None:
            if message is None:
                message = "status of {!r} was {}, not 2xx".format(
                    path,
                    r.status_code,
                )

            if not 200 <= r.status_code < 300:
                pprint.pprint(actual)

                self.fail(message)

        else:
            if message is None:
                message = "status of {!r} was {}, not {}".format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                ppa = pprint.pformat(actual)
                print(f"actual response:\n{ppa}")

                self.fail(message)

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

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

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        self.assertEqual(expected, actual, message)

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
            kwargs.setdefault("headers", dict()).update(
                {"Content-Type": "application/json"}
            )

            return await self.client.post(path, **kwargs)

        return await self.client.get(path, **kwargs)

    @staticmethod
    def __sort_inner_lists(obj):
        """Sort all inner lists and tuples by their JSON string value,
        recursively. This is quite stupid and slow, but works!

        This is purely to help comparison tests, as we don't care
        about the list ordering

        """
        if isinstance(obj, dict):
            return {k: AsyncTestCase.__sort_inner_lists(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return sorted(
                map(AsyncTestCase.__sort_inner_lists, obj),
                key=(lambda p: json.dumps(p, sort_keys=True)),
            )
        else:
            return obj

    def assertRegistrationsEqual(self, expected, actual, message=None):

        # drop lora-generated timestamps & users
        for k in "fratidspunkt", "tiltidspunkt", "brugerref":
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        if actual != expected:
            pprint.pprint(actual)

        # Sort all inner lists and compare
        return self.assertEqual(expected, actual, message)

    def assertRegistrationsNotEqual(self, expected, actual, message=None):
        # drop lora-generated timestamps & users
        for k in "fratidspunkt", "tiltidspunkt", "brugerref":
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        # Sort all inner lists and compare
        return self.assertNotEqual(expected, actual, message)

    def assertSortedEqual(self, expected, actual, message=None):
        """Sort all inner-lists before comparison"""

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        return self.assertEqual(expected, actual, message)


class _BaseTestCase(TestCase):
    """
    Base class for MO testcases w/o LoRA access.
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

    def create_app(self, overrides=None):
        # make sure the configured organisation is always reset
        # every before test
        service.org.ConfiguredOrganisation.valid = False
        app_ = app.create_app(self.app_settings_overrides)

        return app_

    @property
    def lora_url(self):
        return config.get_settings().lora_url

    def get_token(self, use_client_secret: bool = False) -> str:
        """
        Get OIDC token from Keycloak to send with the request
        to the MO backend.

        :param use_client_secret: use client secret if true and password otherwise
        :return: Encoded OIDC token from Keycloak
        """

        data = {
            "grant_type": "password",
            "client_id": "mo",
            "username": "bruce",
            "password": "bruce",
        }
        if use_client_secret:
            data = {
                "grant_type": "client_credentials",
                "client_id": "dipex",
                "client_secret": "603f1c82-d012-4d04-9382-dbe659c533fb",
            }

        r = requests.post(
            "http://keycloak:8080/auth/realms/mo/protocol/openid-connect/token",
            data=data,
        )

        logger.debug("Keycloak token: " + json.dumps(r.json()))

        return r.json()["access_token"]

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
            kwargs.setdefault("headers", dict()).update(
                {"Authorization": "bearer " + self.get_token()}
            )

        r = self.request(path, **kwargs)

        if r.headers.get("content-type") == "application/json":
            actual = r.json()
        else:
            print(r.headers, r.content, r.raw)
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
                pprint.pprint(actual)

                self.fail(message)

        else:
            if message is None:
                message = "status of {!r} was {}, not {}".format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                ppa = pprint.pformat(actual)
                print(f"actual response:\n{ppa}")

                self.fail(message)

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

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

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        self.assertEqual(expected, actual, message)

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
                assert kwargs.keys().isdisjoint({"method", "data"})

                # kwargs['method'] = 'POST'
                kwargs["data"] = json.dumps(kwargs.pop("json"), indent=2)
                kwargs.setdefault("headers", dict()).update(
                    {"Content-Type": "application/json"}
                )
                return client.post(path, **kwargs)

            return client.get(path, **kwargs)

    @staticmethod
    def __sort_inner_lists(obj):
        """Sort all inner lists and tuples by their JSON string value,
        recursively. This is quite stupid and slow, but works!

        This is purely to help comparison tests, as we don't care
        about the list ordering

        """
        if isinstance(obj, dict):
            return {k: TestCase.__sort_inner_lists(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return sorted(
                map(TestCase.__sort_inner_lists, obj),
                key=(lambda p: json.dumps(p, sort_keys=True)),
            )
        else:
            return obj

    def assertRegistrationsEqual(self, expected, actual, message=None):

        # drop lora-generated timestamps & users
        for k in "fratidspunkt", "tiltidspunkt", "brugerref":
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        if actual != expected:
            pprint.pprint(actual)

        # Sort all inner lists and compare
        return self.assertEqual(expected, actual, message)

    def assertRegistrationsNotEqual(self, expected, actual, message=None):
        # drop lora-generated timestamps & users
        for k in "fratidspunkt", "tiltidspunkt", "brugerref":
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        # Sort all inner lists and compare
        return self.assertNotEqual(expected, actual, message)

    def assertSortedEqual(self, expected, actual, message=None):
        """Sort all inner-lists before comparison"""

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        return self.assertEqual(expected, actual, message)


class AsyncTestCase(_AsyncBaseTestCase):
    pass


class TestCase(_BaseTestCase):
    pass


class AsyncMockRequestContextTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Patch usages of request context in test cases that do not
        # take place in a request
        # It looks iffy, and it is, but the _real_ solution would be to rewrite the
        # relevant code to not depend on a global request context
        patcher = patch("mora.util.context", new={"query_args": {}})
        patcher.start()
        self.addCleanup(patcher.stop)
        await super().asyncSetUp()


class MockRequestContextTestCase(TestCase):
    def setUp(self):
        # Patch usages of request context in test cases that do not
        # take place in a request
        # It looks iffy, and it is, but the _real_ solution would be to rewrite the
        # relevant code to not depend on a global request context
        patcher = patch("mora.util.context", new={"query_args": {}})
        patcher.start()
        self.addCleanup(patcher.stop)
        super().setUp()


@pytest.mark.serial
class AsyncLoRATestCase(_AsyncBaseTestCase):
    """Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    """


@pytest.mark.serial
class LoRATestCase(_BaseTestCase):
    """Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    """
