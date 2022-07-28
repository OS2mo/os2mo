# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from tests.conftest import GQLResponse

# --------------------------------------------------------------------------------------
# Class mutator tests
# --------------------------------------------------------------------------------------


class TestClassesMutator:

    """Helper function for tests"""

    def terminate_class(self, uuid: str, graphapi_post):
        """Terminate class"""
        query = 'mutation {class_terminate(input: {uuid: "' + uuid + '"})}'
        response: GQLResponse = graphapi_post(query=query)

        return response

    def test_class_terminate(self, graphapi_post):

        """Post-query classes already deleted to check they're actually deleted"""

        def query_terminated_class(uuid: str):
            """Query class by uuid"""
            query = 'query {classes(uuids: "' + uuid + '"){type}}'
            response: GQLResponse = graphapi_post(query=query)
            return response

        """Assert responses from termination and post-queries"""

        def assert_data_response(response, mutation):
            """Assert response from class termination"""
            assert response.errors is None
            assert response.data
            if mutation:
                assert response.data == {
                    "class_terminate": "Class deleted - Response: None",
                }
            else:
                """Assert class is deleted by checking response after query"""
                assert len(response.data["classes"]) == 0

        def terminate(uuid):
            response = self.terminate_class(uuid, graphapi_post)
            assert_data_response(response, mutation=True)
            response = query_terminated_class(uuid)
            assert_data_response(response, mutation=False)

        """Get a list of all existing classes"""
        query = """query MyQuery {
                                    facets {
                                            classes {
                                                    uuid
                                                    user_key
                                                    type
                                                    scope
                                                    published
                                                    parent_uuid
                                                    example
                                                    owner
                                                    }
                                            }
                                }
                    """

        query_response: GQLResponse = graphapi_post(query=query)

        classes_list = query_response.data["facets"]

        class_uuid_list = [
            uuid["classes"][0]["uuid"]
            for uuid in classes_list
            if len(uuid["classes"]) > 0
        ]

        [terminate(uuid) for uuid in class_uuid_list]

    def test_class_terminate_fails(self, graphapi_post):

        illegal_uuids = ["35d5d061-5d19-4584-8c5e-796309b87dfb", ""]

        response = self.terminate_class(illegal_uuids[0], graphapi_post)
        assert response.data is None
        assert response.errors[0]["message"] == "ErrorCodes.E_UNKNOWN"

        response = self.terminate_class(illegal_uuids[1], graphapi_post)
        assert response.data is None
        assert (
            response.errors[0]["message"]
            == 'Value cannot represent a UUID: "". badly formed hexadecimal UUID string'
        )
