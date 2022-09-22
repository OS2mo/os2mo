# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Custom hypothesis strategies used in the GraphAPI testing suite."""
from fastapi.encoders import jsonable_encoder
from hypothesis import strategies as st

from mora.graphapi.versions.latest.dataloaders import MOModel


@st.composite
def data_strat(draw, models: list[MOModel]):
    """Hypothesis strategy for drawing test data based on MOModels."""
    model = draw(st.sampled_from(models))
    test_data = draw(st.lists(st.builds(model)))
    return model, test_data


@st.composite
def data_with_uuids_strat(draw, models: list[MOModel]):
    """Hypothesis strategy for drawing test data including UUID samples."""
    model, test_data = draw(data_strat(models))
    test_uuids = [model.uuid for model in test_data]

    # Sample UUIDs from test_uuids
    # It's an error to sample from the empty list per the documentation,
    # and so we simply return the empty list if there is nothing to sample.
    sampled_uuids = draw(st.lists(st.sampled_from(test_uuids))) if test_uuids else []

    # Sample UUIDs that are *not* in the set of test_uuids
    not_from_test_uuids = st.uuids().filter(lambda uuid: uuid not in set(test_uuids))
    other_uuids = draw(st.lists(not_from_test_uuids))

    return model, test_data, sampled_uuids, other_uuids


@st.composite
def graph_data_strat(draw, model: MOModel):
    """Hypothesis strategy for drawing encoded test data based on a specific MOModel."""
    data = draw(st.lists(st.builds(model)))
    return jsonable_encoder(data)


@st.composite
def graph_data_uuids_strat(draw, model: MOModel):
    """Hypothesis strategy for drawing data and uuids based on a specific MOModel."""
    data = draw(graph_data_strat(model))
    uuids = list(map(lambda model: model.get("uuid"), data))
    test_uuids = draw(st.lists(st.sampled_from(uuids))) if uuids else []
    test_data = list(filter(lambda obj: obj.get("uuid") in test_uuids, data))
    return test_data, test_uuids
