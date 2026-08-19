-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

CREATE INDEX IF NOT EXISTS bruger_relation_reg_rel_idx
    ON bruger_relation (bruger_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS facet_relation_reg_rel_idx
    ON facet_relation (facet_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS itsystem_relation_reg_rel_idx
    ON itsystem_relation (itsystem_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS klasse_relation_reg_rel_idx
    ON klasse_relation (klasse_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS klassifikation_relation_reg_rel_idx
    ON klassifikation_relation (klassifikation_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS organisationenhed_relation_reg_rel_idx
    ON organisationenhed_relation (organisationenhed_registrering_id, rel_type, rel_maal_uuid);
CREATE INDEX IF NOT EXISTS organisationfunktion_relation_reg_rel_idx
    ON organisationfunktion_relation (organisationfunktion_registrering_id, rel_type, rel_maal_uuid);

-- The indexes above supersede the single-column ones from b27228471604: they
-- lead with the same column, and the `WHERE ... IS NOT NULL` predicate is a
-- no-op since the column is `not null`.
DROP INDEX IF EXISTS bruger_relation_idx_bruger_registrering_id;
DROP INDEX IF EXISTS facet_relation_idx_facet_registrering_id;
DROP INDEX IF EXISTS itsystem_relation_idx_itsystem_registrering_id;
DROP INDEX IF EXISTS klasse_relation_idx_klasse_registrering_id;
DROP INDEX IF EXISTS klassifikation_relation_idx_klassifikation_registrering_id;
DROP INDEX IF EXISTS organisationenhed_relation_idx_organisationenhed_registrering_id;
DROP INDEX IF EXISTS organisationfunktion_relation_idx_organisationfunktion_registrering_id;
