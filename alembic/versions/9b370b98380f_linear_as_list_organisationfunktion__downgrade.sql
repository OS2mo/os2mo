-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- Restore the original (quadratic) as_list_<type> functions.
--
-- This is the pre-migration definition of each function, pg_format(ed) the
-- same way as the upgrade; diff the two files to review the O(n) rewrite.

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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_organisation (organisation_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(organisation_uuids, 1), 0) AND auth_filtered_uuids @> organisation_uuids) THEN
        RAISE EXCEPTION 'Unable to list organisation with uuids [%]. All objects do not fullfill the stipulated criteria:%', organisation_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.organisationObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.organisation_id,
                array_agg(ROW (a.registrering, a.OrganisationTilsGyldighedArr, a.OrganisationAttrEgenskaberArr, a.OrganisationRelationArr)::OrganisationRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::OrganisationType organisationObj
        FROM (
            SELECT
                a.organisation_id,
                a.organisation_registrering_id,
                a.registrering,
                a.OrganisationAttrEgenskaberArr,
                a.OrganisationTilsGyldighedArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) OrganisationRelationArr
            FROM (
                SELECT
                    a.organisation_id,
                    a.organisation_registrering_id,
                    a.registrering,
                    a.OrganisationAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.gyldighed)::OrganisationGyldighedTilsType
                            ELSE
                                NULL
                            END ORDER BY b.gyldighed, b.virkning)) OrganisationTilsGyldighedArr
                FROM (
                    SELECT
                        a.organisation_id,
                        a.organisation_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.organisationsnavn, b.virkning)::OrganisationEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.organisationsnavn, b.virkning)) OrganisationAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.id organisation_id,
                            b.id organisation_registrering_id,
                            b.registrering
                        FROM
                            organisation a
                            JOIN organisation_registrering b ON b.organisation_id = a.id
                        WHERE
                            a.id = ANY (organisation_uuids)
                            AND ((registrering_tstzrange IS NULL
                                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                        LEFT JOIN organisation_attr_egenskaber AS b ON b.organisation_registrering_id = a.organisation_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.organisation_id,
                            a.organisation_registrering_id,
                            a.registrering) AS a
                    LEFT JOIN organisation_tils_gyldighed AS b ON b.organisation_registrering_id = a.organisation_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.organisation_id,
                        a.organisation_registrering_id,
                        a.registrering,
                        a.OrganisationAttrEgenskaberArr) AS a
                LEFT JOIN organisation_relation b ON b.organisation_registrering_id = a.organisation_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.organisation_id,
                    a.organisation_registrering_id,
                    a.registrering,
                    a.OrganisationAttrEgenskaberArr,
                    a.OrganisationTilsGyldighedArr) AS a
            WHERE
                a.organisation_id IS NOT NULL
            GROUP BY
                a.organisation_id
            ORDER BY
                a.organisation_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_organisationenhed (organisationenhed_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(organisationenhed_uuids, 1), 0) AND auth_filtered_uuids @> organisationenhed_uuids) THEN
        RAISE EXCEPTION 'Unable to list organisationenhed with uuids [%]. All objects do not fullfill the stipulated criteria:%', organisationenhed_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.organisationenhedObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.organisationenhed_id,
                array_agg(ROW (a.registrering, a.OrganisationenhedTilsGyldighedArr, a.OrganisationenhedAttrEgenskaberArr, a.OrganisationenhedRelationArr)::OrganisationenhedRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::OrganisationenhedType organisationenhedObj
        FROM (
            SELECT
                a.organisationenhed_id,
                a.organisationenhed_registrering_id,
                a.registrering,
                a.OrganisationenhedAttrEgenskaberArr,
                a.OrganisationenhedTilsGyldighedArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationenhedRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) OrganisationenhedRelationArr
            FROM (
                SELECT
                    a.organisationenhed_id,
                    a.organisationenhed_registrering_id,
                    a.registrering,
                    a.OrganisationenhedAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.gyldighed)::OrganisationenhedGyldighedTilsType
                            ELSE
                                NULL
                            END ORDER BY b.gyldighed, b.virkning)) OrganisationenhedTilsGyldighedArr
                FROM (
                    SELECT
                        a.organisationenhed_id,
                        a.organisationenhed_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.enhedsnavn, b.virkning)::OrganisationenhedEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.enhedsnavn, b.virkning)) OrganisationenhedAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.id organisationenhed_id,
                            b.id organisationenhed_registrering_id,
                            b.registrering
                        FROM
                            organisationenhed a
                            JOIN organisationenhed_registrering b ON b.organisationenhed_id = a.id
                        WHERE
                            a.id = ANY (organisationenhed_uuids)
                            AND ((registrering_tstzrange IS NULL
                                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                        LEFT JOIN organisationenhed_attr_egenskaber AS b ON b.organisationenhed_registrering_id = a.organisationenhed_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.organisationenhed_id,
                            a.organisationenhed_registrering_id,
                            a.registrering) AS a
                    LEFT JOIN organisationenhed_tils_gyldighed AS b ON b.organisationenhed_registrering_id = a.organisationenhed_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.organisationenhed_id,
                        a.organisationenhed_registrering_id,
                        a.registrering,
                        a.OrganisationenhedAttrEgenskaberArr) AS a
                LEFT JOIN organisationenhed_relation b ON b.organisationenhed_registrering_id = a.organisationenhed_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.organisationenhed_id,
                    a.organisationenhed_registrering_id,
                    a.registrering,
                    a.OrganisationenhedAttrEgenskaberArr,
                    a.OrganisationenhedTilsGyldighedArr) AS a
            WHERE
                a.organisationenhed_id IS NOT NULL
            GROUP BY
                a.organisationenhed_id
            ORDER BY
                a.organisationenhed_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_itsystem (itsystem_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(itsystem_uuids, 1), 0) AND auth_filtered_uuids @> itsystem_uuids) THEN
        RAISE EXCEPTION 'Unable to list itsystem with uuids [%]. All objects do not fullfill the stipulated criteria:%', itsystem_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.itsystemObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.itsystem_id,
                array_agg(ROW (a.registrering, a.ItsystemTilsGyldighedArr, a.ItsystemAttrEgenskaberArr, a.ItsystemRelationArr)::ItsystemRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::ItsystemType itsystemObj
        FROM (
            SELECT
                a.itsystem_id,
                a.itsystem_registrering_id,
                a.registrering,
                a.ItsystemAttrEgenskaberArr,
                a.ItsystemTilsGyldighedArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::ItsystemRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) ItsystemRelationArr
            FROM (
                SELECT
                    a.itsystem_id,
                    a.itsystem_registrering_id,
                    a.registrering,
                    a.ItsystemAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.gyldighed)::ItsystemGyldighedTilsType
                            ELSE
                                NULL
                            END ORDER BY b.gyldighed, b.virkning)) ItsystemTilsGyldighedArr
                FROM (
                    SELECT
                        a.itsystem_id,
                        a.itsystem_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.itsystemnavn, b.itsystemtype, b.konfigurationreference, b.virkning)::ItsystemEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.itsystemnavn, b.itsystemtype, b.konfigurationreference, b.virkning)) ItsystemAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.id itsystem_id,
                            b.id itsystem_registrering_id,
                            b.registrering
                        FROM
                            itsystem a
                            JOIN itsystem_registrering b ON b.itsystem_id = a.id
                        WHERE
                            a.id = ANY (itsystem_uuids)
                            AND ((registrering_tstzrange IS NULL
                                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                        LEFT JOIN itsystem_attr_egenskaber AS b ON b.itsystem_registrering_id = a.itsystem_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.itsystem_id,
                            a.itsystem_registrering_id,
                            a.registrering) AS a
                    LEFT JOIN itsystem_tils_gyldighed AS b ON b.itsystem_registrering_id = a.itsystem_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.itsystem_id,
                        a.itsystem_registrering_id,
                        a.registrering,
                        a.ItsystemAttrEgenskaberArr) AS a
                LEFT JOIN itsystem_relation b ON b.itsystem_registrering_id = a.itsystem_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.itsystem_id,
                    a.itsystem_registrering_id,
                    a.registrering,
                    a.ItsystemAttrEgenskaberArr,
                    a.ItsystemTilsGyldighedArr) AS a
            WHERE
                a.itsystem_id IS NOT NULL
            GROUP BY
                a.itsystem_id
            ORDER BY
                a.itsystem_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_klassifikation (klassifikation_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(klassifikation_uuids, 1), 0) AND auth_filtered_uuids @> klassifikation_uuids) THEN
        RAISE EXCEPTION 'Unable to list klassifikation with uuids [%]. All objects do not fullfill the stipulated criteria:%', klassifikation_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.klassifikationObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.klassifikation_id,
                array_agg(ROW (a.registrering, a.KlassifikationTilsPubliceretArr, a.KlassifikationAttrEgenskaberArr, a.KlassifikationRelationArr)::KlassifikationRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::KlassifikationType klassifikationObj
        FROM (
            SELECT
                a.klassifikation_id,
                a.klassifikation_registrering_id,
                a.registrering,
                a.KlassifikationAttrEgenskaberArr,
                a.KlassifikationTilsPubliceretArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::KlassifikationRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) KlassifikationRelationArr
            FROM (
                SELECT
                    a.klassifikation_id,
                    a.klassifikation_registrering_id,
                    a.registrering,
                    a.KlassifikationAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.publiceret)::KlassifikationPubliceretTilsType
                            ELSE
                                NULL
                            END ORDER BY b.publiceret, b.virkning)) KlassifikationTilsPubliceretArr
                FROM (
                    SELECT
                        a.klassifikation_id,
                        a.klassifikation_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.beskrivelse, b.kaldenavn, b.ophavsret, b.virkning)::KlassifikationEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.beskrivelse, b.kaldenavn, b.ophavsret, b.virkning)) KlassifikationAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.id klassifikation_id,
                            b.id klassifikation_registrering_id,
                            b.registrering
                        FROM
                            klassifikation a
                            JOIN klassifikation_registrering b ON b.klassifikation_id = a.id
                        WHERE
                            a.id = ANY (klassifikation_uuids)
                            AND ((registrering_tstzrange IS NULL
                                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                        LEFT JOIN klassifikation_attr_egenskaber AS b ON b.klassifikation_registrering_id = a.klassifikation_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.klassifikation_id,
                            a.klassifikation_registrering_id,
                            a.registrering) AS a
                    LEFT JOIN klassifikation_tils_publiceret AS b ON b.klassifikation_registrering_id = a.klassifikation_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.klassifikation_id,
                        a.klassifikation_registrering_id,
                        a.registrering,
                        a.KlassifikationAttrEgenskaberArr) AS a
                LEFT JOIN klassifikation_relation b ON b.klassifikation_registrering_id = a.klassifikation_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.klassifikation_id,
                    a.klassifikation_registrering_id,
                    a.registrering,
                    a.KlassifikationAttrEgenskaberArr,
                    a.KlassifikationTilsPubliceretArr) AS a
            WHERE
                a.klassifikation_id IS NOT NULL
            GROUP BY
                a.klassifikation_id
            ORDER BY
                a.klassifikation_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_facet (facet_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(facet_uuids, 1), 0) AND auth_filtered_uuids @> facet_uuids) THEN
        RAISE EXCEPTION 'Unable to list facet with uuids [%]. All objects do not fullfill the stipulated criteria:%', facet_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.facetObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.facet_id,
                array_agg(ROW (a.registrering, a.FacetTilsPubliceretArr, a.FacetAttrEgenskaberArr, a.FacetRelationArr)::FacetRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::FacetType facetObj
        FROM (
            SELECT
                a.facet_id,
                a.facet_registrering_id,
                a.registrering,
                a.FacetAttrEgenskaberArr,
                a.FacetTilsPubliceretArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::FacetRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) FacetRelationArr
            FROM (
                SELECT
                    a.facet_id,
                    a.facet_registrering_id,
                    a.registrering,
                    a.FacetAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.publiceret)::FacetPubliceretTilsType
                            ELSE
                                NULL
                            END ORDER BY b.publiceret, b.virkning)) FacetTilsPubliceretArr
                FROM (
                    SELECT
                        a.facet_id,
                        a.facet_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.beskrivelse, b.opbygning, b.ophavsret, b.plan, b.supplement, b.retskilde, b.virkning)::FacetEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.beskrivelse, b.opbygning, b.ophavsret, b.plan, b.supplement, b.retskilde, b.virkning)) FacetAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.id facet_id,
                            b.id facet_registrering_id,
                            b.registrering
                        FROM
                            facet a
                            JOIN facet_registrering b ON b.facet_id = a.id
                        WHERE
                            a.id = ANY (facet_uuids)
                            AND ((registrering_tstzrange IS NULL
                                    AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                        LEFT JOIN facet_attr_egenskaber AS b ON b.facet_registrering_id = a.facet_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.facet_id,
                            a.facet_registrering_id,
                            a.registrering) AS a
                    LEFT JOIN facet_tils_publiceret AS b ON b.facet_registrering_id = a.facet_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.facet_id,
                        a.facet_registrering_id,
                        a.registrering,
                        a.FacetAttrEgenskaberArr) AS a
                LEFT JOIN facet_relation b ON b.facet_registrering_id = a.facet_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.facet_id,
                    a.facet_registrering_id,
                    a.registrering,
                    a.FacetAttrEgenskaberArr,
                    a.FacetTilsPubliceretArr) AS a
            WHERE
                a.facet_id IS NOT NULL
            GROUP BY
                a.facet_id
            ORDER BY
                a.facet_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_bruger (bruger_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(bruger_uuids, 1), 0) AND auth_filtered_uuids @> bruger_uuids) THEN
        RAISE EXCEPTION 'Unable to list bruger with uuids [%]. All objects do not fullfill the stipulated criteria:%', bruger_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.brugerObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.bruger_id,
                array_agg(ROW (a.registrering, a.BrugerTilsGyldighedArr, a.BrugerAttrEgenskaberArr, a.BrugerAttrUdvidelserArr, a.BrugerRelationArr)::BrugerRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::BrugerType brugerObj
        FROM (
            SELECT
                a.bruger_id,
                a.bruger_registrering_id,
                a.registrering,
                a.BrugerAttrEgenskaberArr,
                a.BrugerAttrUdvidelserArr,
                a.BrugerTilsGyldighedArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::BrugerRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) BrugerRelationArr
            FROM (
                SELECT
                    a.bruger_id,
                    a.bruger_registrering_id,
                    a.registrering,
                    a.BrugerAttrEgenskaberArr,
                    a.BrugerAttrUdvidelserArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.gyldighed)::BrugerGyldighedTilsType
                            ELSE
                                NULL
                            END ORDER BY b.gyldighed, b.virkning)) BrugerTilsGyldighedArr
                FROM (
                    SELECT
                        a.bruger_id,
                        a.bruger_registrering_id,
                        a.registrering,
                        a.BrugerAttrUdvidelserArr,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.brugernavn, b.brugertype, b.virkning)::BrugerEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.brugernavn, b.brugertype, b.virkning)) BrugerAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.bruger_id,
                            a.bruger_registrering_id,
                            a.registrering,
                            _remove_nulls_in_array (array_agg(
                                    CASE WHEN b.id IS NOT NULL THEN
                                        ROW (b.fornavn, b.efternavn, b.kaldenavn_fornavn, b.kaldenavn_efternavn, b.seniority, b.virkning)::BrugerUdvidelserAttrType
                                    ELSE
                                        NULL
                                    END ORDER BY b.fornavn, b.efternavn, b.kaldenavn_fornavn, b.kaldenavn_efternavn, b.seniority, b.virkning)) BrugerAttrUdvidelserArr
                        FROM (
                            SELECT
                                a.id bruger_id,
                                b.id bruger_registrering_id,
                                b.registrering
                            FROM
                                bruger a
                                JOIN bruger_registrering b ON b.bruger_id = a.id
                            WHERE
                                a.id = ANY (bruger_uuids)
                                AND ((registrering_tstzrange IS NULL
                                        AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                    OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                            LEFT JOIN bruger_attr_udvidelser AS b ON b.bruger_registrering_id = a.bruger_registrering_id
                                AND (virkning_tstzrange IS NULL
                                    OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                            GROUP BY
                                a.bruger_id,
                                a.bruger_registrering_id,
                                a.registrering) AS a
                        LEFT JOIN bruger_attr_egenskaber AS b ON b.bruger_registrering_id = a.bruger_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.bruger_id,
                            a.bruger_registrering_id,
                            a.registrering,
                            a.BrugerAttrUdvidelserArr) AS a
                    LEFT JOIN bruger_tils_gyldighed AS b ON b.bruger_registrering_id = a.bruger_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.bruger_id,
                        a.bruger_registrering_id,
                        a.registrering,
                        a.BrugerAttrUdvidelserArr,
                        a.BrugerAttrEgenskaberArr) AS a
                LEFT JOIN bruger_relation b ON b.bruger_registrering_id = a.bruger_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.bruger_id,
                    a.bruger_registrering_id,
                    a.registrering,
                    a.BrugerAttrUdvidelserArr,
                    a.BrugerAttrEgenskaberArr,
                    a.BrugerTilsGyldighedArr) AS a
            WHERE
                a.bruger_id IS NOT NULL
            GROUP BY
                a.bruger_id
            ORDER BY
                a.bruger_id) AS x;
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
    /*** Verify that the object meets the stipulated access allowed criteria  ***/
    auth_filtered_uuids := _as_filter_unauth_klasse (klasse_uuids, auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = coalesce(array_length(klasse_uuids, 1), 0) AND auth_filtered_uuids @> klasse_uuids) THEN
        RAISE EXCEPTION 'Unable to list klasse with uuids [%]. All objects do not fullfill the stipulated criteria:%', klasse_uuids, to_json(auth_criteria_arr)
            USING ERRCODE = 'MO401';
    END IF;

    /*********************/
    SELECT
        array_agg(x.klasseObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.klasse_id,
                array_agg(ROW (a.registrering, a.KlasseTilsPubliceretArr, a.KlasseAttrEgenskaberArr, a.KlasseRelationArr)::KlasseRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::KlasseType klasseObj
        FROM (
            SELECT
                a.klasse_id,
                a.klasse_registrering_id,
                a.registrering,
                a.KlasseAttrEgenskaberArr,
                a.KlasseTilsPubliceretArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::KlasseRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) KlasseRelationArr
            FROM (
                SELECT
                    a.klasse_id,
                    a.klasse_registrering_id,
                    a.registrering,
                    a.KlasseAttrEgenskaberArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.publiceret)::KlassePubliceretTilsType
                            ELSE
                                NULL
                            END ORDER BY b.publiceret, b.virkning)) KlasseTilsPubliceretArr
                FROM (
                    SELECT
                        a.klasse_id,
                        a.klasse_registrering_id,
                        a.registrering,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN a.attr_id IS NOT NULL THEN
                                    ROW (a.brugervendtnoegle, a.beskrivelse, a.eksempel, a.omfang, a.titel, a.retskilde, a.aendringsnotat, a.KlasseAttrEgenskaberSoegeordTypeArr, a.virkning)::KlasseEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY a.brugervendtnoegle, a.beskrivelse, a.eksempel, a.omfang, a.titel, a.retskilde, a.aendringsnotat, a.virkning, a.KlasseAttrEgenskaberSoegeordTypeArr)) KlasseAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.klasse_id,
                            a.klasse_registrering_id,
                            a.registrering,
                            b.id attr_id,
                            b.brugervendtnoegle,
                            b.beskrivelse,
                            b.eksempel,
                            b.omfang,
                            b.titel,
                            b.retskilde,
                            b.aendringsnotat,
                            b.virkning,
                            _remove_nulls_in_array (array_agg(
                                    CASE WHEN c.id IS NOT NULL THEN
                                        ROW (c.soegeordidentifikator, c.beskrivelse, c.soegeordskategori)::KlasseSoegeordType
                                    ELSE
                                        NULL
                                    END ORDER BY c.soegeordidentifikator, c.beskrivelse, c.soegeordskategori)) KlasseAttrEgenskaberSoegeordTypeArr
                        FROM (
                            SELECT
                                a.id klasse_id,
                                b.id klasse_registrering_id,
                                b.registrering
                            FROM
                                klasse a
                                JOIN klasse_registrering b ON b.klasse_id = a.id
                            WHERE
                                a.id = ANY (klasse_uuids)
                                AND ((registrering_tstzrange IS NULL
                                        AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                    OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                            LEFT JOIN klasse_attr_egenskaber AS b ON b.klasse_registrering_id = a.klasse_registrering_id
                                AND (virkning_tstzrange IS NULL
                                    OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                            LEFT JOIN klasse_attr_egenskaber_soegeord AS c ON c.klasse_attr_egenskaber_id = b.id
                        GROUP BY
                            a.klasse_id,
                            a.klasse_registrering_id,
                            a.registrering,
                            b.id,
                            b.brugervendtnoegle,
                            b.beskrivelse,
                            b.eksempel,
                            b.omfang,
                            b.titel,
                            b.retskilde,
                            b.aendringsnotat,
                            b.virkning) AS a
                    GROUP BY
                        a.klasse_id,
                        a.klasse_registrering_id,
                        a.registrering) AS a
                LEFT JOIN klasse_tils_publiceret AS b ON b.klasse_registrering_id = a.klasse_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.klasse_id,
                    a.klasse_registrering_id,
                    a.registrering,
                    a.KlasseAttrEgenskaberArr) AS a
            LEFT JOIN klasse_relation b ON b.klasse_registrering_id = a.klasse_registrering_id
                AND (virkning_tstzrange IS NULL
                    OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
            GROUP BY
                a.klasse_id,
                a.klasse_registrering_id,
                a.registrering,
                a.KlasseAttrEgenskaberArr,
                a.KlasseTilsPubliceretArr) AS a
        WHERE
            a.klasse_id IS NOT NULL
        GROUP BY
            a.klasse_id
        ORDER BY
            a.klasse_id) AS x;
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
    SELECT
        array_agg(x.organisationfunktionObj)
    INTO
        result
    FROM (
        SELECT
            ROW (a.organisationfunktion_id,
                array_agg(ROW (a.registrering, a.OrganisationfunktionTilsGyldighedArr, a.OrganisationfunktionAttrEgenskaberArr, a.OrganisationfunktionAttrUdvidelserArr, a.OrganisationfunktionRelationArr)::OrganisationfunktionRegistreringType ORDER BY upper((a.registrering).TimePeriod) DESC))::OrganisationfunktionType organisationfunktionObj
        FROM (
            SELECT
                a.organisationfunktion_id,
                a.organisationfunktion_registrering_id,
                a.registrering,
                a.OrganisationfunktionAttrEgenskaberArr,
                a.OrganisationfunktionAttrUdvidelserArr,
                a.OrganisationfunktionTilsGyldighedArr,
                _remove_nulls_in_array (array_agg(
                        CASE WHEN b.id IS NOT NULL THEN
                            ROW (b.rel_type, b.virkning, b.rel_maal_uuid, b.rel_maal_urn, b.objekt_type)::OrganisationfunktionRelationType
                        ELSE
                            NULL
                        END ORDER BY b.rel_maal_uuid, b.rel_maal_urn, b.rel_type, b.objekt_type, b.virkning)) OrganisationfunktionRelationArr
            FROM (
                SELECT
                    a.organisationfunktion_id,
                    a.organisationfunktion_registrering_id,
                    a.registrering,
                    a.OrganisationfunktionAttrEgenskaberArr,
                    a.OrganisationfunktionAttrUdvidelserArr,
                    _remove_nulls_in_array (array_agg(
                            CASE WHEN b.id IS NOT NULL THEN
                                ROW (b.virkning, b.gyldighed)::OrganisationfunktionGyldighedTilsType
                            ELSE
                                NULL
                            END ORDER BY b.gyldighed, b.virkning)) OrganisationfunktionTilsGyldighedArr
                FROM (
                    SELECT
                        a.organisationfunktion_id,
                        a.organisationfunktion_registrering_id,
                        a.registrering,
                        a.OrganisationfunktionAttrUdvidelserArr,
                        _remove_nulls_in_array (array_agg(
                                CASE WHEN b.id IS NOT NULL THEN
                                    ROW (b.brugervendtnoegle, b.funktionsnavn, b.virkning)::OrganisationfunktionEgenskaberAttrType
                                ELSE
                                    NULL
                                END ORDER BY b.brugervendtnoegle, b.funktionsnavn, b.virkning)) OrganisationfunktionAttrEgenskaberArr
                    FROM (
                        SELECT
                            a.organisationfunktion_id,
                            a.organisationfunktion_registrering_id,
                            a.registrering,
                            _remove_nulls_in_array (array_agg(
                                    CASE WHEN b.id IS NOT NULL THEN
                                        ROW (b.primær, b.fraktion, b.udvidelse_1, b.udvidelse_2, b.udvidelse_3, b.udvidelse_4, b.udvidelse_5, b.udvidelse_6, b.udvidelse_7, b.udvidelse_8, b.udvidelse_9, b.udvidelse_10, b.virkning)::OrganisationfunktionUdvidelserAttrType
                                    ELSE
                                        NULL
                                    END ORDER BY b.primær, b.fraktion, b.udvidelse_1, b.udvidelse_2, b.udvidelse_3, b.udvidelse_4, b.udvidelse_5, b.udvidelse_6, b.udvidelse_7, b.udvidelse_8, b.udvidelse_9, b.udvidelse_10, b.virkning)) OrganisationfunktionAttrUdvidelserArr
                        FROM (
                            SELECT
                                a.id organisationfunktion_id,
                                b.id organisationfunktion_registrering_id,
                                b.registrering
                            FROM
                                organisationfunktion a
                                JOIN organisationfunktion_registrering b ON b.organisationfunktion_id = a.id
                            WHERE
                                a.id = ANY (organisationfunktion_uuids)
                                AND ((registrering_tstzrange IS NULL
                                        AND upper((b.registrering).timeperiod) = 'infinity'::timestamptz)
                                    OR registrering_tstzrange && (b.registrering).timeperiod) --filter ON registrering_tstzrange
) AS a
                            LEFT JOIN organisationfunktion_attr_udvidelser AS b ON b.organisationfunktion_registrering_id = a.organisationfunktion_registrering_id
                                AND (virkning_tstzrange IS NULL
                                    OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                            GROUP BY
                                a.organisationfunktion_id,
                                a.organisationfunktion_registrering_id,
                                a.registrering) AS a
                        LEFT JOIN organisationfunktion_attr_egenskaber AS b ON b.organisationfunktion_registrering_id = a.organisationfunktion_registrering_id
                            AND (virkning_tstzrange IS NULL
                                OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                        GROUP BY
                            a.organisationfunktion_id,
                            a.organisationfunktion_registrering_id,
                            a.registrering,
                            a.OrganisationfunktionAttrUdvidelserArr) AS a
                    LEFT JOIN organisationfunktion_tils_gyldighed AS b ON b.organisationfunktion_registrering_id = a.organisationfunktion_registrering_id
                        AND (virkning_tstzrange IS NULL
                            OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                    GROUP BY
                        a.organisationfunktion_id,
                        a.organisationfunktion_registrering_id,
                        a.registrering,
                        a.OrganisationfunktionAttrUdvidelserArr,
                        a.OrganisationfunktionAttrEgenskaberArr) AS a
                LEFT JOIN organisationfunktion_relation b ON b.organisationfunktion_registrering_id = a.organisationfunktion_registrering_id
                    AND (virkning_tstzrange IS NULL
                        OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
                GROUP BY
                    a.organisationfunktion_id,
                    a.organisationfunktion_registrering_id,
                    a.registrering,
                    a.OrganisationfunktionAttrUdvidelserArr,
                    a.OrganisationfunktionAttrEgenskaberArr,
                    a.OrganisationfunktionTilsGyldighedArr) AS a
            WHERE
                a.organisationfunktion_id IS NOT NULL
            GROUP BY
                a.organisationfunktion_id
            ORDER BY
                a.organisationfunktion_id) AS x;
    RETURN result;
END;
$function$
;
