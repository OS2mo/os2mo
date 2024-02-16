# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from mo_ldap_import_export.os2mo_init import InitEngine


@pytest.fixture()
def mapping() -> dict:
    mapping = {
        "init": {
            "it_systems": {"ADGUID": "Active Directory GUID"},
            "facets": {
                "employee_address_type": {
                    "AddressEmployeeText": {
                        "title": "Address (free-text)",
                        "scope": "TEXT",
                    }
                }
            },
        }
    }
    return mapping


@pytest.fixture()
def dataloader() -> AsyncMock:
    dataloader = AsyncMock()
    dataloader.load_mo_it_systems.return_value = {}
    return dataloader


@pytest.fixture()
def context(mapping: dict, dataloader: AsyncMock) -> dict:
    user_context = {"mapping": mapping, "dataloader": dataloader}
    return {"user_context": user_context}


@pytest.fixture()
def init_engine(context: dict) -> InitEngine:
    return InitEngine(context)


async def test_create_facets(dataloader: AsyncMock, init_engine: InitEngine):
    """
    Create a facet
    """
    dataloader.load_mo_facet.return_value = {}
    await init_engine.create_facets()

    dataloader.create_mo_class.assert_called_once()
    dataloader.create_mo_it_system.assert_not_called()


async def test_create_facets_facet_exists(
    dataloader: AsyncMock, init_engine: InitEngine
):
    """
    Try to create an existing facet. It should be skipped
    """
    class_uuid = str(uuid4())
    dataloader.load_mo_facet.return_value = {
        class_uuid: {
            "user_key": "AddressEmployeeText",
            "uuid": class_uuid,
            "name": "Address (free-text)",
            "scope": "TEXT",
        }
    }
    await init_engine.create_facets()

    dataloader.create_mo_class.assert_not_called()
    dataloader.create_mo_it_system.assert_not_called()


async def test_modify_facets(dataloader: AsyncMock, init_engine: InitEngine):
    """
    Try to update an existing facet.
    """
    class_uuid = str(uuid4())
    dataloader.load_mo_facet.return_value = {
        class_uuid: {
            "user_key": "AddressEmployeeText",
            "uuid": class_uuid,
            "name": "Address (free-text)",
            "scope": "ADDRESS",  # Scope is different here, so a class is updated
        }
    }
    await init_engine.create_facets()

    dataloader.create_mo_class.assert_not_called()
    dataloader.update_mo_class.assert_called_once()
    dataloader.create_mo_it_system.assert_not_called()


async def test_create_it_systems(dataloader: AsyncMock, init_engine: InitEngine):
    """
    Create an it-system
    """
    dataloader.load_mo_it_systems.return_value = {}
    await init_engine.create_it_systems()

    dataloader.create_mo_it_system.assert_called_once()
    dataloader.create_mo_class.assert_not_called()


async def test_create_it_systems_system_exists(
    dataloader: AsyncMock, init_engine: InitEngine
):
    """
    Try to create an existing it-system. It should be skipped
    """
    uuid = str(uuid4())
    dataloader.load_mo_it_systems.return_value = {
        uuid: {
            "user_key": "ADGUID",
            "uuid": uuid,
        }
    }
    await init_engine.create_it_systems()

    dataloader.create_mo_it_system.assert_not_called()
    dataloader.create_mo_class.assert_not_called()


async def test_empty_mapping(dataloader: AsyncMock, context: dict):
    """
    If mapping is empty or not specified at all, the init_engine should not crash.
    It should just do nothing.
    """
    context["user_context"]["mapping"] = {"init": {}}
    init_engine = InitEngine(context)
    await init_engine.create_it_systems()
    await init_engine.create_facets()

    context["user_context"]["mapping"] = {"init": {"it_systems": {}}}
    init_engine = InitEngine(context)
    await init_engine.create_it_systems()
    await init_engine.create_facets()

    context["user_context"]["mapping"] = {"init": {"facets": {}}}
    init_engine = InitEngine(context)
    await init_engine.create_it_systems()
    await init_engine.create_facets()

    dataloader.create_mo_it_system.assert_not_called()
    dataloader.create_mo_class.assert_not_called()
