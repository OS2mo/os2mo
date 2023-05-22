# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ramodels.mo.details.engagement import Engagement

from mo_ldap_import_export.customer_specific_checks import ExportChecks
from mo_ldap_import_export.exceptions import IgnoreChanges


@pytest.fixture
def context(dataloader: MagicMock, converter: MagicMock) -> Context:
    user_context = {"dataloader": dataloader, "converter": converter}

    return Context({"user_context": user_context})


@pytest.fixture
def export_checks(context: Context) -> ExportChecks:
    return ExportChecks(context)


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
