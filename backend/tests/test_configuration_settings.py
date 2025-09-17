# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
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
    feature_flag_computed = _compute_feature_flag_name(feature_flag)

    with util.set_settings_contextmanager(**{feature_flag: feature_flag_expected_val}):
        response = serviceapi_post(url=SERVICE_ENDPOINTS_CONFIGURATIONS)
        assert feature_flag_computed in response.data.keys()
        assert (
            str(response.data.get(feature_flag_computed)) == feature_flag_expected_val
        )


@pytest.mark.parametrize(
    "feature_flag_val,confdb_expected_return",
    [
        ("null", None),
        ("[]", []),
        (
            '["third_party_association_type"]',
            ["third_party_association_type"],
        ),
    ],
)
async def test_feature_flag_employee_hide_association_columns(
    serviceapi_post, feature_flag_val, confdb_expected_return
):
    """Test feature flag CONFDB_EMPLOYEE_HIDE_ASSOCIATION_COLUMNS.

    The flag is used by the frontend to hide employee association columns in the details table.
    """
    feature_flag_name = "CONFDB_EMPLOYEE_HIDE_ASSOCIATION_COLUMNS"
    feature_flag_name_computed = _compute_feature_flag_name(feature_flag_name)
    with util.set_settings_contextmanager(**{feature_flag_name: feature_flag_val}):
        response = serviceapi_post(url=SERVICE_ENDPOINTS_CONFIGURATIONS)
        assert feature_flag_name_computed in response.data.keys()
        assert response.data.get(feature_flag_name_computed) == confdb_expected_return


def _compute_feature_flag_name(feature_flag_name: str) -> str:
    # Create computed version of the feature flag, which are the keys that actually
    # exist on the Settings class / is returned from our GraphQL
    # SERVICE_ENDPOINTS_CONFIGURATIONS-endpoint.
    # FYI: lstrip = backend\mora\service\util.py:51 - we remove 'confdb_' prefixes
    return feature_flag_name.lower().lstrip("confdb_")
