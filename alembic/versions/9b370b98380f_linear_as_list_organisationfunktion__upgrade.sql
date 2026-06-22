-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- Rewrite every as_list_<type> to be O(n) in the number of validities.
--
-- Each function rebuilt the object by repeatedly LEFT JOIN-ing each child
-- table and GROUP BY-ing, carrying every already-aggregated array forward as
-- a GROUP BY key. Grouping N rows of one child table by an N-element array key
-- from another child table costs N*N, so reconstructing an object with many
-- validity slices was quadratic. Every create/update/terminate pays this twice
-- (the two internal reads in as_update_<type>), which is why e.g.
-- engagement_terminate took ~16s at a few hundred validities.
--
-- These rewrites aggregate each child table independently (GROUP BY reg_id) and
-- join the per-table aggregates on reg_id, which is linear. The output of each
-- function is byte-identical to the original.
--
-- Both this file and the matching downgrade are pg_format(pg_get_functiondef())
-- of the respective functions, so they can be diffed directly to review the
-- rewrite (the CREATE/RETURNS/DECLARE/auth boilerplate is identical; only the
-- query body differs).

-- ===================== organisation =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_organisation (organisation_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::ORGANISATIONREGISTRERINGTYPE[])
    RETURNS organisationtype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result OrganisationType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_organisation (organisation_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(organisation_uuids, 1), 0) AND auth_filtered_uuids @> organisation_uuids) THEN
        RAISE EXCEPTION 'Unable to list organisation with uuids [%]. All objects do not fullfill the stipulated criteria:%', organisation_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS organisation_id,
            b.id AS rid,
            b.registrering
        FROM
            organisation a
            JOIN organisation_registrering b ON b.organisation_id = a.id
        WHERE
            a.id = ANY (organisation_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.organisation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.gyldighed)::OrganisationGyldighedTilsType ORDER BY b.gyldighed, b.virkning)) AS arr
    FROM
        organisation_tils_gyldighed b
    WHERE
        b.organisation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisation_registrering_id
),
e AS (
    SELECT
        b.organisation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.organisationsnavn, b.virkning)::OrganisationEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.organisationsnavn, b.virkning)) AS arr
    FROM
        organisation_attr_egenskaber b
    WHERE
        b.organisation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisation_registrering_id
),
r AS (
    SELECT
        b.organisation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        organisation_relation b
    WHERE
        b.organisation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisation_registrering_id
)
SELECT
    array_agg(x.organisationObj ORDER BY x.organisation_id)
INTO
    result
FROM (
    SELECT
        reg.organisation_id,
        ROW (reg.organisation_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::OrganisationRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::OrganisationType AS organisationObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.organisation_id) x;
    RETURN result;
END;
$function$
;

-- ===================== organisationenhed =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_organisationenhed (organisationenhed_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::ORGANISATIONENHEDREGISTRERINGTYPE[])
    RETURNS organisationenhedtype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result OrganisationenhedType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_organisationenhed (organisationenhed_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(organisationenhed_uuids, 1), 0) AND auth_filtered_uuids @> organisationenhed_uuids) THEN
        RAISE EXCEPTION 'Unable to list organisationenhed with uuids [%]. All objects do not fullfill the stipulated criteria:%', organisationenhed_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS organisationenhed_id,
            b.id AS rid,
            b.registrering
        FROM
            organisationenhed a
            JOIN organisationenhed_registrering b ON b.organisationenhed_id = a.id
        WHERE
            a.id = ANY (organisationenhed_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.organisationenhed_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.gyldighed)::OrganisationenhedGyldighedTilsType ORDER BY b.gyldighed, b.virkning)) AS arr
    FROM
        organisationenhed_tils_gyldighed b
    WHERE
        b.organisationenhed_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationenhed_registrering_id
),
e AS (
    SELECT
        b.organisationenhed_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.enhedsnavn, b.virkning)::OrganisationenhedEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.enhedsnavn, b.virkning)) AS arr
    FROM
        organisationenhed_attr_egenskaber b
    WHERE
        b.organisationenhed_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationenhed_registrering_id
),
r AS (
    SELECT
        b.organisationenhed_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationenhedRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        organisationenhed_relation b
    WHERE
        b.organisationenhed_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationenhed_registrering_id
)
SELECT
    array_agg(x.organisationenhedObj ORDER BY x.organisationenhed_id)
INTO
    result
FROM (
    SELECT
        reg.organisationenhed_id,
        ROW (reg.organisationenhed_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::OrganisationenhedRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::OrganisationenhedType AS organisationenhedObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.organisationenhed_id) x;
    RETURN result;
END;
$function$
;

-- ===================== itsystem =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_itsystem (itsystem_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::ITSYSTEMREGISTRERINGTYPE[])
    RETURNS itsystemtype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result ItsystemType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_itsystem (itsystem_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(itsystem_uuids, 1), 0) AND auth_filtered_uuids @> itsystem_uuids) THEN
        RAISE EXCEPTION 'Unable to list itsystem with uuids [%]. All objects do not fullfill the stipulated criteria:%', itsystem_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS itsystem_id,
            b.id AS rid,
            b.registrering
        FROM
            itsystem a
            JOIN itsystem_registrering b ON b.itsystem_id = a.id
        WHERE
            a.id = ANY (itsystem_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.itsystem_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.gyldighed)::ItsystemGyldighedTilsType ORDER BY b.gyldighed, b.virkning)) AS arr
    FROM
        itsystem_tils_gyldighed b
    WHERE
        b.itsystem_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.itsystem_registrering_id
),
e AS (
    SELECT
        b.itsystem_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.itsystemnavn, b.itsystemtype, b.konfigurationreference, b.virkning)::ItsystemEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.itsystemnavn, b.itsystemtype, b.konfigurationreference, b.virkning)) AS arr
    FROM
        itsystem_attr_egenskaber b
    WHERE
        b.itsystem_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.itsystem_registrering_id
),
r AS (
    SELECT
        b.itsystem_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::ItsystemRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        itsystem_relation b
    WHERE
        b.itsystem_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.itsystem_registrering_id
)
SELECT
    array_agg(x.itsystemObj ORDER BY x.itsystem_id)
INTO
    result
FROM (
    SELECT
        reg.itsystem_id,
        ROW (reg.itsystem_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::ItsystemRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::ItsystemType AS itsystemObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.itsystem_id) x;
    RETURN result;
END;
$function$
;

-- ===================== klassifikation =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_klassifikation (klassifikation_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::KLASSIFIKATIONREGISTRERINGTYPE[])
    RETURNS klassifikationtype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result KlassifikationType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_klassifikation (klassifikation_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(klassifikation_uuids, 1), 0) AND auth_filtered_uuids @> klassifikation_uuids) THEN
        RAISE EXCEPTION 'Unable to list klassifikation with uuids [%]. All objects do not fullfill the stipulated criteria:%', klassifikation_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS klassifikation_id,
            b.id AS rid,
            b.registrering
        FROM
            klassifikation a
            JOIN klassifikation_registrering b ON b.klassifikation_id = a.id
        WHERE
            a.id = ANY (klassifikation_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.klassifikation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.publiceret)::KlassifikationPubliceretTilsType ORDER BY b.publiceret, b.virkning)) AS arr
    FROM
        klassifikation_tils_publiceret b
    WHERE
        b.klassifikation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klassifikation_registrering_id
),
e AS (
    SELECT
        b.klassifikation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.beskrivelse, b.kaldenavn, b.ophavsret, b.virkning)::KlassifikationEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.beskrivelse, b.kaldenavn, b.ophavsret, b.virkning)) AS arr
    FROM
        klassifikation_attr_egenskaber b
    WHERE
        b.klassifikation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klassifikation_registrering_id
),
r AS (
    SELECT
        b.klassifikation_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::KlassifikationRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        klassifikation_relation b
    WHERE
        b.klassifikation_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klassifikation_registrering_id
)
SELECT
    array_agg(x.klassifikationObj ORDER BY x.klassifikation_id)
INTO
    result
FROM (
    SELECT
        reg.klassifikation_id,
        ROW (reg.klassifikation_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::KlassifikationRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::KlassifikationType AS klassifikationObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.klassifikation_id) x;
    RETURN result;
END;
$function$
;

-- ===================== facet =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_facet (facet_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr facetregistreringtype[] DEFAULT NULL::FACETREGISTRERINGTYPE[])
    RETURNS facettype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result FacetType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_facet (facet_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(facet_uuids, 1), 0) AND auth_filtered_uuids @> facet_uuids) THEN
        RAISE EXCEPTION 'Unable to list facet with uuids [%]. All objects do not fullfill the stipulated criteria:%', facet_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS facet_id,
            b.id AS rid,
            b.registrering
        FROM
            facet a
            JOIN facet_registrering b ON b.facet_id = a.id
        WHERE
            a.id = ANY (facet_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.facet_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.publiceret)::FacetPubliceretTilsType ORDER BY b.publiceret, b.virkning)) AS arr
    FROM
        facet_tils_publiceret b
    WHERE
        b.facet_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.facet_registrering_id
),
e AS (
    SELECT
        b.facet_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.beskrivelse, b.opbygning, b.ophavsret, b.plan, b.supplement, b.retskilde, b.virkning)::FacetEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.beskrivelse, b.opbygning, b.ophavsret, b.plan, b.supplement, b.retskilde, b.virkning)) AS arr
    FROM
        facet_attr_egenskaber b
    WHERE
        b.facet_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.facet_registrering_id
),
r AS (
    SELECT
        b.facet_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::FacetRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        facet_relation b
    WHERE
        b.facet_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.facet_registrering_id
)
SELECT
    array_agg(x.facetObj ORDER BY x.facet_id)
INTO
    result
FROM (
    SELECT
        reg.facet_id,
        ROW (reg.facet_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::FacetRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::FacetType AS facetObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.facet_id) x;
    RETURN result;
END;
$function$
;

-- ===================== bruger =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_bruger (bruger_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::BRUGERREGISTRERINGTYPE[])
    RETURNS brugertype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result BrugerType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_bruger (bruger_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(bruger_uuids, 1), 0) AND auth_filtered_uuids @> bruger_uuids) THEN
        RAISE EXCEPTION 'Unable to list bruger with uuids [%]. All objects do not fullfill the stipulated criteria:%', bruger_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS bruger_id,
            b.id AS rid,
            b.registrering
        FROM
            bruger a
            JOIN bruger_registrering b ON b.bruger_id = a.id
        WHERE
            a.id = ANY (bruger_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.bruger_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.gyldighed)::BrugerGyldighedTilsType ORDER BY b.gyldighed, b.virkning)) AS arr
    FROM
        bruger_tils_gyldighed b
    WHERE
        b.bruger_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.bruger_registrering_id
),
e AS (
    SELECT
        b.bruger_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.brugernavn, b.brugertype, b.virkning)::BrugerEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.brugernavn, b.brugertype, b.virkning)) AS arr
    FROM
        bruger_attr_egenskaber b
    WHERE
        b.bruger_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.bruger_registrering_id
),
u AS (
    SELECT
        b.bruger_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.fornavn, b.efternavn, b.kaldenavn_fornavn, b.kaldenavn_efternavn, b.seniority, b.virkning)::BrugerUdvidelserAttrType ORDER BY b.fornavn, b.efternavn, b.kaldenavn_fornavn, b.kaldenavn_efternavn, b.seniority, b.virkning)) AS arr
    FROM
        bruger_attr_udvidelser b
    WHERE
        b.bruger_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.bruger_registrering_id
),
r AS (
    SELECT
        b.bruger_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::BrugerRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        bruger_relation b
    WHERE
        b.bruger_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.bruger_registrering_id
)
SELECT
    array_agg(x.brugerObj ORDER BY x.bruger_id)
INTO
    result
FROM (
    SELECT
        reg.bruger_id,
        ROW (reg.bruger_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, u.arr, r.arr)::BrugerRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::BrugerType AS brugerObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN u ON u.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.bruger_id) x;
    RETURN result;
END;
$function$
;

-- ===================== klasse =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_klasse (klasse_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::KLASSEREGISTRERINGTYPE[])
    RETURNS klassetype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result KlasseType[];
BEGIN
    auth_filtered_uuids := _as_filter_unauth_klasse (klasse_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(klasse_uuids, 1), 0) AND auth_filtered_uuids @> klasse_uuids) THEN
        RAISE EXCEPTION 'Unable to list klasse with uuids [%]. All objects do not fullfill the stipulated criteria:%', klasse_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;
    WITH reg AS (
        SELECT
            a.id AS klasse_id,
            b.id AS rid,
            b.registrering
        FROM
            klasse a
            JOIN klasse_registrering b ON b.klasse_id = a.id
        WHERE
            a.id = ANY (klasse_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
t AS (
    SELECT
        b.klasse_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.publiceret)::KlassePubliceretTilsType ORDER BY b.publiceret, b.virkning)) AS arr
    FROM
        klasse_tils_publiceret b
    WHERE
        b.klasse_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klasse_registrering_id
),
soe AS (
    SELECT
        c.klasse_attr_egenskaber_id AS eid,
        _remove_nulls_in_array (array_agg(ROW (c.soegeordidentifikator, c.beskrivelse, c.soegeordskategori)::KlasseSoegeordType ORDER BY c.soegeordidentifikator, c.beskrivelse, c.soegeordskategori)) AS arr
    FROM
        klasse_attr_egenskaber_soegeord c
    GROUP BY
        c.klasse_attr_egenskaber_id
),
e AS (
    SELECT
        b.klasse_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.beskrivelse, b.eksempel, b.omfang, b.titel, b.retskilde, b.aendringsnotat, soe.arr, b.virkning)::KlasseEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.beskrivelse, b.eksempel, b.omfang, b.titel, b.retskilde, b.aendringsnotat, b.virkning, soe.arr)) AS arr
    FROM
        klasse_attr_egenskaber b
        LEFT JOIN soe ON soe.eid = b.id
    WHERE
        b.klasse_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klasse_registrering_id
),
r AS (
    SELECT
        b.klasse_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::KlasseRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        klasse_relation b
    WHERE
        b.klasse_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.klasse_registrering_id
)
SELECT
    array_agg(x.klasseObj ORDER BY x.klasse_id)
INTO
    result
FROM (
    SELECT
        reg.klasse_id,
        ROW (reg.klasse_id,
            array_agg(ROW (reg.registrering, t.arr, e.arr, r.arr)::KlasseRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::KlasseType AS klasseObj
    FROM
        reg
    LEFT JOIN t ON t.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.klasse_id) x;
    RETURN result;
END;
$function$
;

-- ===================== organisationfunktion =====================
CREATE OR REPLACE FUNCTION actual_state.as_list_organisationfunktion (organisationfunktion_uuids uuid[], registrering_tstzrange tstzrange, virkning_tstzrange tstzrange, auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::ORGANISATIONFUNKTIONREGISTRERINGTYPE[])
    RETURNS organisationfunktiontype[]
    LANGUAGE plpgsql
    STABLE
    AS $function$
DECLARE
    auth_filtered_uuids uuid[];
    result OrganisationfunktionType[];
BEGIN
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_organisationfunktion (organisationfunktion_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(organisationfunktion_uuids, 1), 0) AND auth_filtered_uuids @> organisationfunktion_uuids) THEN
        RAISE EXCEPTION 'Unable to list organisationfunktion with uuids [%]. All objects do not fullfill the stipulated criteria:%', organisationfunktion_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    WITH reg AS (
        -- The registrations to reconstruct, filtered on registrering_tstzrange.
        SELECT
            a.id AS organisationfunktion_id,
            b.id AS rid,
            b.registrering
        FROM
            organisationfunktion a
            JOIN organisationfunktion_registrering b ON b.organisationfunktion_id = a.id
        WHERE
            a.id = ANY (organisationfunktion_uuids)
            AND ((registrering_tstzrange IS NULL
                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                OR registrering_tstzrange && (b.registrering).timeperiod)
),
g AS (
    -- tilstand: gyldighed
    SELECT
        b.organisationfunktion_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.virkning, b.gyldighed)::OrganisationfunktionGyldighedTilsType ORDER BY b.gyldighed, b.virkning)) AS arr
    FROM
        organisationfunktion_tils_gyldighed b
    WHERE
        b.organisationfunktion_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationfunktion_registrering_id
),
e AS (
    -- attribut: egenskaber
    SELECT
        b.organisationfunktion_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.brugervendtnoegle, b.funktionsnavn, b.virkning)::OrganisationfunktionEgenskaberAttrType ORDER BY b.brugervendtnoegle, b.funktionsnavn, b.virkning)) AS arr
    FROM
        organisationfunktion_attr_egenskaber b
    WHERE
        b.organisationfunktion_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationfunktion_registrering_id
),
u AS (
    -- attribut: udvidelser
    SELECT
        b.organisationfunktion_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.primær, b.fraktion, b.udvidelse_1, b.udvidelse_2, b.udvidelse_3, b.udvidelse_4, b.udvidelse_5, b.udvidelse_6, b.udvidelse_7, b.udvidelse_8, b.udvidelse_9, b.udvidelse_10, b.virkning)::OrganisationfunktionUdvidelserAttrType ORDER BY b.primær, b.fraktion, b.udvidelse_1, b.udvidelse_2, b.udvidelse_3, b.udvidelse_4, b.udvidelse_5, b.udvidelse_6, b.udvidelse_7, b.udvidelse_8, b.udvidelse_9, b.udvidelse_10, b.virkning)) AS arr
    FROM
        organisationfunktion_attr_udvidelser b
    WHERE
        b.organisationfunktion_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationfunktion_registrering_id
),
r AS (
    -- relationer
    SELECT
        b.organisationfunktion_registrering_id AS rid,
        _remove_nulls_in_array (array_agg(ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationfunktionRelationType ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) AS arr
    FROM
        organisationfunktion_relation b
    WHERE
        b.organisationfunktion_registrering_id IN (
            SELECT
                rid
            FROM
                reg)
            AND (virkning_tstzrange IS NULL
                OR (b.virkning).TimePeriod && virkning_tstzrange)
        GROUP BY
            b.organisationfunktion_registrering_id
)
SELECT
    array_agg(x.organisationfunktionObj ORDER BY x.organisationfunktion_id)
INTO
    result
FROM (
    SELECT
        reg.organisationfunktion_id,
        ROW (reg.organisationfunktion_id,
            array_agg(ROW (reg.registrering, g.arr, e.arr, u.arr, r.arr)::OrganisationfunktionRegistreringType ORDER BY upper((reg.registrering).TimePeriod) DESC))::OrganisationfunktionType AS organisationfunktionObj
    FROM
        reg
    LEFT JOIN g ON g.rid = reg.rid
    LEFT JOIN e ON e.rid = reg.rid
    LEFT JOIN u ON u.rid = reg.rid
    LEFT JOIN r ON r.rid = reg.rid
GROUP BY
    reg.organisationfunktion_id) AS x;
    RETURN result;
END;
$function$
;
