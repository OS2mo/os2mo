# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from uuid import UUID
from unittest.mock import patch

from ramodels.lora._shared import InfiniteDatetime
from fastapi.testclient import TestClient


class TestCreateMutation:
    query = """
    mutation {
      create_organisation(name: "X", user_key: "Y") {
        __typename
        ... on GenericError {
          error_message
        }
        ... on Organisation {
          uuid
          name
          user_key
        }
      }
    }
    """

    def run_query(self, graphapi_test):
        response = graphapi_test.post("/graphql", json={"query": self.query})
        assert response.status_code == 200
        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        return data

    @patch("mora.lora.Scope")
    def test_create_organisation(self, scope_fetch, graphapi_test: TestClient):
        class TestScope:
            async def fetch(self, **params):
                return []

            async def create(self, obj, uuid=None):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                assert obj == {
                    "attributter": {
                        "organisationegenskaber": [
                            {
                                "brugervendtnoegle": "Y",
                                "organisationsnavn": "X",
                                "virkning": {
                                    "from": InfiniteDatetime("-infinity"),
                                    "to": InfiniteDatetime("infinity"),
                                },
                            }
                        ]
                    },
                    "tilstande": {
                        "organisationgyldighed": [
                            {
                                "gyldighed": "Aktiv",
                                "virkning": {
                                    "from": InfiniteDatetime("-infinity"),
                                    "to": InfiniteDatetime("infinity"),
                                },
                            }
                        ]
                    },
                }
                return str(uuid)

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "create_organisation": {
                "__typename": "Organisation",
                "uuid": "67e9a80e-6bc0-e97a-9751-02600c017844",
                "name": "X",
                "user_key": "Y",
            }
        }

    @patch("mora.lora.Scope")
    def test_create_organisation_already_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return ["f214b54f-6a95-4c57-9710-207fae773680"]

            async def create(self, obj, uuid=None):
                assert False

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "create_organisation": {
                "__typename": "GenericError",
                "error_message": "An organisation already exists",
            }
        }

    @patch("mora.lora.Scope")
    def test_create_organisation_multiple_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return [
                    "f214b54f-6a95-4c57-9710-207fae773680",
                    "01881f4f-aba1-48af-9b06-da4aa464ede6",
                ]

            async def create(self, obj, uuid=None):
                assert False

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "create_organisation": {
                "__typename": "GenericError",
                "error_message": "An organisation already exists",
            }
        }


class TestEditMutation:

    query = """
    mutation {
      edit_organisation(
        name: "X",
        user_key: "Y",
        uuid: "67e9a80e-6bc0-e97a-9751-02600c017844"
    ) {
        __typename
        ... on GenericError {
          error_message
        }
        ... on Organisation {
          uuid
          name
          user_key
        }
      }
    }
    """

    def run_query(self, graphapi_test):
        response = graphapi_test.post("/graphql", json={"query": self.query})
        assert response.status_code == 200
        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        return data

    @patch("mora.lora.Scope")
    def test_edit_organisation_none_exist(self, scope_fetch, graphapi_test: TestClient):
        class TestScope:
            async def fetch(self, **params):
                return []

            async def create(self, obj, uuid=None):
                assert False

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "edit_organisation": {
                "__typename": "GenericError",
                "error_message": "An organisation does not exist",
            }
        }

    @patch("mora.lora.Scope")
    def test_edit_organisation(self, scope_fetch, graphapi_test: TestClient):
        class TestScope:
            async def fetch(self, **params):
                return ["67e9a80e-6bc0-e97a-9751-02600c017844"]

            async def create(self, obj, uuid=None):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                assert obj == {
                    "attributter": {
                        "organisationegenskaber": [
                            {
                                "brugervendtnoegle": "Y",
                                "organisationsnavn": "X",
                                "virkning": {
                                    "from": InfiniteDatetime("-infinity"),
                                    "to": InfiniteDatetime("infinity"),
                                },
                            }
                        ]
                    },
                    "tilstande": {
                        "organisationgyldighed": [
                            {
                                "gyldighed": "Aktiv",
                                "virkning": {
                                    "from": InfiniteDatetime("-infinity"),
                                    "to": InfiniteDatetime("infinity"),
                                },
                            }
                        ]
                    },
                }
                return str(uuid)

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "edit_organisation": {
                "__typename": "Organisation",
                "uuid": "67e9a80e-6bc0-e97a-9751-02600c017844",
                "name": "X",
                "user_key": "Y",
            }
        }

    @patch("mora.lora.Scope")
    def test_edit_organisation_already_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return ["f214b54f-6a95-4c57-9710-207fae773680"]

            async def create(self, obj, uuid=None):
                assert False

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "edit_organisation": {
                "__typename": "GenericError",
                "error_message": (
                    "The provided UUID does not match the existing organisation"
                ),
            }
        }

    @patch("mora.lora.Scope")
    def test_edit_organisation_multiple_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return [
                    "f214b54f-6a95-4c57-9710-207fae773680",
                    "01881f4f-aba1-48af-9b06-da4aa464ede6",
                ]

            async def create(self, obj, uuid=None):
                assert False

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {
            "edit_organisation": {
                "__typename": "GenericError",
                "error_message": "Multiple organisations exist",
            }
        }


class TestTerminationMutation:

    query = """
    mutation {
      remove_organisation(uuid: "67e9a80e-6bc0-e97a-9751-02600c017844") {
        error_message
      }
    }
    """

    def run_query(self, graphapi_test):
        response = graphapi_test.post("/graphql", json={"query": self.query})
        assert response.status_code == 200
        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        return data

    @patch("mora.lora.Scope")
    def test_terminate_organisation_none_exist(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return []

            async def delete(self, uuid):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                return None

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {"remove_organisation": None}

    @patch("mora.lora.Scope")
    def test_terminate_organisation(self, scope_fetch, graphapi_test: TestClient):
        class TestScope:
            async def fetch(self, **params):
                return ["67e9a80e-6bc0-e97a-9751-02600c017844"]

            async def delete(self, uuid):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                return None

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {"remove_organisation": None}

    @patch("mora.lora.Scope")
    def test_terminate_organisation_already_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return ["f214b54f-6a95-4c57-9710-207fae773680"]

            async def delete(self, uuid):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                return None

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {"remove_organisation": None}

    @patch("mora.lora.Scope")
    def test_terminate_organisation_multiple_exists(
        self, scope_fetch, graphapi_test: TestClient
    ):
        class TestScope:
            async def fetch(self, **params):
                return [
                    "f214b54f-6a95-4c57-9710-207fae773680",
                    "01881f4f-aba1-48af-9b06-da4aa464ede6",
                ]

            async def delete(self, uuid):
                assert uuid == UUID("67e9a80e-6bc0-e97a-9751-02600c017844")
                return None

        scope_fetch.return_value = TestScope()
        data = self.run_query(graphapi_test)
        assert data == {"remove_organisation": None}
