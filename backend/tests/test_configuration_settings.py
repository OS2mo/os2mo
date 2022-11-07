# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests import util

SERVICE_ENDPOINTS_CONFIGURATIONS = "/service/configuration"


@pytest.mark.parametrize(
    "test_data",
    [
        ("CONFDB_IT_SYSTEM_ENTRY_EDIT_FIELDS_DISABLED", "True"),
        ("CONFDB_IT_SYSTEM_ENTRY_EDIT_FIELDS_DISABLED", "False"),
    ],
)
async def test_feature_flag_it_system_entry_edit_fields_disabled(
    serviceapi_post, test_data
):
    feature_flag = test_data[0]
    feature_flag_expected_val = test_data[1]

    # Create computed version of the feature flag, which are the keys that actually
    # exist on the Settings class / is returned from our GraphQL
    # SERVICE_ENDPOINTS_CONFIGURATIONS-endpoint.
    # FYI: lstrip = backend\mora\service\util.py:51 - we remove 'confdb_' prefixes
    feature_flag_computed = feature_flag.lower().lstrip("confdb_")

    with util.set_settings_contextmanager(**{feature_flag: feature_flag_expected_val}):
        response = serviceapi_post(url=SERVICE_ENDPOINTS_CONFIGURATIONS)
        assert feature_flag_computed in response.data.keys()
        assert (
            str(response.data.get(feature_flag_computed)) == feature_flag_expected_val
        )
