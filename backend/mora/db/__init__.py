# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# flake8: noqa
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from ._amqp import AMQPSubsystem
from ._bruger import Bruger
from ._bruger import BrugerAttrEgenskaber
from ._bruger import BrugerAttrUdvidelser
from ._bruger import BrugerRegistrering
from ._bruger import BrugerRelation
from ._bruger import BrugerRelationKode
from ._bruger import BrugerTilsGyldighed
from ._common import Gyldighed
from ._common import PubliceretStatus
from ._facet import Facet
from ._facet import FacetAttrEgenskaber
from ._facet import FacetRegistrering
from ._facet import FacetRelation
from ._facet import FacetRelationKode
from ._facet import FacetTilsPubliceret
from ._itsystem import ITSystem
from ._itsystem import ITSystemAttrEgenskaber
from ._itsystem import ITSystemRegistrering
from ._itsystem import ITSystemRelation
from ._itsystem import ITSystemRelationKode
from ._itsystem import ITSystemTilsGyldighed
from ._klasse import Klasse
from ._klasse import KlasseAttrEgenskaber
from ._klasse import KlasseRegistrering
from ._klasse import KlasseRelation
from ._klasse import KlasseRelationKode
from ._klasse import KlasseTilsPubliceret
from ._organisation import Organisation
from ._organisation import OrganisationAttrEgenskaber
from ._organisation import OrganisationRegistrering
from ._organisation import OrganisationRelation
from ._organisation import OrganisationRelationKode
from ._organisation import OrganisationTilsGyldighed
from ._organisationsenhed import OrganisationEnhed
from ._organisationsenhed import OrganisationEnhedAttrEgenskaber
from ._organisationsenhed import OrganisationEnhedRegistrering
from ._organisationsenhed import OrganisationEnhedRelation
from ._organisationsenhed import OrganisationEnhedRelationKode
from ._organisationsenhed import OrganisationEnhedTilsGyldighed
from ._organisationsfunktion import OrganisationFunktion
from ._organisationsfunktion import OrganisationFunktionAttrEgenskaber
from ._organisationsfunktion import OrganisationFunktionRegistrering
from ._organisationsfunktion import OrganisationFunktionRelation
from ._organisationsfunktion import OrganisationFunktionRelationKode
from ._organisationsfunktion import OrganisationFunktionTilsGyldighed
from oio_rest.config import get_settings as oio_rest_get_settings


def get_sessionmaker(user, password, host, name):
    engine = create_async_engine(
        f"postgresql+psycopg://{user}:{password}@{host}/{name}"
    )
    return async_sessionmaker(engine)
