# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json

import pytest

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.main import get_conversion_map


@pytest.mark.usefixtures("load_settings_overrides")
@pytest.mark.parametrize(
    "filename",
    (
        "holstebro",
        "magenta_demo",
        "magenta_demo_no_cpr",
    ),
)
def test_file_and_environmental_variable_conversion_map_equivalence(
    monkeypatch: pytest.MonkeyPatch, filename: str
) -> None:
    # Load using YAML file
    monkeypatch.setenv("CONVERSION_MAP", filename + ".yaml")
    settings = Settings()
    yaml_result = get_conversion_map(settings)

    # Load using JSON file
    monkeypatch.setenv("CONVERSION_MAP", filename + ".json")
    settings = Settings()
    json_result = get_conversion_map(settings)

    # Load using environmental variables
    monkeypatch.setenv(
        "CONVERSION_MAPPING", json.dumps(yaml_result.dict(by_alias=True))
    )
    settings = Settings()
    env_result = get_conversion_map(settings)

    assert yaml_result == json_result
    assert yaml_result == env_result
