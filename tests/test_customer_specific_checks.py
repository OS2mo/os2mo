# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.details.it_system import ITUser

from mo_ldap_import_export.customer_specific_checks import ExportChecks
from mo_ldap_import_export.customer_specific_checks import ImportChecks
from mo_ldap_import_export.exceptions import IgnoreChanges


@pytest.fixture
def context(dataloader: MagicMock, converter: MagicMock) -> Context:
    user_context = {"dataloader": dataloader, "converter": converter}

    return Context({"user_context": user_context})


@pytest.fixture
def export_checks(context: Context) -> ExportChecks:
    return ExportChecks(context)


@pytest.fixture
def import_checks(context: Context) -> ImportChecks:
    return ImportChecks(context)


async def test_check_holstebro_ou_is_externals_custom_succeeds(
    import_checks: ImportChecks,
):
    result = await import_checks.check_holstebro_ou_is_externals_issue_57426(
        ["doesn't matter"], "neither does this", "Custom"
    )
    assert result is True


async def test_check_holstebro_ou_is_externals_no_error(import_checks: ImportChecks):
    result = await import_checks.check_holstebro_ou_is_externals_issue_57426(
        ["OU=External consultants,OU=HK"],
        "OU=Magenta,OU=External consultants,OU=HK,DC=test",
        "Test",
    )
    assert result is True


async def test_check_holstebro_ou_is_externals_error(import_checks: ImportChecks):
    result = await import_checks.check_holstebro_ou_is_externals_issue_57426(
        ["OU=Nothing Here", "OU=Also,OU=Nothing Here"], "OU=HK,DC=test", "Test"
    )
    assert result is False


async def test_check_holstebro_ou_is_externals_error2(import_checks: ImportChecks):
    result = await import_checks.check_holstebro_ou_is_externals_issue_57426(
        ["OU=Nothing Here", "OU=hierarchy,OU=HK Eksterne,OU=HK"],
        "OU=HK,DC=test",
        "Test",
    )
    assert result is False


async def test_check_alleroed_sd_number(
    export_checks: ExportChecks, dataloader: MagicMock
):
    """
    Check that IgnoreChanges is raised when an employee number starts with 9
    """

    normal_engagement = Engagement.from_simplified_fields(
        uuid4(), uuid4(), uuid4(), uuid4(), "1234", "2021-01-01"
    )
    hourly_paid_worker_engagement = Engagement.from_simplified_fields(
        uuid4(), uuid4(), uuid4(), uuid4(), "91234", "2021-01-01"
    )

    dataloader.load_mo_employee_engagements.return_value = [normal_engagement]
    assert (await export_checks.check_alleroed_sd_number(uuid4(), uuid4())) is None

    dataloader.load_mo_employee_engagements.return_value = [
        hourly_paid_worker_engagement
    ]
    with pytest.raises(IgnoreChanges):
        await export_checks.check_alleroed_sd_number(uuid4(), uuid4())

    dataloader.load_mo_employee_engagements.return_value = [
        hourly_paid_worker_engagement,
        normal_engagement,
    ]
    with pytest.raises(IgnoreChanges):
        await export_checks.check_alleroed_sd_number(
            uuid4(), hourly_paid_worker_engagement.uuid
        )

    assert (await export_checks.check_alleroed_sd_number(uuid4(), uuid4())) is None

    dataloader.load_mo_employee_engagements.return_value = []

    assert (await export_checks.check_alleroed_sd_number(uuid4(), uuid4())) is None


async def test_check_it_user(export_checks: ExportChecks, dataloader: MagicMock):
    dataloader.load_mo_employee_it_users.return_value = [
        ITUser.from_simplified_fields("foo", uuid4(), "2021-01-01")
    ]

    # If the user_key attribute is empty, no exception should be raised
    await export_checks.check_it_user(uuid4(), "")

    # If the it-user exist, no exception should be raised
    await export_checks.check_it_user(uuid4(), "foo")

    # If the it-user does not exist, we need to raise
    dataloader.load_mo_employee_it_users.return_value = []
    with pytest.raises(IgnoreChanges):
        await export_checks.check_it_user(uuid4(), "foo")
