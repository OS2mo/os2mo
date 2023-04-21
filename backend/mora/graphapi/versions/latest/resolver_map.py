from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .resolvers import EmployeeResolver
from .resolvers import EngagementAssociationResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import ITSystemResolver
from .resolvers import ITUserResolver
from .resolvers import KLEResolver
from .resolvers import LeaveResolver
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import RelatedUnitResolver
from .resolvers import RoleResolver
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Employee
from .schema import Engagement
from .schema import EngagementAssociation
from .schema import Facet
from .schema import ITSystem
from .schema import ITUser
from .schema import KLE
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import RelatedUnit
from .schema import Role


resolver_map = {
    AddressResolver: Address,
    AssociationResolver: Association,
    ClassResolver: Class,
    EmployeeResolver: Employee,
    EngagementResolver: Engagement,
    EngagementAssociationResolver: EngagementAssociation,
    FacetResolver: Facet,
    ITSystemResolver: ITSystem,
    ITUserResolver: ITUser,
    KLEResolver: KLE,
    LeaveResolver: Leave,
    ManagerResolver: Manager,
    OrganisationUnitResolver: OrganisationUnit,
    RelatedUnitResolver: RelatedUnit,
    RoleResolver: Role,
}
