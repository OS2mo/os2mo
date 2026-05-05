# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.db import AsyncSession
from mora.db import Bruger
from mora.db import BrugerAttrEgenskaber
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import BrugerTilsGyldighed
from mora.db import Facet
from mora.db import FacetAttrEgenskaber
from mora.db import FacetRegistrering
from mora.db import FacetRelation
from mora.db import FacetTilsPubliceret
from mora.db import ITSystem
from mora.db import ITSystemAttrEgenskaber
from mora.db import ITSystemRegistrering
from mora.db import ITSystemRelation
from mora.db import ITSystemTilsGyldighed
from mora.db import Klasse
from mora.db import KlasseAttrEgenskaber
from mora.db import KlasseRegistrering
from mora.db import KlasseRelation
from mora.db import KlasseTilsPubliceret
from mora.db import Organisation
from mora.db import OrganisationAttrEgenskaber
from mora.db import OrganisationEnhed
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedRelation
from mora.db import OrganisationEnhedTilsGyldighed
from mora.db import OrganisationFunktion
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionTilsGyldighed
from mora.db import OrganisationRegistrering
from mora.db import OrganisationRelation
from mora.db import OrganisationTilsGyldighed
from sqlalchemy import select


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "db_object",
    [
        Bruger,
        BrugerAttrEgenskaber,
        BrugerAttrUdvidelser,
        BrugerRegistrering,
        BrugerRelation,
        BrugerTilsGyldighed,
        Facet,
        FacetAttrEgenskaber,
        FacetRegistrering,
        FacetRelation,
        FacetTilsPubliceret,
        ITSystem,
        ITSystemAttrEgenskaber,
        ITSystemRegistrering,
        ITSystemRelation,
        ITSystemTilsGyldighed,
        Klasse,
        KlasseAttrEgenskaber,
        KlasseRegistrering,
        KlasseRelation,
        KlasseTilsPubliceret,
        Organisation,
        OrganisationAttrEgenskaber,
        OrganisationEnhed,
        OrganisationEnhedAttrEgenskaber,
        OrganisationEnhedRegistrering,
        OrganisationEnhedRelation,
        OrganisationEnhedTilsGyldighed,
        OrganisationFunktion,
        OrganisationFunktionAttrEgenskaber,
        OrganisationFunktionRegistrering,
        OrganisationFunktionRelation,
        OrganisationFunktionTilsGyldighed,
        OrganisationRegistrering,
        OrganisationRelation,
        OrganisationTilsGyldighed,
    ],
)
async def test_db_models_simple(fixture_db: AsyncSession, db_object):
    r = await fixture_db.scalar(select(db_object).limit(1))
    assert r is not None
