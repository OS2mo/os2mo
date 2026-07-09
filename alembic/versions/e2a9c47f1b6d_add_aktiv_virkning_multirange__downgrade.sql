-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- bruger (also has an attr_udvidelser period table)
DROP TRIGGER touch_period_rows ON bruger_tils_gyldighed;
DROP TRIGGER set_active_tils ON bruger_attr_egenskaber;
DROP TRIGGER set_active_tils ON bruger_attr_udvidelser;
DROP TRIGGER set_active_tils ON bruger_relation;
DROP FUNCTION bruger_touch_period_rows();
DROP FUNCTION bruger_set_active_tils();
DROP INDEX bruger_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX bruger_attr_udvidelser_aktiv_virkning_idx;
DROP INDEX bruger_relation_aktiv_virkning_idx;
ALTER TABLE bruger_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE bruger_attr_udvidelser DROP COLUMN active_tils;
ALTER TABLE bruger_relation DROP COLUMN active_tils;

-- facet
DROP TRIGGER touch_period_rows ON facet_tils_publiceret;
DROP TRIGGER set_active_tils ON facet_attr_egenskaber;
DROP TRIGGER set_active_tils ON facet_relation;
DROP FUNCTION facet_touch_period_rows();
DROP FUNCTION facet_set_active_tils();
DROP INDEX facet_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX facet_relation_aktiv_virkning_idx;
ALTER TABLE facet_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE facet_relation DROP COLUMN active_tils;

-- itsystem
DROP TRIGGER touch_period_rows ON itsystem_tils_gyldighed;
DROP TRIGGER set_active_tils ON itsystem_attr_egenskaber;
DROP TRIGGER set_active_tils ON itsystem_relation;
DROP FUNCTION itsystem_touch_period_rows();
DROP FUNCTION itsystem_set_active_tils();
DROP INDEX itsystem_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX itsystem_relation_aktiv_virkning_idx;
ALTER TABLE itsystem_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE itsystem_relation DROP COLUMN active_tils;

-- klasse
DROP TRIGGER touch_period_rows ON klasse_tils_publiceret;
DROP TRIGGER set_active_tils ON klasse_attr_egenskaber;
DROP TRIGGER set_active_tils ON klasse_relation;
DROP FUNCTION klasse_touch_period_rows();
DROP FUNCTION klasse_set_active_tils();
DROP INDEX klasse_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX klasse_relation_aktiv_virkning_idx;
ALTER TABLE klasse_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE klasse_relation DROP COLUMN active_tils;

-- organisation
DROP TRIGGER touch_period_rows ON organisation_tils_gyldighed;
DROP TRIGGER set_active_tils ON organisation_attr_egenskaber;
DROP TRIGGER set_active_tils ON organisation_relation;
DROP FUNCTION organisation_touch_period_rows();
DROP FUNCTION organisation_set_active_tils();
DROP INDEX organisation_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX organisation_relation_aktiv_virkning_idx;
ALTER TABLE organisation_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE organisation_relation DROP COLUMN active_tils;

-- organisationenhed
DROP TRIGGER touch_period_rows ON organisationenhed_tils_gyldighed;
DROP TRIGGER set_active_tils ON organisationenhed_attr_egenskaber;
DROP TRIGGER set_active_tils ON organisationenhed_relation;
DROP FUNCTION organisationenhed_touch_period_rows();
DROP FUNCTION organisationenhed_set_active_tils();
DROP INDEX organisationenhed_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX organisationenhed_relation_aktiv_virkning_idx;
ALTER TABLE organisationenhed_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE organisationenhed_relation DROP COLUMN active_tils;

-- organisationfunktion (also has an attr_udvidelser period table)
DROP TRIGGER touch_period_rows ON organisationfunktion_tils_gyldighed;
DROP TRIGGER set_active_tils ON organisationfunktion_attr_egenskaber;
DROP TRIGGER set_active_tils ON organisationfunktion_attr_udvidelser;
DROP TRIGGER set_active_tils ON organisationfunktion_relation;
DROP FUNCTION organisationfunktion_touch_period_rows();
DROP FUNCTION organisationfunktion_set_active_tils();
DROP INDEX organisationfunktion_attr_egenskaber_aktiv_virkning_idx;
DROP INDEX organisationfunktion_attr_udvidelser_aktiv_virkning_idx;
DROP INDEX organisationfunktion_relation_aktiv_virkning_idx;
ALTER TABLE organisationfunktion_attr_egenskaber DROP COLUMN active_tils;
ALTER TABLE organisationfunktion_attr_udvidelser DROP COLUMN active_tils;
ALTER TABLE organisationfunktion_relation DROP COLUMN active_tils;
