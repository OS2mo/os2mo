# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import structlog
from pydantic import parse_obj_as

from .config import Init

logger = structlog.stdlib.get_logger()


class InitEngine:
    def __init__(self, context):
        user_context = context["user_context"]
        self.init_mapping = parse_obj_as(Init, user_context["mapping"].get("init", {}))
        self.dataloader = user_context["dataloader"]

    async def create_facets(self):
        facet_mapping = self.init_mapping.facets

        # Loop over facet user_keys. For example "employee_address_type"
        for facet_user_key, class_mapping in facet_mapping.items():
            logger.info("Creating facet", user_key=facet_user_key)

            facet_info = await self.dataloader.load_mo_facet(facet_user_key)
            facet_uuid = await self.dataloader.load_mo_facet_uuid(facet_user_key)
            existing_classes = {f["user_key"]: f for f in facet_info.values()}

            # Loop over class user_keys. For example "EmailEmployee"
            for class_user_key, class_details in class_mapping.items():
                if class_user_key in existing_classes:
                    existing_class = existing_classes[class_user_key]
                    current_title = existing_class["name"]
                    current_scope = existing_class["scope"]
                    if (
                        class_details.title == current_title
                        and class_details.scope == current_scope
                    ):
                        logger.info("Class exists", user_key=class_user_key)
                        continue
                    else:
                        await self.dataloader.update_mo_class(
                            name=class_details.title,
                            user_key=class_user_key,
                            facet_uuid=facet_uuid,
                            class_uuid=existing_class["uuid"],
                            scope=class_details.scope,
                        )

                else:
                    await self.dataloader.create_mo_class(
                        name=class_details.title,
                        user_key=class_user_key,
                        facet_uuid=facet_uuid,
                        scope=class_details.scope,
                    )

    async def create_it_systems(self):
        logger.info("Creating it systems")
        it_system_mapping = self.init_mapping.it_systems

        it_system_info = await self.dataloader.load_mo_it_systems()

        existing_it_systems = [i["user_key"] for i in it_system_info.values()]

        for it_system_user_key, it_system_name in it_system_mapping.items():
            if it_system_user_key in existing_it_systems:
                logger.info("IT-system exists", user_key=it_system_user_key)
                continue
            else:
                await self.dataloader.create_mo_it_system(
                    name=it_system_name,
                    user_key=it_system_user_key,
                )
