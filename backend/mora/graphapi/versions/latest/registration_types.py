# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry
from .schema import KLE, Association, Employee, Engagement, Facet, ITUser, Leave, Manager, OrganisationUnit, Owner, RelatedUnit
from .schema import ITSystem
from .schema import RoleBinding
from .schema import Class
from .model_registration import ModelRegistration


# These concrete classes must be instantiated explicitly so they can be added to the
# `types` parameter on `CustomSchema` within `schema.py` as strawberry otherwise has no
# way to discover which instantiations of `ModelRegistration` may exist and thus cannot
# construct the schema statically.


@strawberry.type
class AddressRegistration(ModelRegistration[Facet]):
    pass


@strawberry.type
class AssociationRegistration(ModelRegistration[Association]):
    pass


@strawberry.type
class ClassRegistration(ModelRegistration[Class]):
    pass


@strawberry.type
class PersonRegistration(ModelRegistration[Employee]):
    pass


@strawberry.type
class EngagementRegistration(ModelRegistration[Engagement]):
    pass


@strawberry.type
class FacetRegistration(ModelRegistration[Facet]):
    pass


@strawberry.type
class ITSystemRegistration(ModelRegistration[ITSystem]):
    pass


@strawberry.type
class ITUserRegistration(ModelRegistration[ITUser]):
    pass


@strawberry.type
class KLERegistration(ModelRegistration[KLE]):
    pass


@strawberry.type
class LeaveRegistration(ModelRegistration[Leave]):
    pass


@strawberry.type
class ManagerRegistration(ModelRegistration[Manager]):
    pass


@strawberry.type
class OwnerRegistration(ModelRegistration[Owner]):
    pass


@strawberry.type
class OrganisationUnitRegistration(ModelRegistration[OrganisationUnit]):
    pass


@strawberry.type
class RelatedUnitRegistration(ModelRegistration[RelatedUnit]):
    pass


@strawberry.type
class RoleBindingRegistration(ModelRegistration[RoleBinding]):
    pass
