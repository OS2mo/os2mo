-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- The BEFORE INSERT/UPDATE trigger always sets active_tils, so new rows are
-- non-null without a DEFAULT; the backfill has filled existing rows. SET NOT
-- NULL scans once to verify.
ALTER TABLE bruger_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE bruger_attr_udvidelser ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE bruger_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE facet_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE facet_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE itsystem_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE itsystem_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE klasse_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE klasse_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE organisation_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE organisation_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE organisationenhed_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE organisationenhed_relation ALTER COLUMN active_tils SET NOT NULL;

ALTER TABLE organisationfunktion_attr_egenskaber ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE organisationfunktion_attr_udvidelser ALTER COLUMN active_tils SET NOT NULL;
ALTER TABLE organisationfunktion_relation ALTER COLUMN active_tils SET NOT NULL;
