# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import synonym

from ._common import Base
from ._common import _AttrEgenskaberMixin
from ._common import _OIOEntityMixin
from ._common import _RegistreringMixin
from ._common import _RelationMixin
from ._common import _TilsGyldighedMixin

# Think twice before using this. We will probably get rid of this, so the code
# base doesn't sometimes reflect a desire to be multi-tenant:
# https://rammearkitektur.docs.magenta.dk/decision-logs/2022/mo-should-not-be-multitenant.html


class Organisation(_OIOEntityMixin, Base):
    __tablename__ = "organisation"


class OrganisationRegistrering(_RegistreringMixin, Base):
    __tablename__ = "organisation_registrering"
    organisation_id = Column(ForeignKey("organisation.id"), index=True)
    uuid = synonym("organisation_id")


class OrganisationAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "organisation_attr_egenskaber"

    organisationsnavn: Mapped[str | None] = mapped_column(Text, index=True)

    organisation_registrering_id = Column(
        ForeignKey("organisation_registrering.id"), index=True
    )


OrganisationRelationKode = Literal["myndighed"]


class OrganisationRelation(_RelationMixin, Base):
    __tablename__ = "organisation_relation"

    rel_type: Mapped[OrganisationRelationKode]

    organisation_registrering_id = Column(
        ForeignKey("organisation_registrering.id"), index=True
    )


class OrganisationTilsGyldighed(_TilsGyldighedMixin("organisation"), Base):
    __tablename__ = "organisation_tils_gyldighed"

    organisation_registrering_id = Column(
        ForeignKey("organisation_registrering.id"), index=True
    )
