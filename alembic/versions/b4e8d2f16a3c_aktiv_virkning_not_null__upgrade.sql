-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

UPDATE bruger_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE bruger_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE bruger_attr_udvidelser SET id = id WHERE active_tils IS NULL;
ALTER TABLE bruger_attr_udvidelser ALTER COLUMN active_tils SET NOT NULL;
UPDATE bruger_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE bruger_relation ALTER COLUMN active_tils SET NOT NULL;

UPDATE facet_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE facet_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE facet_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE facet_relation ALTER COLUMN active_tils SET NOT NULL;

UPDATE itsystem_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE itsystem_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE itsystem_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE itsystem_relation ALTER COLUMN active_tils SET NOT NULL;

UPDATE klasse_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE klasse_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE klasse_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE klasse_relation ALTER COLUMN active_tils SET NOT NULL;

UPDATE organisationenhed_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE organisationenhed_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE organisationenhed_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE organisationenhed_relation ALTER COLUMN active_tils SET NOT NULL;

UPDATE organisationfunktion_attr_egenskaber SET id = id WHERE active_tils IS NULL;
ALTER TABLE organisationfunktion_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
UPDATE organisationfunktion_attr_udvidelser SET id = id WHERE active_tils IS NULL;
ALTER TABLE organisationfunktion_attr_udvidelser ALTER COLUMN active_tils SET NOT NULL;
UPDATE organisationfunktion_relation SET id = id WHERE active_tils IS NULL;
ALTER TABLE organisationfunktion_relation ALTER COLUMN active_tils SET NOT NULL;
