# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch
from ramodels.mo.details import ITSystemRead

import mora.graphapi.dataloaders as dataloaders
import mora.graphapi.main as main
from mora.graphapi.main import get_schema

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestITSystemsQuery:
    """Class collecting ITSystems query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(ITSystemRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the ITSystem data model."""

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(main, "get_itsystems", patch_loader(test_data))
            query = """
                query {
                    itsystems {
                        name
                        system_type
                        type
                        user_key
                        uuid
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["itsystems"] == [
            {
                "name": itsystem["name"],
                "system_type": itsystem["system_type"],
                "type": itsystem["type"],
                "user_key": itsystem["user_key"],
                "uuid": itsystem["uuid"],
            }
            # JSON encode test data
            for itsystem in jsonable_encoder(test_data)
        ]

    @given(test_data=st.lists(st.builds(ITSystemRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test):
        """Test that we can query ITSystems by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(
                dataloaders,
                "lora_itsystem_to_mo_itsystem",
                lambda *args, **kwargs: test_data,
            )
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        itsystems(uuids: $uuids) {
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
        result_uuids = [
            model.get("uuid") for model in jsonable_encoder(data["itsystems"])
        ]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
