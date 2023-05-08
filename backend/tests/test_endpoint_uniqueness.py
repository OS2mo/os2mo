# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import FastAPI


def test_ensure_endpoint_function_names_are_unique(fastapi_test_app: FastAPI) -> None:
    # RBAC requires these endpoints to be unique
    must_be_unique = [
        "create_org_unit",
        "terminate",
        "terminate_org_unit",
        "terminate_employee",
    ]
    endpoint_func_names = [route.name for route in fastapi_test_app.routes]

    for endpoint in must_be_unique:
        endpoint_func_names.remove(endpoint)

    without_uniques = set(endpoint_func_names)

    for endpoint in must_be_unique:
        assert endpoint not in without_uniques
