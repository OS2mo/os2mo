# -*- coding: utf-8 -*-
from .logging import logger


class InitEngine:
    def __init__(self, context):
        user_context = context["user_context"]
        self.mapping = user_context["mapping"]
        self.dataloader = user_context["dataloader"]

    def create_facets(self):
        facet_mapping = self.mapping.get("init", {}).get("facets", {})

        # Loop over facet user_keys. For example "employee_address_type"
        for facet_user_key, class_mapping in facet_mapping.items():
            logger.info(f"[init] Creating facets with user_key = {facet_user_key}")

            facet_info = self.dataloader.load_mo_facet(facet_user_key)
            facet_uuid = self.dataloader.load_mo_facet_uuid(facet_user_key)
            existing_classes = {f["user_key"]: f for f in facet_info.values()}

            # Loop over class user_keys. For example "EmailEmployee"
            for class_user_key, class_details in class_mapping.items():
                if class_user_key in existing_classes:
                    existing_class = existing_classes[class_user_key]
                    current_title = existing_class["name"]
                    current_scope = existing_class["scope"]
                    if (
                        class_details["title"] == current_title
                        and class_details["scope"] == current_scope
                    ):
                        logger.info(f"[init] '{class_user_key}' class exists.")
                        continue
                    else:
                        self.dataloader.update_mo_class(
                            name=class_details["title"],
                            user_key=class_user_key,
                            facet_uuid=facet_uuid,
                            class_uuid=existing_class["uuid"],
                            scope=class_details["scope"],
                        )

                else:
                    self.dataloader.create_mo_class(
                        name=class_details["title"],
                        user_key=class_user_key,
                        facet_uuid=facet_uuid,
                        scope=class_details["scope"],
                    )

    def create_it_systems(self):
        logger.info("[init] Creating it systems")
        it_system_mapping = self.mapping.get("init", {}).get("it_systems", {})
        it_system_info = self.dataloader.load_mo_it_systems()

        existing_it_systems = [i["user_key"] for i in it_system_info.values()]

        for it_system_user_key, it_system_name in it_system_mapping.items():
            if it_system_user_key in existing_it_systems:
                logger.info(
                    f"[init] '{it_system_user_key}' IT-system exists. Moving on."
                )
                continue
            else:
                self.dataloader.create_mo_it_system(
                    name=it_system_name,
                    user_key=it_system_user_key,
                )
