-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

CREATE INDEX IF NOT EXISTS bruger_relation_idx_bruger_registrering_id ON bruger_relation (bruger_registrering_id) WHERE bruger_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS facet_relation_idx_facet_registrering_id ON facet_relation (facet_registrering_id) WHERE facet_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS itsystem_relation_idx_itsystem_registrering_id ON itsystem_relation (itsystem_registrering_id) WHERE itsystem_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS klasse_relation_idx_klasse_registrering_id ON klasse_relation (klasse_registrering_id) WHERE klasse_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS klassifikation_relation_idx_klassifikation_registrering_id ON klassifikation_relation (klassifikation_registrering_id) WHERE klassifikation_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS organisationenhed_relation_idx_organisationenhed_registrering_id ON organisationenhed_relation (organisationenhed_registrering_id) WHERE organisationenhed_registrering_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS organisationfunktion_relation_idx_organisationfunktion_registrering_id ON organisationfunktion_relation (organisationfunktion_registrering_id) WHERE organisationfunktion_registrering_id IS NOT NULL;

DROP INDEX IF EXISTS bruger_relation_reg_rel_idx;
DROP INDEX IF EXISTS facet_relation_reg_rel_idx;
DROP INDEX IF EXISTS itsystem_relation_reg_rel_idx;
DROP INDEX IF EXISTS klasse_relation_reg_rel_idx;
DROP INDEX IF EXISTS klassifikation_relation_reg_rel_idx;
DROP INDEX IF EXISTS organisationenhed_relation_reg_rel_idx;
DROP INDEX IF EXISTS organisationfunktion_relation_reg_rel_idx;
