# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""
Authentication
--------------

This section describes how to authenticate with MO. The API is work in
progress.

"""
import os
from fastapi import APIRouter
from starlette.requests import Request

from mora.auth.saml_sso import get_session_name_id

__all__ = ("get_user",)

from mora.settings import app_config

basedir = os.path.dirname(__file__)

router = APIRouter()


@router.get("/user")
def get_user(request: Request):
    """Get the currently logged in user

    .. :quickref: Authentication; Get user

    :return: The username of the user who is currently logged in.
    """
    if app_config["SAML_AUTH_ENABLE"]:
        return get_session_name_id(request)
    else:
        return "N/A"
