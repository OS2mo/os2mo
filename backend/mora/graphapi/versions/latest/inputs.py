# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID
from uuid import uuid4

import pydantic
import strawberry
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from mora.db import events
from mora.graphapi.gmodels.mo import OpenValidity as RAOpenValidity
from mora.graphapi.gmodels.mo import Validity as RAValidity

from ...gmodels.mo._shared import UUIDBase
from .events import EventTokenType
from .events import ListenerFilter
from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressUpdate
from .models import AssociationCreate
from .models import AssociationTerminate
from .models import AssociationUpdate
from .models import ClassCreate
from .models import ClassTerminate
from .models import ClassUpdate
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .models import EngagementCreate
from .models import EngagementTerminate
from .models import EngagementUpdate
from .models import FacetCreate
from .models import FacetTerminate
from .models import FacetUpdate
from .models import ITAssociationCreate
from .models import ITAssociationTerminate
from .models import ITAssociationUpdate
from .models import ITSystemCreate
from .models import ITSystemTerminate
from .models import ITSystemUpdate
from .models import ITUserCreate
from .models import ITUserTerminate
from .models import ITUserUpdate
from .models import KLECreate
from .models import KLETerminate
from .models import KLEUpdate
from .models import LeaveCreate
from .models import LeaveTerminate
from .models import LeaveUpdate
from .models import ManagerCreate
from .models import ManagerTerminate
from .models import ManagerUpdate
from .models import Organisation
from .models import OrganisationUnitTerminate
from .models import OwnerCreate
from .models import OwnerTerminate
from .models import OwnerUpdate
from .models import RelatedUnitsUpdate
from .models import RoleBindingCreate
from .models import RoleBindingTerminate
from .models import RoleBindingUpdate
from .models import Validity
from .models import ValidityTerminate


def gen_uuid_unset(uuid: UUID | UnsetType | None) -> dict[str, str] | UnsetType | None:
    if uuid is UNSET:
        return UNSET
    if uuid is None:
        return None
    return {"uuid": str(uuid)}


def strip_unset(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not UNSET}


def strip_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def strip_none_and_unset(d: dict[str, Any]) -> dict[str, Any]:
    return strip_none(strip_unset(d))


def all_fields(model: Any) -> set[str]:
    return set(model.__fields__.keys())


# Various
# -------
@strawberry.experimental.pydantic.input(
    model=Validity,
    all_fields=True,
)
class ValidityInput:
    pass


@strawberry.experimental.pydantic.input(
    model=RAValidity,
    all_fields=True,
)
class RAValidityInput:
    pass


@strawberry.experimental.pydantic.input(
    model=RAOpenValidity,
    all_fields=True,
)
class RAOpenValidityInput:
    pass


def validity2dict(validity: Any) -> dict:
    def dt2diso_or_none(dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.date().isoformat()

    return {
        "from": dt2diso_or_none(validity.from_date),
        "to": dt2diso_or_none(validity.to_date),
    }


# Root Organisation
# -----------------
@strawberry.experimental.pydantic.input(
    model=Organisation,
    all_fields=True,
)
class OrganisationInput:
    """input model for terminating organisation units."""


# Addresses
# ---------
@strawberry.experimental.pydantic.input(
    model=AddressCreate, fields=list(all_fields(AddressCreate) - {"employee"})
)
class AddressCreateInput:
    """input model for creating addresses."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""


@strawberry.experimental.pydantic.input(
    model=AddressUpdate, fields=list(all_fields(AddressUpdate) - {"employee"})
)
class AddressUpdateInput:
    """input model for updating addresses."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


# Associations
# ------------
@strawberry.experimental.pydantic.input(
    model=AssociationCreate, fields=list(all_fields(AssociationCreate) - {"employee"})
)
class AssociationCreateInput:
    """input model for creating associations."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AssociationUpdate, fields=list(all_fields(AssociationUpdate) - {"employee"})
)
class AssociationUpdateInput:
    """input model for updating associations."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AssociationTerminate,
    all_fields=True,
)
class AssociationTerminateInput:
    """input model for terminating associations."""


# Classes
# ---------
@strawberry.experimental.pydantic.input(
    model=ClassCreate,
    all_fields=True,
)
class ClassCreateInput:
    """input model for creating a class."""


@strawberry.experimental.pydantic.input(
    model=ClassUpdate,
    all_fields=True,
)
class ClassUpdateInput:
    """input model for updating a class."""


@strawberry.experimental.pydantic.input(
    model=ClassTerminate,
    all_fields=True,
)
class ClassTerminateInput:
    """Input model for terminating a class."""


class ClassTerminateV18(UUIDBase):
    uuid: UUID = pydantic.Field(description="UUID for the class we want to terminate.")
    validity: ValidityTerminate = pydantic.Field(
        description="When to terminate the class"
    )


@strawberry.experimental.pydantic.input(
    name="ClassTerminateInput",
    model=ClassTerminateV18,
    all_fields=True,
)
class ClassTerminateInputV18:
    """Input model for terminating a class in version 18 or below."""


# Employees
# ---------
@strawberry.experimental.pydantic.input(
    model=EmployeeCreate,
    all_fields=True,
)
class EmployeeCreateInput:
    """Input model for creating an employee."""


@strawberry.experimental.pydantic.input(
    model=EmployeeUpdate,
    all_fields=True,
)
class EmployeeUpdateInput:
    """Input model for updating an employee."""


@strawberry.experimental.pydantic.input(
    model=EmployeeTerminate,
    all_fields=True,
)
class EmployeeTerminateInput:
    pass


# Engagements
# -----------
@strawberry.experimental.pydantic.input(
    model=EngagementTerminate,
    all_fields=True,
)
class EngagementTerminateInput:
    """input model for terminating Engagements."""


@strawberry.experimental.pydantic.input(
    model=EngagementCreate, fields=list(all_fields(EngagementCreate) - {"employee"})
)
class EngagementCreateInput:
    """input model for creating engagements."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=EngagementUpdate, fields=list(all_fields(EngagementUpdate) - {"employee"})
)
class EngagementUpdateInput:
    """input model for updating Engagements."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


# EngagementsAssociations
# -----------------------


# ITAssociations
# ---------
@strawberry.experimental.pydantic.input(
    model=ITAssociationCreate,
    all_fields=True,
)
class ITAssociationCreateInput:
    """input model for creating IT-associations."""


@strawberry.experimental.pydantic.input(
    model=ITAssociationUpdate,
    all_fields=True,
)
class ITAssociationUpdateInput:
    """input model for updating IT-associations."""


@strawberry.experimental.pydantic.input(
    model=ITAssociationTerminate,
    all_fields=True,
)
class ITAssociationTerminateInput:
    """input model for terminating IT-associations."""


# Facets
# ------
@strawberry.experimental.pydantic.input(
    model=FacetCreate,
    all_fields=True,
)
class FacetCreateInput:
    """Input model for creating a facet."""


@strawberry.experimental.pydantic.input(
    model=FacetUpdate,
    all_fields=True,
)
class FacetUpdateInput:
    """Input model for updating a facet."""


@strawberry.experimental.pydantic.input(
    model=FacetTerminate,
    all_fields=True,
)
class FacetTerminateInput:
    """Input model for terminating a facet."""


class FacetTerminateV18(UUIDBase):
    uuid: UUID = pydantic.Field(description="UUID for the facet we want to terminate.")
    validity: ValidityTerminate = pydantic.Field(
        description="When to terminate the facet"
    )


@strawberry.experimental.pydantic.input(
    name="FacetTerminateInput",
    model=FacetTerminateV18,
    all_fields=True,
)
class FacetTerminateInputV18:
    """Input model for terminating a facet in version 18 or below."""


# ITSystems
# ---------
@strawberry.experimental.pydantic.input(
    model=ITSystemCreate,
    all_fields=True,
)
class ITSystemCreateInput:
    """input model for creating ITSystems."""


@strawberry.experimental.pydantic.input(
    model=ITSystemUpdate,
    all_fields=True,
)
class ITSystemUpdateInput:
    """Input model for updating ITSystems."""


@strawberry.experimental.pydantic.input(
    model=ITSystemTerminate,
    all_fields=True,
)
class ITSystemTerminateInput:
    """Input model for terminating an ITSystem."""


class ITSystemTerminateV18(UUIDBase):
    uuid: UUID = pydantic.Field(
        description="UUID for the it-system we want to terminate."
    )
    validity: ValidityTerminate = pydantic.Field(
        description="When to terminate the ITSystem"
    )


@strawberry.experimental.pydantic.input(
    name="ITSystemTerminateInput",
    model=ITSystemTerminateV18,
    all_fields=True,
)
class ITSystemTerminateInputV18:
    """Input model for terminating an it system in version 18 or below."""


# ITUsers
# -------
@strawberry.experimental.pydantic.input(
    model=ITUserCreate,
    all_fields=True,
)
class ITUserCreateInput:
    """input model for creating IT-Users."""


@strawberry.experimental.pydantic.input(
    model=ITUserUpdate,
    all_fields=True,
)
class ITUserUpdateInput:
    """input model for creating IT-Users."""


@strawberry.experimental.pydantic.input(
    model=ITUserTerminate,
    all_fields=True,
)
class ITUserTerminateInput:
    """input model for terminating IT-user."""


# KLEs
# ----


@strawberry.experimental.pydantic.input(
    model=KLECreate,
    all_fields=True,
)
class KLECreateInput:
    """Input model for creating a KLE annotation."""


@strawberry.experimental.pydantic.input(
    model=KLEUpdate,
    all_fields=True,
)
class KLEUpdateInput:
    """Input model for updating a KLE annotation."""


@strawberry.experimental.pydantic.input(
    model=KLETerminate,
    all_fields=True,
)
class KLETerminateInput:
    """Input model for terminating a KLE annotation."""


# Leave
# -----
@strawberry.experimental.pydantic.input(
    model=LeaveCreate,
    all_fields=True,
)
class LeaveCreateInput:
    """Input model for creating a leave."""


@strawberry.experimental.pydantic.input(
    model=LeaveUpdate,
    all_fields=True,
)
class LeaveUpdateInput:
    """Input model for updating a leave."""


@strawberry.experimental.pydantic.input(
    model=LeaveTerminate,
    all_fields=True,
)
class LeaveTerminateInput:
    """Input model for terminating a leave."""


# Managers
# --------


@strawberry.experimental.pydantic.input(
    model=ManagerCreate,
    all_fields=True,
)
class ManagerCreateInput:
    """Input model for creating a manager."""


@strawberry.experimental.pydantic.input(
    model=ManagerUpdate,
    all_fields=True,
)
class ManagerUpdateInput:
    """Input model for updating a manager."""


@strawberry.experimental.pydantic.input(
    model=ManagerTerminate,
    all_fields=True,
)
class ManagerTerminateInput:
    """Input model for terminating a manager."""


# Organisational Units
# --------------------
@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganisationUnitTerminateInput:
    """Input model for terminating organisation units."""


@strawberry.input
class OrganisationUnitCreateInput:
    """Input model for creating organisation units."""

    uuid: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID to be created. Will be autogenerated if not specified."
        ),
    ] = UNSET

    validity: Annotated[
        RAValidityInput,
        strawberry.argument(description="Validity range for the org-unit."),
    ]

    name: Annotated[str, strawberry.argument(description="Org-unit name.")]
    user_key: Annotated[
        str | None, strawberry.argument(description="Extra info or uuid.")
    ] = UNSET
    parent: Annotated[
        UUID | None,
        strawberry.argument(description="UUID of the related parent."),
    ] = UNSET
    org_unit_type: Annotated[UUID, strawberry.argument(description="UUID of the type.")]
    time_planning: Annotated[
        UUID | None, strawberry.argument(description="UUID of time planning.")
    ] = UNSET
    org_unit_level: Annotated[
        UUID | None, strawberry.argument(description="UUID of unit level.")
    ] = UNSET
    org_unit_hierarchy: Annotated[
        UUID | None, strawberry.argument(description="UUID of the unit hierarchy.")
    ] = UNSET

    def to_handler_dict(self) -> dict:
        # Set UUID if not set
        # TODO: Should use a default_factory once strawberry supports it
        self.uuid = self.uuid or uuid4()
        if self.user_key is None or self.user_key is UNSET:
            self.user_key = str(self.uuid)

        data_dict: dict = {
            "uuid": self.uuid,
            "name": self.name,
            "user_key": self.user_key,
            "time_planning": gen_uuid_unset(self.time_planning),
            "parent": gen_uuid_unset(self.parent),
            "org_unit_type": gen_uuid_unset(self.org_unit_type),
            "org_unit_level": gen_uuid_unset(self.org_unit_level),
            "org_unit_hierarchy": gen_uuid_unset(self.org_unit_hierarchy),
            "details": [],
            "validity": validity2dict(self.validity),
        }
        return strip_none_and_unset(data_dict)


@strawberry.input
class OrganisationUnitUpdateInput:
    """Input model for updating organisation units."""

    uuid: Annotated[
        UUID,
        strawberry.argument(description="UUID of the organisation unit to be updated."),
    ]

    validity: Annotated[
        RAValidityInput,
        strawberry.argument(
            description="Validity range for the organisation unit to be updated."
        ),
    ]

    name: Annotated[
        str | None,
        strawberry.argument(description="Name of the organisation unit to be updated."),
    ] = UNSET

    user_key: Annotated[
        str | None, strawberry.argument(description="Extra info or uuid.")
    ] = UNSET

    parent: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID of the organisation units related parent to be updated."
        ),
    ] = UNSET

    org_unit_type: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID of the organisation units type to be updated."
        ),
    ] = UNSET

    org_unit_level: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID of the organisation units level to be updated."
        ),
    ] = UNSET

    org_unit_hierarchy: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID of organisation units hierarchy to be updated."
        ),
    ] = UNSET

    time_planning: Annotated[
        UUID | None,
        strawberry.argument(
            description="UUID of organisation units time planning to be updated."
        ),
    ] = UNSET

    def to_handler_dict(self) -> dict:
        data_dict: dict = {
            "uuid": self.uuid,
            "name": self.name,
            "user_key": self.user_key,
            "parent": gen_uuid_unset(self.parent),
            "org_unit_type": gen_uuid_unset(self.org_unit_type),
            "org_unit_level": gen_uuid_unset(self.org_unit_level),
            "org_unit_hierarchy": gen_uuid_unset(self.org_unit_hierarchy),
            "time_planning": gen_uuid_unset(self.time_planning),
            "validity": validity2dict(self.validity),
        }
        return strip_unset(data_dict)


# Owners
# -----
@strawberry.experimental.pydantic.input(
    model=OwnerCreate,
    all_fields=True,
)
class OwnerCreateInput:
    """Input model for creating owners."""


@strawberry.experimental.pydantic.input(
    model=OwnerUpdate,
    all_fields=True,
)
class OwnerUpdateInput:
    """Input model for updating owners."""


@strawberry.experimental.pydantic.input(
    model=OwnerTerminate,
    all_fields=True,
)
class OwnerTerminateInput:
    """Input model for terminating owners."""


# Related Units
# -------------


@strawberry.experimental.pydantic.input(
    model=RelatedUnitsUpdate,
    all_fields=True,
)
class RelatedUnitsUpdateInput:
    """Input model for creating related_units."""


# Roles
# -----
@strawberry.experimental.pydantic.input(
    model=RoleBindingCreate,
    all_fields=True,
)
class RoleBindingCreateInput:
    """Input model for creating roles."""


@strawberry.experimental.pydantic.input(
    model=RoleBindingUpdate,
    all_fields=True,
)
class RoleBindingUpdateInput:
    """Input model for updating roles."""


@strawberry.experimental.pydantic.input(
    model=RoleBindingTerminate,
    all_fields=True,
)
class RoleBindingTerminateInput:
    """Input model for terminating roles."""


# Health
# ------

# Files
# -----


# Event system
# ------------


@strawberry.input(description="Create a namespace.")
class NamespaceCreateInput:
    name: str = strawberry.field(
        description="Name of the namespace. This is also the identifier for namespaces."
    )
    public: bool = strawberry.field(
        default=False, description="Can others create listeners in the namespace?"
    )


@strawberry.input(description="Delete a namespace.")
class NamespaceDeleteInput:
    name: str = strawberry.field(description="Name of namespace to delete")


@strawberry.input(description="Create a listener.")
class ListenerCreateInput:
    namespace: str = strawberry.field(
        default="mo",
        description='Namespace of listener. Defaults to "mo", which means you will get events from os2mo.',
    )
    user_key: str = strawberry.field(description="User key of listener.")
    routing_key: str = strawberry.field(description="Routing key of listener.")


@strawberry.input(description="Delete a listener.")
class ListenerDeleteInput:
    uuid: UUID = strawberry.field(description="Listener ID to delete.")
    delete_pending_events: bool = strawberry.field(
        default=False,
        description="Delete all events awaiting acknowledgement for this listener.",
    )


@strawberry.input(description="Acknowledge an event.")
class EventAcknowledgeInput:
    token: EventTokenType


@strawberry.input
class EventSendInput:
    namespace: str = strawberry.field(description="Namespace to send the event in.")
    routing_key: str = strawberry.field(description="Routing key of the event.")
    subject: str = strawberry.field(description="Subject the event is about.")
    priority: int = strawberry.field(
        default=events.DEFAULT_PRIORITY,
        description="Priority of the event. 1 is the highest priority.",
    )


@strawberry.input(
    description=dedent(
        """\
        Silence an event.

        Silenced events are not received with `event_fetch`.
        """
    ),
)
class EventSilenceInput:
    listeners: ListenerFilter = strawberry.field(
        description="Only silence the event for these listeners."
    )
    subjects: list[str] = strawberry.field(description="Subjects to silence.")


@strawberry.input(description="Unsilence all matching events.")
class EventUnsilenceInput:
    listeners: ListenerFilter | None = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None
