# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID
from uuid import uuid4

import strawberry
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from mora.db import events
from mora.graphapi.gmodels.mo import OpenValidity as RAOpenValidity
from mora.graphapi.gmodels.mo import Validity as RAValidity

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
from .policies import PolicyActorKind


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
@strawberry.experimental.pydantic.input(model=AddressCreate)
class AddressCreateInput:
    """input model for creating addresses."""

    uuid: strawberry.auto
    org_unit: strawberry.auto
    person: strawberry.auto
    engagement: strawberry.auto
    ituser: strawberry.auto
    visibility: strawberry.auto
    validity: strawberry.auto
    user_key: strawberry.auto
    value: strawberry.auto
    address_type: strawberry.auto
    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""


@strawberry.experimental.pydantic.input(model=AddressUpdate)
class AddressUpdateInput:
    """input model for updating addresses."""

    uuid: strawberry.auto
    org_unit: strawberry.auto
    person: strawberry.auto
    engagement: strawberry.auto
    ituser: strawberry.auto
    visibility: strawberry.auto
    validity: strawberry.auto
    user_key: strawberry.auto
    value: strawberry.auto
    address_type: strawberry.auto
    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


# Associations
# ------------
@strawberry.experimental.pydantic.input(model=AssociationCreate)
class AssociationCreateInput:
    """input model for creating associations."""

    uuid: strawberry.auto
    user_key: strawberry.auto
    primary: strawberry.auto
    validity: strawberry.auto
    person: strawberry.auto
    substitute: strawberry.auto
    trade_union: strawberry.auto
    org_unit: strawberry.auto
    association_type: strawberry.auto
    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(model=AssociationUpdate)
class AssociationUpdateInput:
    """input model for updating associations."""

    uuid: strawberry.auto
    user_key: strawberry.auto
    primary: strawberry.auto
    validity: strawberry.auto
    person: strawberry.auto
    substitute: strawberry.auto
    trade_union: strawberry.auto
    org_unit: strawberry.auto
    association_type: strawberry.auto
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


@strawberry.experimental.pydantic.input(model=EngagementCreate)
class EngagementCreateInput:
    """input model for creating engagements."""

    uuid: strawberry.auto
    user_key: strawberry.auto
    primary: strawberry.auto
    validity: strawberry.auto
    fraction: strawberry.auto
    extension_1: strawberry.auto
    extension_2: strawberry.auto
    extension_3: strawberry.auto
    extension_4: strawberry.auto
    extension_5: strawberry.auto
    extension_6: strawberry.auto
    extension_7: strawberry.auto
    extension_8: strawberry.auto
    extension_9: strawberry.auto
    extension_10: strawberry.auto
    person: strawberry.auto
    org_unit: strawberry.auto
    engagement_type: strawberry.auto
    job_function: strawberry.auto
    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(model=EngagementUpdate)
class EngagementUpdateInput:
    """input model for updating Engagements."""

    uuid: strawberry.auto
    user_key: strawberry.auto
    primary: strawberry.auto
    validity: strawberry.auto
    fraction: strawberry.auto
    extension_1: strawberry.auto
    extension_2: strawberry.auto
    extension_3: strawberry.auto
    extension_4: strawberry.auto
    extension_5: strawberry.auto
    extension_6: strawberry.auto
    extension_7: strawberry.auto
    extension_8: strawberry.auto
    extension_9: strawberry.auto
    extension_10: strawberry.auto
    person: strawberry.auto
    org_unit: strawberry.auto
    engagement_type: strawberry.auto
    job_function: strawberry.auto
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


@strawberry.input
class ManagerUpdateInput:
    """Input model for updating a manager."""

    uuid: UUID
    validity: RAValidityInput

    user_key: str | None = None
    person: UUID | None = None
    engagement: UUID | None = UNSET
    responsibility: list[UUID] | None = None
    org_unit: UUID | None = None
    manager_type: UUID | None = None
    manager_level: UUID | None = None

    def to_pydantic(self) -> ManagerUpdate:
        kwargs = {
            "uuid": self.uuid,
            "validity": self.validity.to_pydantic(),
            "user_key": self.user_key,
            "person": self.person,
            "responsibility": self.responsibility,
            "org_unit": self.org_unit,
            "manager_type": self.manager_type,
            "manager_level": self.manager_level,
        }

        # ONLY engagement is passed conditionally to support PATCH semantics
        if self.engagement is not UNSET:
            kwargs["engagement"] = self.engagement

        return ManagerUpdate(**kwargs)


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

        Silencing does not affect delivery, it only affects whether alerts are triggered.
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


@strawberry.input(description="Rerun all matching events.")
class EventRerunInput:
    listeners: ListenerFilter | None = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None
    silenced: bool | None = None


# Policies
# --------


@strawberry.input(
    description=dedent(
        """\
        Declare a policy.

        Describes the state a policy should have (`name`, `description` and
        whether it is `activated`).

        Omit `uuid` to create a new policy. Supply `uuid` to update the existing
        policy with that ID.
        """
    )
)
class PolicyDeclareInput:
    uuid: UUID | None = strawberry.field(
        default=None,
        description="UUID of the policy to update. Omit to create a new policy.",
    )
    name: str = strawberry.field(description="Name of the policy.")
    description: str | None = strawberry.field(
        default=None, description="Description of the policy."
    )
    activated: bool = strawberry.field(
        default=True,
        description="Whether the policy is in effect. Defaults to true.",
    )


@strawberry.input(description="Delete a policy.")
class PolicyDeleteInput:
    uuid: UUID = strawberry.field(description="UUID of the policy to delete.")


@strawberry.input(
    description="Declare (idempotently ensure) a single actor on a policy."
)
class PolicyActorDeclareInput:
    policy: UUID = strawberry.field(
        description="UUID of the policy to declare the actor on."
    )
    kind: PolicyActorKind = strawberry.field(
        description="The kind of attribute to match on."
    )
    value: str = strawberry.field(description="The value the attribute must equal.")


@strawberry.input(description="A single actor entry.")
class PolicyActorEntryInput:
    kind: PolicyActorKind = strawberry.field(
        description="The kind of attribute to match on."
    )
    value: str = strawberry.field(description="The value the attribute must equal.")


@strawberry.input(
    description="Declare (idempotently ensure) a set of actors on a policy."
)
class PolicyActorsDeclareInput:
    policy: UUID = strawberry.field(
        description="UUID of the policy to declare the actors on."
    )
    actors: list[PolicyActorEntryInput] = strawberry.field(
        description="The actors to declare on the policy."
    )


@strawberry.input(description="Delete an actor from a policy.")
class PolicyActorDeleteInput:
    uuid: UUID = strawberry.field(description="UUID of the actor binding to delete.")


@strawberry.input(
    description="Declare (idempotently ensure) a single rule on a policy."
)
class PolicyRuleDeclareInput:
    policy: UUID = strawberry.field(
        description="UUID of the policy to declare the rule on."
    )
    type: str = strawberry.field(
        description='GraphQL type the rule grants access to (or "Query"/"Mutation").'
    )
    field: str = strawberry.field(
        description='Field/mutator on the type, or "*" for all fields.'
    )
    condition: str | None = strawberry.field(
        default=None,
        description=(
            "Optional CEL condition that must evaluate true for the rule to "
            "grant access. Omit or leave null for an unconditional rule."
        ),
    )
    filter: str | None = strawberry.field(
        default=None,
        description=(
            "Optional CEL expression returning one or more access-check specs "
            "`{collection, filter, check, field}`; the rule only grants when all "
            "of them pass. Omit or leave null for no entity restriction."
        ),
    )


@strawberry.input(description="A single rule entry.")
class PolicyRuleEntryInput:
    type: str = strawberry.field(
        description='GraphQL type the rule grants access to (or "Query"/"Mutation").'
    )
    field: str = strawberry.field(
        description='Field/mutator on the type, or "*" for all fields.'
    )
    condition: str | None = strawberry.field(
        default=None,
        description=(
            "Optional CEL condition that must evaluate true for the rule to "
            "grant access. Omit or leave null for an unconditional rule."
        ),
    )
    filter: str | None = strawberry.field(
        default=None,
        description=(
            "Optional CEL expression returning one or more access-check specs "
            "`{collection, filter, check, field}`; the rule only grants when all "
            "of them pass. Omit or leave null for no entity restriction."
        ),
    )


@strawberry.input(
    description="Declare (idempotently ensure) a set of rules on a policy."
)
class PolicyRulesDeclareInput:
    policy: UUID = strawberry.field(
        description="UUID of the policy to declare the rules on."
    )
    rules: list[PolicyRuleEntryInput] = strawberry.field(
        description="The rules to declare on the policy."
    )


@strawberry.input(description="Delete a rule from a policy.")
class PolicyRuleDeleteInput:
    uuid: UUID = strawberry.field(description="UUID of the rule to delete.")
