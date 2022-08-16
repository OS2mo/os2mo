#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ._shared import get_relations
from ._shared import ITSystemAttributes
from ._shared import ITSystemProperties
from ._shared import ITSystemRelations
from ._shared import ITSystemStates
from ._shared import ITSystemValidState
from ._shared import LoraBase


# --------------------------------------------------------------------------------------
# Organisation model
# --------------------------------------------------------------------------------------


class ITSystem(LoraBase):
    """A LoRa ITSystem"""

    attributes: ITSystemAttributes = Field(
        alias="attributter", description="The ITSystem attributes."
    )
    states: ITSystemStates = Field(
        alias="tilstande", description="The ITSystem states."
    )

    note: Optional[str] = Field(description="Note describing the ITSystem.")
    relations: Optional[ITSystemRelations] = Field(
        alias="relationer", description="The ITSystem relations."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        # State
        state: str,
        # Properties
        user_key: str,  # often == name,
        #  UUID of the ITSys model. Auto-created if not set
        uuid: Optional[UUID] = None,
        name: Optional[str] = None,
        note: Optional[str] = None,
        type: Optional[str] = None,
        configuration_ref: Optional[List[str]] = None,
        # Relation
        belongs_to: Optional[UUID] = None,
        affiliated_orgs: Optional[List[UUID]] = None,
        affiliated_units: Optional[List[UUID]] = None,
        affiliated_functions: Optional[List[UUID]] = None,
        affiliated_users: Optional[List[UUID]] = None,
        affiliated_interests: Optional[List[UUID]] = None,
        affiliated_itsystems: Optional[List[UUID]] = None,
        affiliated_persons: Optional[List[UUID]] = None,
        addresses: Optional[List[UUID]] = None,
        system_types: Optional[List[UUID]] = None,
        tasks: Optional[List[UUID]] = None,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "ITSystem":
        "Create an ITSystem from simplified fields."
        # Inner fields
        _effective_time = EffectiveTime(from_date=from_date, to_date=to_date)
        _properties = ITSystemProperties(
            user_key=user_key,
            effective_time=_effective_time,
            name=name,
            type=type,
            configuration_ref=configuration_ref,
        )
        _state = ITSystemValidState(state=state, effective_time=_effective_time)

        attributes = ITSystemAttributes(properties=[_properties])
        states = ITSystemStates(valid_state=[_state])
        relations = ITSystemRelations(
            belongs_to=get_relations(belongs_to, _effective_time),
            affiliated_orgs=get_relations(affiliated_orgs, _effective_time),
            affiliated_units=get_relations(affiliated_units, _effective_time),
            affiliated_functions=get_relations(affiliated_functions, _effective_time),
            affiliated_users=get_relations(affiliated_users, _effective_time),
            affiliated_interests=get_relations(affiliated_interests, _effective_time),
            affiliated_itsystems=get_relations(affiliated_itsystems, _effective_time),
            affiliated_persons=get_relations(affiliated_persons, _effective_time),
            addresses=get_relations(addresses, _effective_time),
            system_types=get_relations(system_types, _effective_time),
            tasks=get_relations(tasks, _effective_time),
        )

        return cls(
            note=note,
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
