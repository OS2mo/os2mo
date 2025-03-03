# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from functools import partial
from math import inf
from typing import Any
from uuid import UUID

from structlog import get_logger

from ... import mapping
from ... import util
from ...common import get_connector
from ...common import parse_owner_inference_priority_str
from ...exceptions import ErrorCodes
from ...graphapi.middleware import is_graphql
from ...mapping import EXTENSION_1
from ...mapping import PRIMARY
from ...mapping import OwnerInferencePriority
from ...service import employee
from ...service import orgunit
from ...service.facet import get_sorted_primary_class_list
from ...util import get_uuid
from ...util import get_valid_from
from .. import reading
from .association import AssociationReader
from .engagement import EngagementReader

ROLE_TYPE = mapping.OWNER

logger = get_logger()


@reading.register(ROLE_TYPE)
class OwnerReader(reading.OrgFunkReadingHandler):
    function_key = mapping.OWNER

    @classmethod
    async def get_from_type(
        cls,
        c,
        type,
        object_id,
        inherit_owner: bool = False,
    ):
        if inherit_owner or util.get_args_flag("inherit_owner"):
            return await cls.get_inherited_owner(c, type, object_id)

        return await super().get_from_type(c, type, object_id)

    @classmethod
    async def get_inherited_owner(cls, c, type, object_id):
        search_fields = {cls.SEARCH_FIELDS[type]: object_id}

        owner = list(await super().get(c, search_fields))

        if owner:
            return owner

        only_primary_uuid = util.get_args_flag("only_primary_uuid")
        ou = await orgunit.get_one_orgunit(
            c,
            object_id,
            details=orgunit.UnitDetails.FULL,
            only_primary_uuid=only_primary_uuid,
        )
        try:
            parent_id = ou[mapping.PARENT][mapping.UUID]
        except (TypeError, KeyError):
            return owner

        return await cls.get_inherited_owner(c, type, parent_id)

    @staticmethod
    def __owner_priority(
        obj: dict[str, Any], primary_priorities: dict[str, int]
    ) -> tuple[int, float, str]:
        """
        strict ordering between objects with scope-based priority
        :param obj: An appropriate MO-obj
        :param primary_priorities: Mapping from "primary-class-uuid" to "priority-int"
        :return: Tuple, ready for comparison with other tuples from this function
        """

        # use scope if possible
        scope_uuid = obj.get(PRIMARY, {}).get(mapping.UUID, None)
        scope_priority = -inf
        if primary_priorities:
            scope_priority = primary_priorities[scope_uuid]

        # break ties with from, older is better
        start = get_valid_from(obj).timestamp()

        # Finally, break ties with UUID, ALWAYS works
        uuid = get_uuid(obj)
        return scope_priority, start, uuid

    @staticmethod
    async def get_relation_candidates(
        owned_person_uuid: UUID, inference_priority: OwnerInferencePriority
    ) -> list[dict[str, Any]]:
        if inference_priority is OwnerInferencePriority.engagement:
            return list(
                await EngagementReader.get(
                    c=get_connector(),
                    search_fields={"tilknyttedebrugere": owned_person_uuid},
                )
            )
        if inference_priority is OwnerInferencePriority.association:
            return await AssociationReader.get(
                c=get_connector(),
                search_fields={"tilknyttedebrugere": owned_person_uuid},
            )
        # coverage: pause
        raise NotImplementedError(
            f"Mapping for inference_priority missing: {inference_priority}"
        )
        # coverage: unpause

    @classmethod
    async def infer_owner(
        cls,
        owned_person_uuid: UUID,
        inference_priority: OwnerInferencePriority,
    ) -> Awaitable[dict[str, Any]] | None:
        candidates = await cls.get_relation_candidates(
            owned_person_uuid=owned_person_uuid,
            inference_priority=inference_priority,
        )

        if not candidates:  # pragma: no cover
            # nothing to do
            return None
        elif len(candidates) > 1:  # sort if multiple
            priorities = dict(await get_sorted_primary_class_list(c=get_connector()))
            sort_func = partial(cls.__owner_priority, primary_priorities=priorities)
            best_candidate = max(candidates, key=sort_func)
        else:  # pragma: no cover
            # nothing to infer
            best_candidate = candidates[0]

        # we have a candidate, so look at owner of candidate's org_unit
        org_unit_owners = await OwnerReader.get_from_type(
            c=get_connector(),
            type="ou",
            object_id=util.get_mapping_uuid(
                best_candidate, mapping.ORG_UNIT, required=True
            ),
            inherit_owner=True,
        )
        # even when inheriting, no owners can be found
        if not org_unit_owners:  # pragma: no cover
            return None
        return org_unit_owners[0]["owner"]

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        owned_person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        owner_uuid = mapping.EMPLOYEE_PERSON_FIELD.get_uuid(effect)
        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        inference_priority_str = extensions.get(EXTENSION_1, None)
        inference_priority = None
        if inference_priority_str:  # filters both None and empty string
            inference_priority = parse_owner_inference_priority_str(
                inference_priority_str
            )
        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        if is_graphql():
            return {
                **base_obj,
                "owner_uuid": owner_uuid,
                "employee_uuid": owned_person,
                "org_unit_uuid": org_unit,
                "owner_inference_priority": inference_priority_str,
            }

        func: dict[Any, Any] = {
            **base_obj,
            mapping.OWNER_INFERENCE_PRIORITY: inference_priority.value
            if inference_priority is not None
            else None,
            mapping.OWNER: None,
            mapping.ORG_UNIT: None,
            mapping.PERSON: None,
        }

        if inference_priority:
            if owned_person:
                func[mapping.OWNER] = await cls.infer_owner(
                    owned_person_uuid=owned_person,
                    inference_priority=inference_priority,
                )
            else:  # pragma: no cover
                ErrorCodes.E_INTERNAL_ERROR(
                    f"ill-formatted object encountered: {effect}"
                )
        elif owner_uuid:
            func[mapping.OWNER] = await employee.request_bulked_get_one_employee(
                owner_uuid, only_primary_uuid=only_primary_uuid
            )

        if org_unit:
            func[mapping.ORG_UNIT] = await orgunit.request_bulked_get_one_orgunit(
                org_unit,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )

        if owned_person:
            func[mapping.PERSON] = await employee.request_bulked_get_one_employee(
                str(owned_person), only_primary_uuid=only_primary_uuid
            )

        return func
