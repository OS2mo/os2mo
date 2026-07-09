-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- bruger (also has an attr_udvidelser period table)
ALTER TABLE bruger_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE bruger_attr_udvidelser ADD COLUMN active_tils tstzmultirange;
ALTER TABLE bruger_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX bruger_attr_egenskaber_aktiv_virkning_idx ON bruger_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX bruger_attr_udvidelser_aktiv_virkning_idx ON bruger_attr_udvidelser USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX bruger_relation_aktiv_virkning_idx ON bruger_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION bruger_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM bruger_tils_gyldighed t
         WHERE t.bruger_registrering_id = NEW.bruger_registrering_id AND t.gyldighed = 'Aktiv'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON bruger_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION bruger_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON bruger_attr_udvidelser FOR EACH ROW EXECUTE FUNCTION bruger_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON bruger_relation FOR EACH ROW EXECUTE FUNCTION bruger_set_active_tils();
CREATE FUNCTION bruger_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.bruger_registrering_id; ELSE rid := NEW.bruger_registrering_id; END IF;
    UPDATE bruger_attr_egenskaber SET id = id WHERE bruger_registrering_id = rid;
    UPDATE bruger_attr_udvidelser SET id = id WHERE bruger_registrering_id = rid;
    UPDATE bruger_relation SET id = id WHERE bruger_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON bruger_tils_gyldighed FOR EACH ROW EXECUTE FUNCTION bruger_touch_period_rows();

-- facet
ALTER TABLE facet_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE facet_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX facet_attr_egenskaber_aktiv_virkning_idx ON facet_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX facet_relation_aktiv_virkning_idx ON facet_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION facet_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM facet_tils_publiceret t
         WHERE t.facet_registrering_id = NEW.facet_registrering_id AND t.publiceret = 'Publiceret'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON facet_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION facet_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON facet_relation FOR EACH ROW EXECUTE FUNCTION facet_set_active_tils();
CREATE FUNCTION facet_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.facet_registrering_id; ELSE rid := NEW.facet_registrering_id; END IF;
    UPDATE facet_attr_egenskaber SET id = id WHERE facet_registrering_id = rid;
    UPDATE facet_relation SET id = id WHERE facet_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON facet_tils_publiceret FOR EACH ROW EXECUTE FUNCTION facet_touch_period_rows();

-- itsystem
ALTER TABLE itsystem_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE itsystem_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX itsystem_attr_egenskaber_aktiv_virkning_idx ON itsystem_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX itsystem_relation_aktiv_virkning_idx ON itsystem_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION itsystem_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM itsystem_tils_gyldighed t
         WHERE t.itsystem_registrering_id = NEW.itsystem_registrering_id AND t.gyldighed = 'Aktiv'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON itsystem_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION itsystem_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON itsystem_relation FOR EACH ROW EXECUTE FUNCTION itsystem_set_active_tils();
CREATE FUNCTION itsystem_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.itsystem_registrering_id; ELSE rid := NEW.itsystem_registrering_id; END IF;
    UPDATE itsystem_attr_egenskaber SET id = id WHERE itsystem_registrering_id = rid;
    UPDATE itsystem_relation SET id = id WHERE itsystem_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON itsystem_tils_gyldighed FOR EACH ROW EXECUTE FUNCTION itsystem_touch_period_rows();

-- klasse
ALTER TABLE klasse_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE klasse_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX klasse_attr_egenskaber_aktiv_virkning_idx ON klasse_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX klasse_relation_aktiv_virkning_idx ON klasse_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION klasse_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM klasse_tils_publiceret t
         WHERE t.klasse_registrering_id = NEW.klasse_registrering_id AND t.publiceret = 'Publiceret'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON klasse_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION klasse_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON klasse_relation FOR EACH ROW EXECUTE FUNCTION klasse_set_active_tils();
CREATE FUNCTION klasse_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.klasse_registrering_id; ELSE rid := NEW.klasse_registrering_id; END IF;
    UPDATE klasse_attr_egenskaber SET id = id WHERE klasse_registrering_id = rid;
    UPDATE klasse_relation SET id = id WHERE klasse_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON klasse_tils_publiceret FOR EACH ROW EXECUTE FUNCTION klasse_touch_period_rows();

-- organisation
ALTER TABLE organisation_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE organisation_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX organisation_attr_egenskaber_aktiv_virkning_idx ON organisation_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX organisation_relation_aktiv_virkning_idx ON organisation_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION organisation_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM organisation_tils_gyldighed t
         WHERE t.organisation_registrering_id = NEW.organisation_registrering_id AND t.gyldighed = 'Aktiv'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisation_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION organisation_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisation_relation FOR EACH ROW EXECUTE FUNCTION organisation_set_active_tils();
CREATE FUNCTION organisation_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.organisation_registrering_id; ELSE rid := NEW.organisation_registrering_id; END IF;
    UPDATE organisation_attr_egenskaber SET id = id WHERE organisation_registrering_id = rid;
    UPDATE organisation_relation SET id = id WHERE organisation_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON organisation_tils_gyldighed FOR EACH ROW EXECUTE FUNCTION organisation_touch_period_rows();

-- organisationenhed
ALTER TABLE organisationenhed_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE organisationenhed_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX organisationenhed_attr_egenskaber_aktiv_virkning_idx ON organisationenhed_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX organisationenhed_relation_aktiv_virkning_idx ON organisationenhed_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION organisationenhed_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM organisationenhed_tils_gyldighed t
         WHERE t.organisationenhed_registrering_id = NEW.organisationenhed_registrering_id AND t.gyldighed = 'Aktiv'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisationenhed_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION organisationenhed_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisationenhed_relation FOR EACH ROW EXECUTE FUNCTION organisationenhed_set_active_tils();
CREATE FUNCTION organisationenhed_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.organisationenhed_registrering_id; ELSE rid := NEW.organisationenhed_registrering_id; END IF;
    UPDATE organisationenhed_attr_egenskaber SET id = id WHERE organisationenhed_registrering_id = rid;
    UPDATE organisationenhed_relation SET id = id WHERE organisationenhed_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON organisationenhed_tils_gyldighed FOR EACH ROW EXECUTE FUNCTION organisationenhed_touch_period_rows();

-- organisationfunktion (also has an attr_udvidelser period table)
ALTER TABLE organisationfunktion_attr_egenskaber ADD COLUMN active_tils tstzmultirange;
ALTER TABLE organisationfunktion_attr_udvidelser ADD COLUMN active_tils tstzmultirange;
ALTER TABLE organisationfunktion_relation ADD COLUMN active_tils tstzmultirange;
CREATE INDEX organisationfunktion_attr_egenskaber_aktiv_virkning_idx ON organisationfunktion_attr_egenskaber USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX organisationfunktion_attr_udvidelser_aktiv_virkning_idx ON organisationfunktion_attr_udvidelser USING gist ((tstzmultirange((virkning).timeperiod) * active_tils));
CREATE INDEX organisationfunktion_relation_aktiv_virkning_idx ON organisationfunktion_relation USING gist (rel_type, rel_maal_uuid, (tstzmultirange((virkning).timeperiod) * active_tils));
CREATE FUNCTION organisationfunktion_set_active_tils() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.active_tils := COALESCE(
        (SELECT range_agg((t.virkning).timeperiod) FROM organisationfunktion_tils_gyldighed t
         WHERE t.organisationfunktion_registrering_id = NEW.organisationfunktion_registrering_id AND t.gyldighed = 'Aktiv'),
        '{}'::tstzmultirange);
    RETURN NEW;
END;
$$;
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisationfunktion_attr_egenskaber FOR EACH ROW EXECUTE FUNCTION organisationfunktion_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisationfunktion_attr_udvidelser FOR EACH ROW EXECUTE FUNCTION organisationfunktion_set_active_tils();
CREATE TRIGGER set_active_tils BEFORE INSERT OR UPDATE ON organisationfunktion_relation FOR EACH ROW EXECUTE FUNCTION organisationfunktion_set_active_tils();
CREATE FUNCTION organisationfunktion_touch_period_rows() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    rid bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN rid := OLD.organisationfunktion_registrering_id; ELSE rid := NEW.organisationfunktion_registrering_id; END IF;
    UPDATE organisationfunktion_attr_egenskaber SET id = id WHERE organisationfunktion_registrering_id = rid;
    UPDATE organisationfunktion_attr_udvidelser SET id = id WHERE organisationfunktion_registrering_id = rid;
    UPDATE organisationfunktion_relation SET id = id WHERE organisationfunktion_registrering_id = rid;
    RETURN NULL;
END;
$$;
CREATE TRIGGER touch_period_rows AFTER INSERT OR UPDATE OR DELETE ON organisationfunktion_tils_gyldighed FOR EACH ROW EXECUTE FUNCTION organisationfunktion_touch_period_rows();
