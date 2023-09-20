# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Custom hypothesis strategies used in the GraphAPI testing suite."""
import datetime

from fastapi.encoders import jsonable_encoder
from hypothesis import strategies as st

from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.graphql_utils import PrintableStr
from ramodels.mo import Validity as RAValidity


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


@st.composite
def graph_data_momodel_validity_strat(
    draw, model: MOModel, now: datetime.datetime = None
):
    return jsonable_encoder(draw(_strat_data_momodel_validity(draw, model, now)))


@st.composite
def graph_data_momodel_validity_strat_list(
    draw, model: MOModel, now: datetime.datetime = None
):
    return jsonable_encoder(
        draw(st.lists(_strat_data_momodel_validity(draw, model, now)))
    )


# local helpers


def _strat_data_momodel_validity(draw, model: MOModel, now: datetime.datetime = None):
    data_args = {}
    min_dt = datetime.datetime(1900, 1, 1)
    if "validity" in model.__fields__:
        validity_tuple = draw(
            st.tuples(
                st.datetimes(min_value=min_dt),
                st.datetimes(min_value=min_dt) | st.none(),
            )
            .filter(
                # only generate validities that are valid NOW / have currents - if NOW is specified
                lambda dts: (dts[0] <= now if now else True)
                and (dts[1] >= now if dts[1] and now else True)
            )
            .filter(
                # Only generate validities where from_date <= to_date
                lambda dts: dts[0] <= dts[1]
                if dts[0] and dts[1]
                else True
            )
        )

        data_args["validity"] = st.builds(
            RAValidity,
            from_date=st.just(validity_tuple[0]),
            to_date=st.just(validity_tuple[1]),
        )

    # If there is a name in model, it must be a PrintableStr and not be empty
    if "name" in model.__fields__:
        data_args["name"] = st.from_regex(PrintableStr.regex)

    if "user_key" in model.__fields__:
        data_args["user_key"] = st.from_regex(PrintableStr.regex)

    return st.builds(model, **data_args)
