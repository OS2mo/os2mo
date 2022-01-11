# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch

import mora.graphapi.dataloaders as dataloaders
from mora.graphapi.main import get_schema
from mora.graphapi.models import ClassRead

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestClassessQuery:
    """Class collecting classess query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(ClassRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the classes data model."""

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            # TODO need to mock the function responsible for loading classes
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    classes {
                        facet_uuid
                        name
                        org_uuid
                        parent_uuid
                        published
                        scope
                        type
                        validity {from to}
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["classes"] == [
            {
                "facet_uuid": classes["facet_uuid"],
                "name": classes["name"],
                "org_uuid": classes["org_uuid"],
                "parent_uuid": classes["parent_uuid"],
                "published": classes["published"],
                "scope": classes["scope"],
                "type": classes["type"],
                "validity": classes["validity"],
            }
            for classes in test_data
        ]

    @given(test_data=st.lists(st.builds(ClassRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test, patch_loader):
        """Test that we can query classess by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        classes(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response = graphapi_test.post(
                "/graphql", json={"query": query, "variables": {"uuids": test_uuids}}
            )

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None

        # Check UUID equivalence
        result_uuids = [assoc.get("uuid") for assoc in data["classes"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
