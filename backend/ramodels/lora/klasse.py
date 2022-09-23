# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ._shared import FacetRef
from ._shared import KlasseAttributes
from ._shared import KlasseProperties
from ._shared import KlasseRelations
from ._shared import KlasseStates
from ._shared import LoraBase
from ._shared import Published
from ._shared import RegistrationTime
from ._shared import Responsible


class Klasse(LoraBase):
    """
    A LoRa klasse.
    """

    attributes: KlasseAttributes = Field(
        alias="attributter", description="The klasse attributes."
    )
    states: KlasseStates = Field(alias="tilstande", description="The klasse states.")
    relations: KlasseRelations = Field(
        alias="relationer", description="The klasse relations."
    )
    note: str | None = Field(description="Optional note.")

    @classmethod
    def from_simplified_fields(
        cls,
        facet_uuid: UUID,  # uuid
        user_key: str,  # rarely used
        organisation_uuid: UUID,
        title: str,
        uuid: UUID | None = None,
        scope: str | None = None,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "Klasse":
        "Create a Klasse from simplified fields."
        # Inner fields
        _effective_time = EffectiveTime(from_date=from_date, to_date=to_date)
        _properties = KlasseProperties(
            user_key=user_key,
            title=title,
            scope=scope,
            effective_time=_effective_time,
        )
        _published = Published(effective_time=_effective_time)
        _responsible = Responsible(
            uuid=organisation_uuid,
            effective_time=_effective_time,
        )
        _facet = FacetRef(
            uuid=facet_uuid,
            effective_time=_effective_time,
        )

        # Klasse fields
        attributes = KlasseAttributes(properties=[_properties])
        states = KlasseStates(published_state=[_published])
        relations = KlasseRelations(responsible=[_responsible], facet=[_facet])

        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )


class KlasseRead(Klasse):
    from_time: RegistrationTime = Field(
        alias="fratidspunkt", description="The klasse registration from time."
    )
    to_time: RegistrationTime = Field(
        alias="tiltidspunkt", description="The klasse registration to time."
    )
    life_cycle_code: str = Field(
        alias="livscykluskode", description="The klasse registation life cycle code."
    )
    user_ref: UUID = Field(
        alias="brugerref", description="The klasse registration user."
    )
