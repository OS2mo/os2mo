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
        "alleroed.json",
        "groenland.json",
        "holstebro.json",
        "magenta_demo.json",
        "magenta_demo_no_cpr.json",
    ),
)
def test_file_and_environmental_variable_conversion_map_equivalence(
    monkeypatch: pytest.MonkeyPatch, filename: str
) -> None:
    # Load using file
    monkeypatch.setenv("CONVERSION_MAP", filename)
    settings = Settings()
    file_result = get_conversion_map(settings)

    # Load using environmental variables
    monkeypatch.setenv("CONVERSION_MAPPING", json.dumps(file_result.dict()))
    settings = Settings()
    env_result = get_conversion_map(settings)

    assert file_result == env_result
