-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of BrugerAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_bruger(
    bruger_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber BrugerEgenskaberAttrType[],
    
    attrUdvidelser BrugerUdvidelserAttrType[],
    

    
    tilsGyldighed BrugerGyldighedTilsType[],
    

    relationer BrugerRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      BrugerRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_bruger          BrugerType;
    read_prev_bruger         BrugerType;
    read_new_bruger_reg      BrugerRegistreringType;
    read_prev_bruger_reg     BrugerRegistreringType;
    new_bruger_registrering  bruger_registrering;
    prev_bruger_registrering bruger_registrering;
    bruger_relation_navn     BrugerRelationKode;

    
    attrEgenskaberObj BrugerEgenskaberAttrType;
    
    attrUdvidelserObj BrugerUdvidelserAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from bruger a join bruger_registrering b ON b.bruger_id=a.id WHERE a.id=bruger_uuid) THEN
        RAISE EXCEPTION 'Unable to update bruger with uuid [%], being unable to find any previous registrations.',bruger_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM bruger a WHERE a.id=bruger_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_bruger(array[bruger_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[bruger_uuid]) THEN
      RAISE EXCEPTION 'Unable to update bruger with uuid [%]. Object does not met stipulated criteria:%', bruger_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_bruger_registrering := _as_create_bruger_registrering(bruger_uuid, livscykluskode, brugerref, note);
    prev_bruger_registrering := _as_get_prev_bruger_registrering(new_bruger_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_bruger_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update bruger with uuid [%], as the bruger seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', bruger_uuid, lostUpdatePreventionTZ, LOWER((prev_bruger_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO bruger_relation (bruger_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_bruger_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH bruger_relation_navn IN ARRAY ARRAY['tilhoerer'::BrugerRelationKode  ]::BrugerRelationKode[]  LOOP
        INSERT INTO bruger_relation (bruger_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_bruger_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM bruger_relation b
                 WHERE b.bruger_registrering_id = new_bruger_registrering.id AND b.rel_type = bruger_relation_navn) d
            JOIN bruger_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.bruger_registrering_id = prev_bruger_registrering.id AND a.rel_type = bruger_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH bruger_relation_navn IN ARRAY ARRAY['adresser'::BrugerRelationKode, 'brugertyper'::BrugerRelationKode, 'opgaver'::BrugerRelationKode, 'tilknyttedeenheder'::BrugerRelationKode, 'tilknyttedefunktioner'::BrugerRelationKode, 'tilknyttedeinteressefaellesskaber'::BrugerRelationKode, 'tilknyttedeorganisationer'::BrugerRelationKode, 'tilknyttedepersoner'::BrugerRelationKode, 'tilknyttedeitsystemer'::BrugerRelationKode]::BrugerRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM bruger_relation
                     WHERE bruger_registrering_id = new_bruger_registrering.id AND rel_type = bruger_relation_navn) THEN
                    
                    INSERT INTO bruger_relation (bruger_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_bruger_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM bruger_relation
        WHERE
            bruger_registrering_id = prev_bruger_registrering.id AND rel_type = bruger_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsGyldighed IS NOT NULL AND coalesce(array_length(tilsGyldighed, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Gyldighed] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- bruger_tils_gyldighed

        -- Ad 1)
        INSERT INTO bruger_tils_gyldighed(virkning, gyldighed, bruger_registrering_id)
             SELECT a.virkning, a.gyldighed, new_bruger_registrering.id
               FROM unnest(tilsGyldighed) AS a;

        -- Ad 2
        INSERT INTO bruger_tils_gyldighed(virkning, gyldighed, bruger_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.gyldighed,
            new_bruger_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- bruger_tils_gyldighed of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- bruger_tils_gyldighed of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM bruger_tils_gyldighed b
             WHERE b.bruger_registrering_id = new_bruger_registrering.id) d
              JOIN bruger_tils_gyldighed a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.bruger_registrering_id = prev_bruger_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- bruger_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrBrugerObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.brugernavn,a.brugertype,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update bruger with uuid [%], as the bruger have overlapping virknings in the given egenskaber array :%', bruger_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).brugernavn IS NULL  OR  (attrEgenskaberObj).brugertype IS NULL  THEN
            
            INSERT INTO bruger_attr_egenskaber ( brugervendtnoegle,brugernavn,brugertype, virkning, bruger_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugernavn, a.brugernavn),
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugertype, a.brugertype),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_bruger_registrering.id
                        FROM bruger_attr_egenskaber a
                    WHERE
                        a.bruger_registrering_id = prev_bruger_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO bruger_attr_egenskaber ( brugervendtnoegle,brugernavn,brugertype, virkning, bruger_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.brugernavn,
                    
                     attrEgenskaberObj.brugertype,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_bruger_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the bruger_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM bruger_attr_egenskaber b
                    WHERE b.bruger_registrering_id = new_bruger_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO bruger_attr_egenskaber ( brugervendtnoegle,brugernavn,brugertype, virkning, bruger_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.brugernavn,  attrEgenskaberObj.brugertype, attrEgenskaberObj.virkning, new_bruger_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO bruger_attr_egenskaber ( brugervendtnoegle,brugernavn,brugertype, virkning, bruger_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.brugernavn,
        
            a.brugertype,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_bruger_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- bruger_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- bruger_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                bruger_attr_egenskaber b
            WHERE
                b.bruger_registrering_id = new_bruger_registrering.id) d
            JOIN bruger_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.bruger_registrering_id = prev_bruger_registrering.id ;

END IF;

    -- bruger_attr_udvidelser

    -- Generate and insert any merged objects, if any fields are null
    -- in attrBrugerObj
    IF attrUdvidelser IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrUdvidelser) a
                    JOIN unnest(attrUdvidelser) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.fornavn,a.efternavn,a.kaldenavn_fornavn,a.kaldenavn_efternavn,a.seniority,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update bruger with uuid [%], as the bruger have overlapping virknings in the given udvidelser array :%', bruger_uuid, to_json(attrUdvidelser) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrUdvidelserObj IN ARRAY attrUdvidelser LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrUdvidelserObj).fornavn IS NULL  OR  (attrUdvidelserObj).efternavn IS NULL  OR  (attrUdvidelserObj).kaldenavn_fornavn IS NULL  OR  (attrUdvidelserObj).kaldenavn_efternavn IS NULL  OR  (attrUdvidelserObj).seniority IS NULL  THEN
            
            INSERT INTO bruger_attr_udvidelser ( fornavn,efternavn,kaldenavn_fornavn,kaldenavn_efternavn,seniority, virkning, bruger_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrUdvidelserObj.fornavn, a.fornavn),
                    
                        
                        
                            coalesce(attrUdvidelserObj.efternavn, a.efternavn),
                    
                        
                        
                            coalesce(attrUdvidelserObj.kaldenavn_fornavn, a.kaldenavn_fornavn),
                    
                        
                        
                            coalesce(attrUdvidelserObj.kaldenavn_efternavn, a.kaldenavn_efternavn),
                    
                        
                        
                            coalesce(attrUdvidelserObj.seniority, a.seniority),
                    
                    ROW ((a.virkning).TimePeriod * (attrUdvidelserObj.virkning).TimePeriod,
                            (attrUdvidelserObj.virkning).AktoerRef,
                            (attrUdvidelserObj.virkning).AktoerTypeKode,
                            (attrUdvidelserObj.virkning).NoteTekst)::Virkning,
                            new_bruger_registrering.id
                        FROM bruger_attr_udvidelser a
                    WHERE
                        a.bruger_registrering_id = prev_bruger_registrering.id
                        AND (a.virkning).TimePeriod && (attrUdvidelserObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrUdvidelserObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO bruger_attr_udvidelser ( fornavn,efternavn,kaldenavn_fornavn,kaldenavn_efternavn,seniority, virkning, bruger_registrering_id)
                SELECT
                    
                     attrUdvidelserObj.fornavn,
                    
                     attrUdvidelserObj.efternavn,
                    
                     attrUdvidelserObj.kaldenavn_fornavn,
                    
                     attrUdvidelserObj.kaldenavn_efternavn,
                    
                     attrUdvidelserObj.seniority,
                    
                    ROW (b.tz_range_leftover,
                        (attrUdvidelserObj.virkning).AktoerRef,
                        (attrUdvidelserObj.virkning).AktoerTypeKode,
                        (attrUdvidelserObj.virkning).NoteTekst)::Virkning,
                        new_bruger_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the bruger_attr_udvidelser of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM bruger_attr_udvidelser b
                    WHERE b.bruger_registrering_id = new_bruger_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrUdvidelserObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrUdvidelserObj raw (if there were no null-valued fields)
            

            INSERT INTO bruger_attr_udvidelser ( fornavn,efternavn,kaldenavn_fornavn,kaldenavn_efternavn,seniority, virkning, bruger_registrering_id)
                VALUES (  attrUdvidelserObj.fornavn,  attrUdvidelserObj.efternavn,  attrUdvidelserObj.kaldenavn_fornavn,  attrUdvidelserObj.kaldenavn_efternavn,  attrUdvidelserObj.seniority, attrUdvidelserObj.virkning, new_bruger_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrUdvidelser IS NOT NULL AND coalesce(array_length(attrUdvidelser, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of udvidelser of previous registration as an empty array was explicit given.';
        ELSE



-- Handle udvidelser of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO bruger_attr_udvidelser ( fornavn,efternavn,kaldenavn_fornavn,kaldenavn_efternavn,seniority, virkning, bruger_registrering_id)
    SELECT
        
        
            a.fornavn,
        
            a.efternavn,
        
            a.kaldenavn_fornavn,
        
            a.kaldenavn_efternavn,
        
            a.seniority,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_bruger_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- bruger_attr_udvidelser of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- bruger_attr_udvidelser of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                bruger_attr_udvidelser b
            WHERE
                b.bruger_registrering_id = new_bruger_registrering.id) d
            JOIN bruger_attr_udvidelser a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.bruger_registrering_id = prev_bruger_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_bruger := as_read_bruger(bruger_uuid, (new_bruger_registrering.registrering).timeperiod, null);
    read_prev_bruger := as_read_bruger(bruger_uuid, (prev_bruger_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_bruger.registrering[1].registrering).TimePeriod) = lower((new_bruger_registrering.registrering).TimePeriod) and lower((read_prev_bruger.registrering[1].registrering).TimePeriod)=lower((prev_bruger_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating bruger with id [%]: The ordering of as_list_bruger should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', bruger_uuid, to_json(new_bruger_registrering), to_json(read_new_bruger.registrering[1].registrering), to_json(prev_bruger_registrering), to_json(prev_new_bruger.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_bruger_reg := ROW(
        ROW (null, (read_new_bruger.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_bruger.registrering[1]).tilsGyldighed ,
        
        (read_new_bruger.registrering[1]).attrEgenskaber ,
        (read_new_bruger.registrering[1]).attrUdvidelser ,
        (read_new_bruger.registrering[1]).relationer
    )::brugerRegistreringType;

    read_prev_bruger_reg := ROW(
        ROW(null, (read_prev_bruger.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_bruger.registrering[1]).tilsGyldighed ,
        
        (read_prev_bruger.registrering[1]).attrEgenskaber ,
        (read_prev_bruger.registrering[1]).attrUdvidelser ,
        (read_prev_bruger.registrering[1]).relationer
    )::brugerRegistreringType;


    IF read_prev_bruger_reg = read_new_bruger_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_bruger_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_bruger_reg);
      RAISE NOTICE 'Aborted updating bruger with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', bruger_uuid, to_json(read_new_bruger_reg), to_json(read_prev_bruger_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_bruger_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of FacetAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_facet(
    facet_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber FacetEgenskaberAttrType[],
    

    
    tilsPubliceret FacetPubliceretTilsType[],
    

    relationer FacetRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      FacetRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_facet          FacetType;
    read_prev_facet         FacetType;
    read_new_facet_reg      FacetRegistreringType;
    read_prev_facet_reg     FacetRegistreringType;
    new_facet_registrering  facet_registrering;
    prev_facet_registrering facet_registrering;
    facet_relation_navn     FacetRelationKode;

    
    attrEgenskaberObj FacetEgenskaberAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from facet a join facet_registrering b ON b.facet_id=a.id WHERE a.id=facet_uuid) THEN
        RAISE EXCEPTION 'Unable to update facet with uuid [%], being unable to find any previous registrations.',facet_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM facet a WHERE a.id=facet_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_facet(array[facet_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[facet_uuid]) THEN
      RAISE EXCEPTION 'Unable to update facet with uuid [%]. Object does not met stipulated criteria:%', facet_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_facet_registrering := _as_create_facet_registrering(facet_uuid, livscykluskode, brugerref, note);
    prev_facet_registrering := _as_get_prev_facet_registrering(new_facet_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_facet_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update facet with uuid [%], as the facet seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', facet_uuid, lostUpdatePreventionTZ, LOWER((prev_facet_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO facet_relation (facet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_facet_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH facet_relation_navn IN ARRAY ARRAY['ansvarlig'::FacetRelationKode ,  'ejer'::FacetRelationKode ,  'facettilhoerer'::FacetRelationKode  ]::FacetRelationKode[]  LOOP
        INSERT INTO facet_relation (facet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_facet_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM facet_relation b
                 WHERE b.facet_registrering_id = new_facet_registrering.id AND b.rel_type = facet_relation_navn) d
            JOIN facet_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.facet_registrering_id = prev_facet_registrering.id AND a.rel_type = facet_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH facet_relation_navn IN ARRAY ARRAY['redaktoerer'::FacetRelationKode]::FacetRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM facet_relation
                     WHERE facet_registrering_id = new_facet_registrering.id AND rel_type = facet_relation_navn) THEN
                    
                    INSERT INTO facet_relation (facet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_facet_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM facet_relation
        WHERE
            facet_registrering_id = prev_facet_registrering.id AND rel_type = facet_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsPubliceret IS NOT NULL AND coalesce(array_length(tilsPubliceret, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Publiceret] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- facet_tils_publiceret

        -- Ad 1)
        INSERT INTO facet_tils_publiceret(virkning, publiceret, facet_registrering_id)
             SELECT a.virkning, a.publiceret, new_facet_registrering.id
               FROM unnest(tilsPubliceret) AS a;

        -- Ad 2
        INSERT INTO facet_tils_publiceret(virkning, publiceret, facet_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.publiceret,
            new_facet_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- facet_tils_publiceret of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- facet_tils_publiceret of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM facet_tils_publiceret b
             WHERE b.facet_registrering_id = new_facet_registrering.id) d
              JOIN facet_tils_publiceret a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.facet_registrering_id = prev_facet_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- facet_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrFacetObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.beskrivelse,a.opbygning,a.ophavsret,a.plan,a.supplement,a.retskilde,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update facet with uuid [%], as the facet have overlapping virknings in the given egenskaber array :%', facet_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).beskrivelse IS NULL  OR  (attrEgenskaberObj).opbygning IS NULL  OR  (attrEgenskaberObj).ophavsret IS NULL  OR  (attrEgenskaberObj).plan IS NULL  OR  (attrEgenskaberObj).supplement IS NULL  OR  (attrEgenskaberObj).retskilde IS NULL  THEN
            
            INSERT INTO facet_attr_egenskaber ( brugervendtnoegle,beskrivelse,opbygning,ophavsret,plan,supplement,retskilde, virkning, facet_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.beskrivelse, a.beskrivelse),
                    
                        
                        
                            coalesce(attrEgenskaberObj.opbygning, a.opbygning),
                    
                        
                        
                            coalesce(attrEgenskaberObj.ophavsret, a.ophavsret),
                    
                        
                        
                            coalesce(attrEgenskaberObj.plan, a.plan),
                    
                        
                        
                            coalesce(attrEgenskaberObj.supplement, a.supplement),
                    
                        
                        
                            coalesce(attrEgenskaberObj.retskilde, a.retskilde),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_facet_registrering.id
                        FROM facet_attr_egenskaber a
                    WHERE
                        a.facet_registrering_id = prev_facet_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO facet_attr_egenskaber ( brugervendtnoegle,beskrivelse,opbygning,ophavsret,plan,supplement,retskilde, virkning, facet_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.beskrivelse,
                    
                     attrEgenskaberObj.opbygning,
                    
                     attrEgenskaberObj.ophavsret,
                    
                     attrEgenskaberObj.plan,
                    
                     attrEgenskaberObj.supplement,
                    
                     attrEgenskaberObj.retskilde,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_facet_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the facet_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM facet_attr_egenskaber b
                    WHERE b.facet_registrering_id = new_facet_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO facet_attr_egenskaber ( brugervendtnoegle,beskrivelse,opbygning,ophavsret,plan,supplement,retskilde, virkning, facet_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.opbygning,  attrEgenskaberObj.ophavsret,  attrEgenskaberObj.plan,  attrEgenskaberObj.supplement,  attrEgenskaberObj.retskilde, attrEgenskaberObj.virkning, new_facet_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO facet_attr_egenskaber ( brugervendtnoegle,beskrivelse,opbygning,ophavsret,plan,supplement,retskilde, virkning, facet_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.beskrivelse,
        
            a.opbygning,
        
            a.ophavsret,
        
            a.plan,
        
            a.supplement,
        
            a.retskilde,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_facet_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- facet_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- facet_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                facet_attr_egenskaber b
            WHERE
                b.facet_registrering_id = new_facet_registrering.id) d
            JOIN facet_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.facet_registrering_id = prev_facet_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_facet := as_read_facet(facet_uuid, (new_facet_registrering.registrering).timeperiod, null);
    read_prev_facet := as_read_facet(facet_uuid, (prev_facet_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_facet.registrering[1].registrering).TimePeriod) = lower((new_facet_registrering.registrering).TimePeriod) and lower((read_prev_facet.registrering[1].registrering).TimePeriod)=lower((prev_facet_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating facet with id [%]: The ordering of as_list_facet should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', facet_uuid, to_json(new_facet_registrering), to_json(read_new_facet.registrering[1].registrering), to_json(prev_facet_registrering), to_json(prev_new_facet.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_facet_reg := ROW(
        ROW (null, (read_new_facet.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_facet.registrering[1]).tilsPubliceret ,
        
        (read_new_facet.registrering[1]).attrEgenskaber ,
        (read_new_facet.registrering[1]).relationer
    )::facetRegistreringType;

    read_prev_facet_reg := ROW(
        ROW(null, (read_prev_facet.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_facet.registrering[1]).tilsPubliceret ,
        
        (read_prev_facet.registrering[1]).attrEgenskaber ,
        (read_prev_facet.registrering[1]).relationer
    )::facetRegistreringType;


    IF read_prev_facet_reg = read_new_facet_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_facet_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_facet_reg);
      RAISE NOTICE 'Aborted updating facet with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', facet_uuid, to_json(read_new_facet_reg), to_json(read_prev_facet_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_facet_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of ItsystemAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_itsystem(
    itsystem_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber ItsystemEgenskaberAttrType[],
    

    
    tilsGyldighed ItsystemGyldighedTilsType[],
    

    relationer ItsystemRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      ItsystemRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_itsystem          ItsystemType;
    read_prev_itsystem         ItsystemType;
    read_new_itsystem_reg      ItsystemRegistreringType;
    read_prev_itsystem_reg     ItsystemRegistreringType;
    new_itsystem_registrering  itsystem_registrering;
    prev_itsystem_registrering itsystem_registrering;
    itsystem_relation_navn     ItsystemRelationKode;

    
    attrEgenskaberObj ItsystemEgenskaberAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from itsystem a join itsystem_registrering b ON b.itsystem_id=a.id WHERE a.id=itsystem_uuid) THEN
        RAISE EXCEPTION 'Unable to update itsystem with uuid [%], being unable to find any previous registrations.',itsystem_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM itsystem a WHERE a.id=itsystem_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_itsystem(array[itsystem_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[itsystem_uuid]) THEN
      RAISE EXCEPTION 'Unable to update itsystem with uuid [%]. Object does not met stipulated criteria:%', itsystem_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_itsystem_registrering := _as_create_itsystem_registrering(itsystem_uuid, livscykluskode, brugerref, note);
    prev_itsystem_registrering := _as_get_prev_itsystem_registrering(new_itsystem_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_itsystem_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update itsystem with uuid [%], as the itsystem seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', itsystem_uuid, lostUpdatePreventionTZ, LOWER((prev_itsystem_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO itsystem_relation (itsystem_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_itsystem_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH itsystem_relation_navn IN ARRAY ARRAY['tilhoerer'::ItsystemRelationKode  ]::ItsystemRelationKode[]  LOOP
        INSERT INTO itsystem_relation (itsystem_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_itsystem_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM itsystem_relation b
                 WHERE b.itsystem_registrering_id = new_itsystem_registrering.id AND b.rel_type = itsystem_relation_navn) d
            JOIN itsystem_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.itsystem_registrering_id = prev_itsystem_registrering.id AND a.rel_type = itsystem_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH itsystem_relation_navn IN ARRAY ARRAY['tilknyttedeorganisationer'::ItsystemRelationKode, 'tilknyttedeenheder'::ItsystemRelationKode, 'tilknyttedefunktioner'::ItsystemRelationKode, 'tilknyttedebrugere'::ItsystemRelationKode, 'tilknyttedeinteressefaellesskaber'::ItsystemRelationKode, 'tilknyttedeitsystemer'::ItsystemRelationKode, 'tilknyttedepersoner'::ItsystemRelationKode, 'systemtyper'::ItsystemRelationKode, 'opgaver'::ItsystemRelationKode, 'adresser'::ItsystemRelationKode]::ItsystemRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM itsystem_relation
                     WHERE itsystem_registrering_id = new_itsystem_registrering.id AND rel_type = itsystem_relation_navn) THEN
                    
                    INSERT INTO itsystem_relation (itsystem_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_itsystem_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM itsystem_relation
        WHERE
            itsystem_registrering_id = prev_itsystem_registrering.id AND rel_type = itsystem_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsGyldighed IS NOT NULL AND coalesce(array_length(tilsGyldighed, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Gyldighed] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- itsystem_tils_gyldighed

        -- Ad 1)
        INSERT INTO itsystem_tils_gyldighed(virkning, gyldighed, itsystem_registrering_id)
             SELECT a.virkning, a.gyldighed, new_itsystem_registrering.id
               FROM unnest(tilsGyldighed) AS a;

        -- Ad 2
        INSERT INTO itsystem_tils_gyldighed(virkning, gyldighed, itsystem_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.gyldighed,
            new_itsystem_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- itsystem_tils_gyldighed of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- itsystem_tils_gyldighed of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM itsystem_tils_gyldighed b
             WHERE b.itsystem_registrering_id = new_itsystem_registrering.id) d
              JOIN itsystem_tils_gyldighed a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.itsystem_registrering_id = prev_itsystem_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- itsystem_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrItsystemObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.itsystemnavn,a.itsystemtype,a.konfigurationreference,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update itsystem with uuid [%], as the itsystem have overlapping virknings in the given egenskaber array :%', itsystem_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).itsystemnavn IS NULL  OR  (attrEgenskaberObj).itsystemtype IS NULL  OR  (attrEgenskaberObj).konfigurationreference IS NULL  THEN
            
            INSERT INTO itsystem_attr_egenskaber ( brugervendtnoegle,itsystemnavn,itsystemtype,konfigurationreference, virkning, itsystem_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.itsystemnavn, a.itsystemnavn),
                    
                        
                        
                            coalesce(attrEgenskaberObj.itsystemtype, a.itsystemtype),
                    
                        
                        
                            coalesce(attrEgenskaberObj.konfigurationreference, a.konfigurationreference),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_itsystem_registrering.id
                        FROM itsystem_attr_egenskaber a
                    WHERE
                        a.itsystem_registrering_id = prev_itsystem_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO itsystem_attr_egenskaber ( brugervendtnoegle,itsystemnavn,itsystemtype,konfigurationreference, virkning, itsystem_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.itsystemnavn,
                    
                     attrEgenskaberObj.itsystemtype,
                    
                     attrEgenskaberObj.konfigurationreference,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_itsystem_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the itsystem_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM itsystem_attr_egenskaber b
                    WHERE b.itsystem_registrering_id = new_itsystem_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO itsystem_attr_egenskaber ( brugervendtnoegle,itsystemnavn,itsystemtype,konfigurationreference, virkning, itsystem_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.itsystemnavn,  attrEgenskaberObj.itsystemtype,  attrEgenskaberObj.konfigurationreference, attrEgenskaberObj.virkning, new_itsystem_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO itsystem_attr_egenskaber ( brugervendtnoegle,itsystemnavn,itsystemtype,konfigurationreference, virkning, itsystem_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.itsystemnavn,
        
            a.itsystemtype,
        
            a.konfigurationreference,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_itsystem_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- itsystem_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- itsystem_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                itsystem_attr_egenskaber b
            WHERE
                b.itsystem_registrering_id = new_itsystem_registrering.id) d
            JOIN itsystem_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.itsystem_registrering_id = prev_itsystem_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_itsystem := as_read_itsystem(itsystem_uuid, (new_itsystem_registrering.registrering).timeperiod, null);
    read_prev_itsystem := as_read_itsystem(itsystem_uuid, (prev_itsystem_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_itsystem.registrering[1].registrering).TimePeriod) = lower((new_itsystem_registrering.registrering).TimePeriod) and lower((read_prev_itsystem.registrering[1].registrering).TimePeriod)=lower((prev_itsystem_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating itsystem with id [%]: The ordering of as_list_itsystem should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', itsystem_uuid, to_json(new_itsystem_registrering), to_json(read_new_itsystem.registrering[1].registrering), to_json(prev_itsystem_registrering), to_json(prev_new_itsystem.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_itsystem_reg := ROW(
        ROW (null, (read_new_itsystem.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_itsystem.registrering[1]).tilsGyldighed ,
        
        (read_new_itsystem.registrering[1]).attrEgenskaber ,
        (read_new_itsystem.registrering[1]).relationer
    )::itsystemRegistreringType;

    read_prev_itsystem_reg := ROW(
        ROW(null, (read_prev_itsystem.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_itsystem.registrering[1]).tilsGyldighed ,
        
        (read_prev_itsystem.registrering[1]).attrEgenskaber ,
        (read_prev_itsystem.registrering[1]).relationer
    )::itsystemRegistreringType;


    IF read_prev_itsystem_reg = read_new_itsystem_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_itsystem_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_itsystem_reg);
      RAISE NOTICE 'Aborted updating itsystem with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', itsystem_uuid, to_json(read_new_itsystem_reg), to_json(read_prev_itsystem_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_itsystem_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of KlasseAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_klasse(
    klasse_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber KlasseEgenskaberAttrType[],
    

    
    tilsPubliceret KlassePubliceretTilsType[],
    

    relationer KlasseRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      KlasseRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_klasse          KlasseType;
    read_prev_klasse         KlasseType;
    read_new_klasse_reg      KlasseRegistreringType;
    read_prev_klasse_reg     KlasseRegistreringType;
    new_klasse_registrering  klasse_registrering;
    prev_klasse_registrering klasse_registrering;
    klasse_relation_navn     KlasseRelationKode;

    
    attrEgenskaberObj KlasseEgenskaberAttrType;
    

    
    new_id_klasse_attr_egenskaber bigint;
    klasseSoegeordObj KlasseSoegeordType;
    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from klasse a join klasse_registrering b ON b.klasse_id=a.id WHERE a.id=klasse_uuid) THEN
        RAISE EXCEPTION 'Unable to update klasse with uuid [%], being unable to find any previous registrations.',klasse_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM klasse a WHERE a.id=klasse_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_klasse(array[klasse_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[klasse_uuid]) THEN
      RAISE EXCEPTION 'Unable to update klasse with uuid [%]. Object does not met stipulated criteria:%', klasse_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_klasse_registrering := _as_create_klasse_registrering(klasse_uuid, livscykluskode, brugerref, note);
    prev_klasse_registrering := _as_get_prev_klasse_registrering(new_klasse_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_klasse_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update klasse with uuid [%], as the klasse seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', klasse_uuid, lostUpdatePreventionTZ, LOWER((prev_klasse_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO klasse_relation (klasse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_klasse_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH klasse_relation_navn IN ARRAY ARRAY['ejer'::KlasseRelationKode ,  'ansvarlig'::KlasseRelationKode ,  'overordnetklasse'::KlasseRelationKode ,  'facet'::KlasseRelationKode  ]::KlasseRelationKode[]  LOOP
        INSERT INTO klasse_relation (klasse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_klasse_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM klasse_relation b
                 WHERE b.klasse_registrering_id = new_klasse_registrering.id AND b.rel_type = klasse_relation_navn) d
            JOIN klasse_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.klasse_registrering_id = prev_klasse_registrering.id AND a.rel_type = klasse_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH klasse_relation_navn IN ARRAY ARRAY['redaktoerer'::KlasseRelationKode, 'sideordnede'::KlasseRelationKode, 'mapninger'::KlasseRelationKode, 'tilfoejelser'::KlasseRelationKode, 'erstatter'::KlasseRelationKode, 'lovligekombinationer'::KlasseRelationKode]::KlasseRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM klasse_relation
                     WHERE klasse_registrering_id = new_klasse_registrering.id AND rel_type = klasse_relation_navn) THEN
                    
                    INSERT INTO klasse_relation (klasse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_klasse_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM klasse_relation
        WHERE
            klasse_registrering_id = prev_klasse_registrering.id AND rel_type = klasse_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsPubliceret IS NOT NULL AND coalesce(array_length(tilsPubliceret, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Publiceret] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- klasse_tils_publiceret

        -- Ad 1)
        INSERT INTO klasse_tils_publiceret(virkning, publiceret, klasse_registrering_id)
             SELECT a.virkning, a.publiceret, new_klasse_registrering.id
               FROM unnest(tilsPubliceret) AS a;

        -- Ad 2
        INSERT INTO klasse_tils_publiceret(virkning, publiceret, klasse_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.publiceret,
            new_klasse_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- klasse_tils_publiceret of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- klasse_tils_publiceret of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM klasse_tils_publiceret b
             WHERE b.klasse_registrering_id = new_klasse_registrering.id) d
              JOIN klasse_tils_publiceret a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.klasse_registrering_id = prev_klasse_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- klasse_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrKlasseObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.beskrivelse,a.eksempel,a.omfang,a.titel,a.retskilde,a.aendringsnotat,
                    a.virkning
                    ,
                        a.soegeord
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update klasse with uuid [%], as the klasse have overlapping virknings in the given egenskaber array :%', klasse_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).beskrivelse IS NULL  OR  (attrEgenskaberObj).eksempel IS NULL  OR  (attrEgenskaberObj).omfang IS NULL  OR  (attrEgenskaberObj).titel IS NULL  OR  (attrEgenskaberObj).retskilde IS NULL  OR  (attrEgenskaberObj).aendringsnotat IS NULL  THEN
             WITH inserted_merged_attr_egenskaber AS (
            INSERT INTO klasse_attr_egenskaber ( id,  brugervendtnoegle,beskrivelse,eksempel,omfang,titel,retskilde,aendringsnotat, virkning, klasse_registrering_id)
                SELECT
                    
                         nextval('klasse_attr_egenskaber_id_seq'), 
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.beskrivelse, a.beskrivelse),
                    
                        
                        
                            coalesce(attrEgenskaberObj.eksempel, a.eksempel),
                    
                        
                        
                            coalesce(attrEgenskaberObj.omfang, a.omfang),
                    
                        
                        
                            coalesce(attrEgenskaberObj.titel, a.titel),
                    
                        
                        
                            coalesce(attrEgenskaberObj.retskilde, a.retskilde),
                    
                        
                        
                            coalesce(attrEgenskaberObj.aendringsnotat, a.aendringsnotat),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_klasse_registrering.id
                        FROM klasse_attr_egenskaber a
                    WHERE
                        a.klasse_registrering_id = prev_klasse_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        
                        RETURNING
                            id new_id,
                            (virkning).TimePeriod merged_timeperiod
                        ) INSERT INTO klasse_attr_egenskaber_soegeord (soegeordidentifikator, beskrivelse, soegeordskategori, klasse_attr_egenskaber_id)
                        SELECT
                            coalesce(b.soegeordidentifikator, c.soegeordidentifikator), --please notice that this is not a merge - one of the joins on b or c will fail.
                            coalesce(b.beskrivelse, c.beskrivelse), --please notice that this is not a merge - one of the joins on b or c will fail.
                            coalesce(b.soegeordskategori, c.soegeordskategori), --please notice that this is not a merge - one of the joins on b or c will fail.
                            a.new_id
                        FROM
                            inserted_merged_attr_egenskaber a
                            LEFT JOIN unnest(attrEgenskaberObj.soegeord) AS b (soegeordidentifikator,
                                beskrivelse,
                                soegeordskategori) ON attrEgenskaberObj.soegeord IS NOT NULL
                            LEFT JOIN klasse_attr_egenskaber AS b2 ON attrEgenskaberObj.soegeord IS NULL AND b2.klasse_registrering_id = prev_klasse_registrering.id AND (b2.virkning).TimePeriod @> a.merged_timeperiod --Please notice, that this will max hit exactly one row - the row that the new id was merged with
                            LEFT JOIN klasse_attr_egenskaber_soegeord AS c ON attrEgenskaberObj.soegeord IS NULL AND c.klasse_attr_egenskaber_id = b2.id
                        WHERE ((attrEgenskaberObj.soegeord IS NULL AND c.id IS NOT NULL) --there is sogeord of merged egenskab
                            OR coalesce(array_length(attrEgenskaberObj.soegeord, 1), 0) > 0 --soegeord is defined in array
                        ) AND (NOT (attrEgenskaberObj.soegeord IS NOT NULL AND array_length(attrEgenskaberObj.soegeord, 1) = 0)) --if the array is empty, no sogeord should be inserted
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
        WITH inserted_attr_egenskaber AS (
        
            INSERT INTO klasse_attr_egenskaber ( id,  brugervendtnoegle,beskrivelse,eksempel,omfang,titel,retskilde,aendringsnotat, virkning, klasse_registrering_id)
                SELECT
                    
                     nextval('klasse_attr_egenskaber_id_seq'), attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.beskrivelse,
                    
                     attrEgenskaberObj.eksempel,
                    
                     attrEgenskaberObj.omfang,
                    
                     attrEgenskaberObj.titel,
                    
                     attrEgenskaberObj.retskilde,
                    
                     attrEgenskaberObj.aendringsnotat,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_klasse_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the klasse_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM klasse_attr_egenskaber b
                    WHERE b.klasse_registrering_id = new_klasse_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE 
                    RETURNING id
        ) INSERT INTO klasse_attr_egenskaber_soegeord(soegeordidentifikator, beskrivelse, soegeordskategori, klasse_attr_egenskaber_id)
        SELECT
            a.soegeordidentifikator,
            a.beskrivelse,
            a.soegeordskategori,
            b.id
        FROM
            unnest(attrEgenskaberObj.soegeord) AS a (soegeordidentifikator,
                beskrivelse,
                soegeordskategori)
            JOIN inserted_attr_egenskaber b ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            
            new_id_klasse_attr_egenskaber := nextval('klasse_attr_egenskaber_id_seq');
            

            INSERT INTO klasse_attr_egenskaber ( id,  brugervendtnoegle,beskrivelse,eksempel,omfang,titel,retskilde,aendringsnotat, virkning, klasse_registrering_id)
                VALUES ( new_id_klasse_attr_egenskaber,   attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.eksempel,  attrEgenskaberObj.omfang,  attrEgenskaberObj.titel,  attrEgenskaberObj.retskilde,  attrEgenskaberObj.aendringsnotat, attrEgenskaberObj.virkning, new_klasse_registrering.id );
        IF attrEgenskaberObj.soegeord IS NOT NULL THEN
            INSERT INTO klasse_attr_egenskaber_soegeord (soegeordidentifikator, beskrivelse, soegeordskategori, klasse_attr_egenskaber_id)
            SELECT
                a.soegeordidentifikator,
                a.beskrivelse,
                a.soegeordskategori,
                new_id_klasse_attr_egenskaber
            FROM
                unnest(attrEgenskaberObj.soegeord) AS a (soegeordidentifikator, beskrivelse, soegeordskategori);
        END IF;

        
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

WITH copied_attr_egenskaber AS (

    INSERT INTO klasse_attr_egenskaber ( id,  brugervendtnoegle,beskrivelse,eksempel,omfang,titel,retskilde,aendringsnotat, virkning, klasse_registrering_id)
    SELECT
         nextval('klasse_attr_egenskaber_id_seq'), 
        
            a.brugervendtnoegle,
        
            a.beskrivelse,
        
            a.eksempel,
        
            a.omfang,
        
            a.titel,
        
            a.retskilde,
        
            a.aendringsnotat,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_klasse_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- klasse_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- klasse_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                klasse_attr_egenskaber b
            WHERE
                b.klasse_registrering_id = new_klasse_registrering.id) d
            JOIN klasse_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.klasse_registrering_id = prev_klasse_registrering.id 
            RETURNING id new_id, (virkning).TimePeriod
    ) INSERT INTO klasse_attr_egenskaber_soegeord (soegeordidentifikator, beskrivelse, soegeordskategori, klasse_attr_egenskaber_id)
    SELECT
        b.soegeordidentifikator, b.beskrivelse, b.soegeordskategori, a.new_id
    FROM
        copied_attr_egenskaber a
        JOIN klasse_attr_egenskaber a2 ON a2.klasse_registrering_id = prev_klasse_registrering.id AND (a2.virkning).TimePeriod @> a.TimePeriod
        -- This will hit exactly one row - that is, the row that we copied.
        JOIN klasse_attr_egenskaber_soegeord b ON a2.id = b.klasse_attr_egenskaber_id
        ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_klasse := as_read_klasse(klasse_uuid, (new_klasse_registrering.registrering).timeperiod, null);
    read_prev_klasse := as_read_klasse(klasse_uuid, (prev_klasse_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_klasse.registrering[1].registrering).TimePeriod) = lower((new_klasse_registrering.registrering).TimePeriod) and lower((read_prev_klasse.registrering[1].registrering).TimePeriod)=lower((prev_klasse_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating klasse with id [%]: The ordering of as_list_klasse should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', klasse_uuid, to_json(new_klasse_registrering), to_json(read_new_klasse.registrering[1].registrering), to_json(prev_klasse_registrering), to_json(prev_new_klasse.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_klasse_reg := ROW(
        ROW (null, (read_new_klasse.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_klasse.registrering[1]).tilsPubliceret ,
        
        (read_new_klasse.registrering[1]).attrEgenskaber ,
        (read_new_klasse.registrering[1]).relationer
    )::klasseRegistreringType;

    read_prev_klasse_reg := ROW(
        ROW(null, (read_prev_klasse.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_klasse.registrering[1]).tilsPubliceret ,
        
        (read_prev_klasse.registrering[1]).attrEgenskaber ,
        (read_prev_klasse.registrering[1]).relationer
    )::klasseRegistreringType;


    IF read_prev_klasse_reg = read_new_klasse_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_klasse_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_klasse_reg);
      RAISE NOTICE 'Aborted updating klasse with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', klasse_uuid, to_json(read_new_klasse_reg), to_json(read_prev_klasse_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_klasse_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of KlassifikationAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_klassifikation(
    klassifikation_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber KlassifikationEgenskaberAttrType[],
    

    
    tilsPubliceret KlassifikationPubliceretTilsType[],
    

    relationer KlassifikationRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      KlassifikationRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_klassifikation          KlassifikationType;
    read_prev_klassifikation         KlassifikationType;
    read_new_klassifikation_reg      KlassifikationRegistreringType;
    read_prev_klassifikation_reg     KlassifikationRegistreringType;
    new_klassifikation_registrering  klassifikation_registrering;
    prev_klassifikation_registrering klassifikation_registrering;
    klassifikation_relation_navn     KlassifikationRelationKode;

    
    attrEgenskaberObj KlassifikationEgenskaberAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from klassifikation a join klassifikation_registrering b ON b.klassifikation_id=a.id WHERE a.id=klassifikation_uuid) THEN
        RAISE EXCEPTION 'Unable to update klassifikation with uuid [%], being unable to find any previous registrations.',klassifikation_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM klassifikation a WHERE a.id=klassifikation_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_klassifikation(array[klassifikation_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[klassifikation_uuid]) THEN
      RAISE EXCEPTION 'Unable to update klassifikation with uuid [%]. Object does not met stipulated criteria:%', klassifikation_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_klassifikation_registrering := _as_create_klassifikation_registrering(klassifikation_uuid, livscykluskode, brugerref, note);
    prev_klassifikation_registrering := _as_get_prev_klassifikation_registrering(new_klassifikation_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_klassifikation_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update klassifikation with uuid [%], as the klassifikation seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', klassifikation_uuid, lostUpdatePreventionTZ, LOWER((prev_klassifikation_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO klassifikation_relation (klassifikation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_klassifikation_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH klassifikation_relation_navn IN ARRAY ARRAY['ansvarlig'::KlassifikationRelationKode ,  'ejer'::KlassifikationRelationKode  ]::KlassifikationRelationKode[]  LOOP
        INSERT INTO klassifikation_relation (klassifikation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_klassifikation_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM klassifikation_relation b
                 WHERE b.klassifikation_registrering_id = new_klassifikation_registrering.id AND b.rel_type = klassifikation_relation_navn) d
            JOIN klassifikation_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.klassifikation_registrering_id = prev_klassifikation_registrering.id AND a.rel_type = klassifikation_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH klassifikation_relation_navn IN ARRAY ARRAY[]::KlassifikationRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM klassifikation_relation
                     WHERE klassifikation_registrering_id = new_klassifikation_registrering.id AND rel_type = klassifikation_relation_navn) THEN
                    
                    INSERT INTO klassifikation_relation (klassifikation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_klassifikation_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM klassifikation_relation
        WHERE
            klassifikation_registrering_id = prev_klassifikation_registrering.id AND rel_type = klassifikation_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsPubliceret IS NOT NULL AND coalesce(array_length(tilsPubliceret, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Publiceret] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- klassifikation_tils_publiceret

        -- Ad 1)
        INSERT INTO klassifikation_tils_publiceret(virkning, publiceret, klassifikation_registrering_id)
             SELECT a.virkning, a.publiceret, new_klassifikation_registrering.id
               FROM unnest(tilsPubliceret) AS a;

        -- Ad 2
        INSERT INTO klassifikation_tils_publiceret(virkning, publiceret, klassifikation_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.publiceret,
            new_klassifikation_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- klassifikation_tils_publiceret of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- klassifikation_tils_publiceret of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM klassifikation_tils_publiceret b
             WHERE b.klassifikation_registrering_id = new_klassifikation_registrering.id) d
              JOIN klassifikation_tils_publiceret a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.klassifikation_registrering_id = prev_klassifikation_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- klassifikation_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrKlassifikationObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.beskrivelse,a.kaldenavn,a.ophavsret,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update klassifikation with uuid [%], as the klassifikation have overlapping virknings in the given egenskaber array :%', klassifikation_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).beskrivelse IS NULL  OR  (attrEgenskaberObj).kaldenavn IS NULL  OR  (attrEgenskaberObj).ophavsret IS NULL  THEN
            
            INSERT INTO klassifikation_attr_egenskaber ( brugervendtnoegle,beskrivelse,kaldenavn,ophavsret, virkning, klassifikation_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.beskrivelse, a.beskrivelse),
                    
                        
                        
                            coalesce(attrEgenskaberObj.kaldenavn, a.kaldenavn),
                    
                        
                        
                            coalesce(attrEgenskaberObj.ophavsret, a.ophavsret),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_klassifikation_registrering.id
                        FROM klassifikation_attr_egenskaber a
                    WHERE
                        a.klassifikation_registrering_id = prev_klassifikation_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO klassifikation_attr_egenskaber ( brugervendtnoegle,beskrivelse,kaldenavn,ophavsret, virkning, klassifikation_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.beskrivelse,
                    
                     attrEgenskaberObj.kaldenavn,
                    
                     attrEgenskaberObj.ophavsret,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_klassifikation_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the klassifikation_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM klassifikation_attr_egenskaber b
                    WHERE b.klassifikation_registrering_id = new_klassifikation_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO klassifikation_attr_egenskaber ( brugervendtnoegle,beskrivelse,kaldenavn,ophavsret, virkning, klassifikation_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.kaldenavn,  attrEgenskaberObj.ophavsret, attrEgenskaberObj.virkning, new_klassifikation_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO klassifikation_attr_egenskaber ( brugervendtnoegle,beskrivelse,kaldenavn,ophavsret, virkning, klassifikation_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.beskrivelse,
        
            a.kaldenavn,
        
            a.ophavsret,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_klassifikation_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- klassifikation_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- klassifikation_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                klassifikation_attr_egenskaber b
            WHERE
                b.klassifikation_registrering_id = new_klassifikation_registrering.id) d
            JOIN klassifikation_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.klassifikation_registrering_id = prev_klassifikation_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_klassifikation := as_read_klassifikation(klassifikation_uuid, (new_klassifikation_registrering.registrering).timeperiod, null);
    read_prev_klassifikation := as_read_klassifikation(klassifikation_uuid, (prev_klassifikation_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_klassifikation.registrering[1].registrering).TimePeriod) = lower((new_klassifikation_registrering.registrering).TimePeriod) and lower((read_prev_klassifikation.registrering[1].registrering).TimePeriod)=lower((prev_klassifikation_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating klassifikation with id [%]: The ordering of as_list_klassifikation should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', klassifikation_uuid, to_json(new_klassifikation_registrering), to_json(read_new_klassifikation.registrering[1].registrering), to_json(prev_klassifikation_registrering), to_json(prev_new_klassifikation.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_klassifikation_reg := ROW(
        ROW (null, (read_new_klassifikation.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_klassifikation.registrering[1]).tilsPubliceret ,
        
        (read_new_klassifikation.registrering[1]).attrEgenskaber ,
        (read_new_klassifikation.registrering[1]).relationer
    )::klassifikationRegistreringType;

    read_prev_klassifikation_reg := ROW(
        ROW(null, (read_prev_klassifikation.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_klassifikation.registrering[1]).tilsPubliceret ,
        
        (read_prev_klassifikation.registrering[1]).attrEgenskaber ,
        (read_prev_klassifikation.registrering[1]).relationer
    )::klassifikationRegistreringType;


    IF read_prev_klassifikation_reg = read_new_klassifikation_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_klassifikation_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_klassifikation_reg);
      RAISE NOTICE 'Aborted updating klassifikation with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', klassifikation_uuid, to_json(read_new_klassifikation_reg), to_json(read_prev_klassifikation_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_klassifikation_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of OrganisationAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_organisation(
    organisation_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber OrganisationEgenskaberAttrType[],
    

    
    tilsGyldighed OrganisationGyldighedTilsType[],
    

    relationer OrganisationRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      OrganisationRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_organisation          OrganisationType;
    read_prev_organisation         OrganisationType;
    read_new_organisation_reg      OrganisationRegistreringType;
    read_prev_organisation_reg     OrganisationRegistreringType;
    new_organisation_registrering  organisation_registrering;
    prev_organisation_registrering organisation_registrering;
    organisation_relation_navn     OrganisationRelationKode;

    
    attrEgenskaberObj OrganisationEgenskaberAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from organisation a join organisation_registrering b ON b.organisation_id=a.id WHERE a.id=organisation_uuid) THEN
        RAISE EXCEPTION 'Unable to update organisation with uuid [%], being unable to find any previous registrations.',organisation_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM organisation a WHERE a.id=organisation_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_organisation(array[organisation_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[organisation_uuid]) THEN
      RAISE EXCEPTION 'Unable to update organisation with uuid [%]. Object does not met stipulated criteria:%', organisation_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_organisation_registrering := _as_create_organisation_registrering(organisation_uuid, livscykluskode, brugerref, note);
    prev_organisation_registrering := _as_get_prev_organisation_registrering(new_organisation_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_organisation_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update organisation with uuid [%], as the organisation seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', organisation_uuid, lostUpdatePreventionTZ, LOWER((prev_organisation_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO organisation_relation (organisation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_organisation_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH organisation_relation_navn IN ARRAY ARRAY['branche'::OrganisationRelationKode ,  'myndighed'::OrganisationRelationKode ,  'myndighedstype'::OrganisationRelationKode ,  'overordnet'::OrganisationRelationKode ,  'produktionsenhed'::OrganisationRelationKode ,  'skatteenhed'::OrganisationRelationKode ,  'tilhoerer'::OrganisationRelationKode ,  'virksomhed'::OrganisationRelationKode ,  'virksomhedstype'::OrganisationRelationKode  ]::OrganisationRelationKode[]  LOOP
        INSERT INTO organisation_relation (organisation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_organisation_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM organisation_relation b
                 WHERE b.organisation_registrering_id = new_organisation_registrering.id AND b.rel_type = organisation_relation_navn) d
            JOIN organisation_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisation_registrering_id = prev_organisation_registrering.id AND a.rel_type = organisation_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH organisation_relation_navn IN ARRAY ARRAY['adresser'::OrganisationRelationKode, 'ansatte'::OrganisationRelationKode, 'opgaver'::OrganisationRelationKode, 'tilknyttedebrugere'::OrganisationRelationKode, 'tilknyttedeenheder'::OrganisationRelationKode, 'tilknyttedefunktioner'::OrganisationRelationKode, 'tilknyttedeinteressefaellesskaber'::OrganisationRelationKode, 'tilknyttedeorganisationer'::OrganisationRelationKode, 'tilknyttedepersoner'::OrganisationRelationKode, 'tilknyttedeitsystemer'::OrganisationRelationKode]::OrganisationRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM organisation_relation
                     WHERE organisation_registrering_id = new_organisation_registrering.id AND rel_type = organisation_relation_navn) THEN
                    
                    INSERT INTO organisation_relation (organisation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_organisation_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM organisation_relation
        WHERE
            organisation_registrering_id = prev_organisation_registrering.id AND rel_type = organisation_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsGyldighed IS NOT NULL AND coalesce(array_length(tilsGyldighed, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Gyldighed] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- organisation_tils_gyldighed

        -- Ad 1)
        INSERT INTO organisation_tils_gyldighed(virkning, gyldighed, organisation_registrering_id)
             SELECT a.virkning, a.gyldighed, new_organisation_registrering.id
               FROM unnest(tilsGyldighed) AS a;

        -- Ad 2
        INSERT INTO organisation_tils_gyldighed(virkning, gyldighed, organisation_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.gyldighed,
            new_organisation_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisation_tils_gyldighed of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisation_tils_gyldighed of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM organisation_tils_gyldighed b
             WHERE b.organisation_registrering_id = new_organisation_registrering.id) d
              JOIN organisation_tils_gyldighed a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.organisation_registrering_id = prev_organisation_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- organisation_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrOrganisationObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.organisationsnavn,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update organisation with uuid [%], as the organisation have overlapping virknings in the given egenskaber array :%', organisation_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).organisationsnavn IS NULL  THEN
            
            INSERT INTO organisation_attr_egenskaber ( brugervendtnoegle,organisationsnavn, virkning, organisation_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.organisationsnavn, a.organisationsnavn),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_organisation_registrering.id
                        FROM organisation_attr_egenskaber a
                    WHERE
                        a.organisation_registrering_id = prev_organisation_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO organisation_attr_egenskaber ( brugervendtnoegle,organisationsnavn, virkning, organisation_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.organisationsnavn,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_organisation_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the organisation_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM organisation_attr_egenskaber b
                    WHERE b.organisation_registrering_id = new_organisation_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO organisation_attr_egenskaber ( brugervendtnoegle,organisationsnavn, virkning, organisation_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.organisationsnavn, attrEgenskaberObj.virkning, new_organisation_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO organisation_attr_egenskaber ( brugervendtnoegle,organisationsnavn, virkning, organisation_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.organisationsnavn,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_organisation_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisation_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisation_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                organisation_attr_egenskaber b
            WHERE
                b.organisation_registrering_id = new_organisation_registrering.id) d
            JOIN organisation_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisation_registrering_id = prev_organisation_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_organisation := as_read_organisation(organisation_uuid, (new_organisation_registrering.registrering).timeperiod, null);
    read_prev_organisation := as_read_organisation(organisation_uuid, (prev_organisation_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_organisation.registrering[1].registrering).TimePeriod) = lower((new_organisation_registrering.registrering).TimePeriod) and lower((read_prev_organisation.registrering[1].registrering).TimePeriod)=lower((prev_organisation_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating organisation with id [%]: The ordering of as_list_organisation should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', organisation_uuid, to_json(new_organisation_registrering), to_json(read_new_organisation.registrering[1].registrering), to_json(prev_organisation_registrering), to_json(prev_new_organisation.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_organisation_reg := ROW(
        ROW (null, (read_new_organisation.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_organisation.registrering[1]).tilsGyldighed ,
        
        (read_new_organisation.registrering[1]).attrEgenskaber ,
        (read_new_organisation.registrering[1]).relationer
    )::organisationRegistreringType;

    read_prev_organisation_reg := ROW(
        ROW(null, (read_prev_organisation.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_organisation.registrering[1]).tilsGyldighed ,
        
        (read_prev_organisation.registrering[1]).attrEgenskaber ,
        (read_prev_organisation.registrering[1]).relationer
    )::organisationRegistreringType;


    IF read_prev_organisation_reg = read_new_organisation_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_organisation_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_organisation_reg);
      RAISE NOTICE 'Aborted updating organisation with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisation_uuid, to_json(read_new_organisation_reg), to_json(read_prev_organisation_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisation_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of OrganisationenhedAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_organisationenhed(
    organisationenhed_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber OrganisationenhedEgenskaberAttrType[],
    

    
    tilsGyldighed OrganisationenhedGyldighedTilsType[],
    

    relationer OrganisationenhedRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      OrganisationenhedRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_organisationenhed          OrganisationenhedType;
    read_prev_organisationenhed         OrganisationenhedType;
    read_new_organisationenhed_reg      OrganisationenhedRegistreringType;
    read_prev_organisationenhed_reg     OrganisationenhedRegistreringType;
    new_organisationenhed_registrering  organisationenhed_registrering;
    prev_organisationenhed_registrering organisationenhed_registrering;
    organisationenhed_relation_navn     OrganisationenhedRelationKode;

    
    attrEgenskaberObj OrganisationenhedEgenskaberAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from organisationenhed a join organisationenhed_registrering b ON b.organisationenhed_id=a.id WHERE a.id=organisationenhed_uuid) THEN
        RAISE EXCEPTION 'Unable to update organisationenhed with uuid [%], being unable to find any previous registrations.',organisationenhed_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM organisationenhed a WHERE a.id=organisationenhed_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_organisationenhed(array[organisationenhed_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[organisationenhed_uuid]) THEN
      RAISE EXCEPTION 'Unable to update organisationenhed with uuid [%]. Object does not met stipulated criteria:%', organisationenhed_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_organisationenhed_registrering := _as_create_organisationenhed_registrering(organisationenhed_uuid, livscykluskode, brugerref, note);
    prev_organisationenhed_registrering := _as_get_prev_organisationenhed_registrering(new_organisationenhed_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_organisationenhed_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update organisationenhed with uuid [%], as the organisationenhed seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', organisationenhed_uuid, lostUpdatePreventionTZ, LOWER((prev_organisationenhed_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO organisationenhed_relation (organisationenhed_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_organisationenhed_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH organisationenhed_relation_navn IN ARRAY ARRAY['branche'::OrganisationenhedRelationKode ,  'enhedstype'::OrganisationenhedRelationKode ,  'overordnet'::OrganisationenhedRelationKode ,  'produktionsenhed'::OrganisationenhedRelationKode ,  'skatteenhed'::OrganisationenhedRelationKode ,  'tilhoerer'::OrganisationenhedRelationKode ,  'niveau'::OrganisationenhedRelationKode  ]::OrganisationenhedRelationKode[]  LOOP
        INSERT INTO organisationenhed_relation (organisationenhed_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_organisationenhed_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM organisationenhed_relation b
                 WHERE b.organisationenhed_registrering_id = new_organisationenhed_registrering.id AND b.rel_type = organisationenhed_relation_navn) d
            JOIN organisationenhed_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisationenhed_registrering_id = prev_organisationenhed_registrering.id AND a.rel_type = organisationenhed_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH organisationenhed_relation_navn IN ARRAY ARRAY['adresser'::OrganisationenhedRelationKode, 'ansatte'::OrganisationenhedRelationKode, 'opgaver'::OrganisationenhedRelationKode, 'tilknyttedebrugere'::OrganisationenhedRelationKode, 'tilknyttedeenheder'::OrganisationenhedRelationKode, 'tilknyttedefunktioner'::OrganisationenhedRelationKode, 'tilknyttedeinteressefaellesskaber'::OrganisationenhedRelationKode, 'tilknyttedeorganisationer'::OrganisationenhedRelationKode, 'tilknyttedepersoner'::OrganisationenhedRelationKode, 'tilknyttedeitsystemer'::OrganisationenhedRelationKode, 'opmærkning'::OrganisationenhedRelationKode]::OrganisationenhedRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM organisationenhed_relation
                     WHERE organisationenhed_registrering_id = new_organisationenhed_registrering.id AND rel_type = organisationenhed_relation_navn) THEN
                    
                    INSERT INTO organisationenhed_relation (organisationenhed_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_organisationenhed_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM organisationenhed_relation
        WHERE
            organisationenhed_registrering_id = prev_organisationenhed_registrering.id AND rel_type = organisationenhed_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsGyldighed IS NOT NULL AND coalesce(array_length(tilsGyldighed, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Gyldighed] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- organisationenhed_tils_gyldighed

        -- Ad 1)
        INSERT INTO organisationenhed_tils_gyldighed(virkning, gyldighed, organisationenhed_registrering_id)
             SELECT a.virkning, a.gyldighed, new_organisationenhed_registrering.id
               FROM unnest(tilsGyldighed) AS a;

        -- Ad 2
        INSERT INTO organisationenhed_tils_gyldighed(virkning, gyldighed, organisationenhed_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.gyldighed,
            new_organisationenhed_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisationenhed_tils_gyldighed of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisationenhed_tils_gyldighed of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM organisationenhed_tils_gyldighed b
             WHERE b.organisationenhed_registrering_id = new_organisationenhed_registrering.id) d
              JOIN organisationenhed_tils_gyldighed a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.organisationenhed_registrering_id = prev_organisationenhed_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- organisationenhed_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrOrganisationenhedObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.enhedsnavn,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update organisationenhed with uuid [%], as the organisationenhed have overlapping virknings in the given egenskaber array :%', organisationenhed_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).enhedsnavn IS NULL  THEN
            
            INSERT INTO organisationenhed_attr_egenskaber ( brugervendtnoegle,enhedsnavn, virkning, organisationenhed_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.enhedsnavn, a.enhedsnavn),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_organisationenhed_registrering.id
                        FROM organisationenhed_attr_egenskaber a
                    WHERE
                        a.organisationenhed_registrering_id = prev_organisationenhed_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO organisationenhed_attr_egenskaber ( brugervendtnoegle,enhedsnavn, virkning, organisationenhed_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.enhedsnavn,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_organisationenhed_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the organisationenhed_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM organisationenhed_attr_egenskaber b
                    WHERE b.organisationenhed_registrering_id = new_organisationenhed_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO organisationenhed_attr_egenskaber ( brugervendtnoegle,enhedsnavn, virkning, organisationenhed_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.enhedsnavn, attrEgenskaberObj.virkning, new_organisationenhed_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO organisationenhed_attr_egenskaber ( brugervendtnoegle,enhedsnavn, virkning, organisationenhed_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.enhedsnavn,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_organisationenhed_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisationenhed_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisationenhed_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                organisationenhed_attr_egenskaber b
            WHERE
                b.organisationenhed_registrering_id = new_organisationenhed_registrering.id) d
            JOIN organisationenhed_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisationenhed_registrering_id = prev_organisationenhed_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_organisationenhed := as_read_organisationenhed(organisationenhed_uuid, (new_organisationenhed_registrering.registrering).timeperiod, null);
    read_prev_organisationenhed := as_read_organisationenhed(organisationenhed_uuid, (prev_organisationenhed_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_organisationenhed.registrering[1].registrering).TimePeriod) = lower((new_organisationenhed_registrering.registrering).TimePeriod) and lower((read_prev_organisationenhed.registrering[1].registrering).TimePeriod)=lower((prev_organisationenhed_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating organisationenhed with id [%]: The ordering of as_list_organisationenhed should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', organisationenhed_uuid, to_json(new_organisationenhed_registrering), to_json(read_new_organisationenhed.registrering[1].registrering), to_json(prev_organisationenhed_registrering), to_json(prev_new_organisationenhed.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_organisationenhed_reg := ROW(
        ROW (null, (read_new_organisationenhed.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_organisationenhed.registrering[1]).tilsGyldighed ,
        
        (read_new_organisationenhed.registrering[1]).attrEgenskaber ,
        (read_new_organisationenhed.registrering[1]).relationer
    )::organisationenhedRegistreringType;

    read_prev_organisationenhed_reg := ROW(
        ROW(null, (read_prev_organisationenhed.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_organisationenhed.registrering[1]).tilsGyldighed ,
        
        (read_prev_organisationenhed.registrering[1]).attrEgenskaber ,
        (read_prev_organisationenhed.registrering[1]).relationer
    )::organisationenhedRegistreringType;


    IF read_prev_organisationenhed_reg = read_new_organisationenhed_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_organisationenhed_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_organisationenhed_reg);
      RAISE NOTICE 'Aborted updating organisationenhed with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisationenhed_uuid, to_json(read_new_organisationenhed_reg), to_json(read_prev_organisationenhed_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisationenhed_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;




-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

/*
NOTICE: This file is auto-generated!
*/


-- Also notice, that the given arrays of OrganisationfunktionAttr...Type
-- must be consistent regarding virkning (although the allowance of
-- null-values might make it possible to construct
-- 'logically consistent'-arrays of objects with overlapping virknings)
CREATE OR REPLACE FUNCTION as_update_organisationfunktion(
    organisationfunktion_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode Livscykluskode,

    
    attrEgenskaber OrganisationfunktionEgenskaberAttrType[],
    
    attrUdvidelser OrganisationfunktionUdvidelserAttrType[],
    

    
    tilsGyldighed OrganisationfunktionGyldighedTilsType[],
    

    relationer OrganisationfunktionRelationType[],

    

    lostUpdatePreventionTZ TIMESTAMPTZ = null,
    auth_criteria_arr      OrganisationfunktionRegistreringType[] = null
) RETURNS bigint AS $$
DECLARE
    read_new_organisationfunktion          OrganisationfunktionType;
    read_prev_organisationfunktion         OrganisationfunktionType;
    read_new_organisationfunktion_reg      OrganisationfunktionRegistreringType;
    read_prev_organisationfunktion_reg     OrganisationfunktionRegistreringType;
    new_organisationfunktion_registrering  organisationfunktion_registrering;
    prev_organisationfunktion_registrering organisationfunktion_registrering;
    organisationfunktion_relation_navn     OrganisationfunktionRelationKode;

    
    attrEgenskaberObj OrganisationfunktionEgenskaberAttrType;
    
    attrUdvidelserObj OrganisationfunktionUdvidelserAttrType;
    

    

    auth_filtered_uuids uuid[];

    
BEGIN
    -- Create a new registrering
    IF NOT EXISTS (select a.id from organisationfunktion a join organisationfunktion_registrering b ON b.organisationfunktion_id=a.id WHERE a.id=organisationfunktion_uuid) THEN
        RAISE EXCEPTION 'Unable to update organisationfunktion with uuid [%], being unable to find any previous registrations.',organisationfunktion_uuid USING ERRCODE = 'MO400';
    END IF;

    -- We synchronize concurrent invocations of as_updates of this particular
    -- object on a exclusive row lock. This lock will be held by the current
    -- transaction until it terminates.
    PERFORM a.id FROM organisationfunktion a WHERE a.id=organisationfunktion_uuid FOR UPDATE;

    -- Verify that the object meets the stipulated access allowed criteria
    auth_filtered_uuids := _as_filter_unauth_organisationfunktion(array[organisationfunktion_uuid]::uuid[], auth_criteria_arr);
    IF NOT (coalesce(array_length(auth_filtered_uuids, 1), 0) = 1 AND auth_filtered_uuids @>ARRAY[organisationfunktion_uuid]) THEN
      RAISE EXCEPTION 'Unable to update organisationfunktion with uuid [%]. Object does not met stipulated criteria:%', organisationfunktion_uuid, to_json(auth_criteria_arr) USING ERRCODE = 'MO401';
    END IF;

    new_organisationfunktion_registrering := _as_create_organisationfunktion_registrering(organisationfunktion_uuid, livscykluskode, brugerref, note);
    prev_organisationfunktion_registrering := _as_get_prev_organisationfunktion_registrering(new_organisationfunktion_registrering);

    IF lostUpdatePreventionTZ IS NOT NULL THEN
      IF NOT (LOWER((prev_organisationfunktion_registrering.registrering).timeperiod) = lostUpdatePreventionTZ) THEN
        RAISE EXCEPTION 'Unable to update organisationfunktion with uuid [%], as the organisationfunktion seems to have been updated since latest read by client (the given lostUpdatePreventionTZ [%] does not match the timesamp of latest registration [%]).', organisationfunktion_uuid, lostUpdatePreventionTZ, LOWER((prev_organisationfunktion_registrering.registrering).timeperiod) USING ERRCODE = 'MO409';
      END IF;
    END IF;

    -- Handle relationer (relations)
    IF relationer IS NOT NULL AND coalesce(array_length(relationer, 1), 0) = 0 THEN
        -- raise notice 'Skipping relations, as it is explicit set to empty array. Update note [%]', note;
    ELSE

    -- 1) Insert relations given as part of this update
    -- 2) for aktivitet: Insert relations of previous registration, with index
    --      values not included in this update. Please notice that for the
    --      logic to work, it is very important that the index sequences
    --      start with the max value for index of the same type in the
    --      previous registration
    -- 2) for everything else: Insert relations of previous registration,
    --      taking overlapping virknings into consideration
    --      (using function subtract_tstzrange)

    --Ad 1)
    

    INSERT INTO organisationfunktion_relation (organisationfunktion_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
    SELECT
        new_organisationfunktion_registrering.id,
        a.virkning,
        a.uuid,
        a.urn,
        a.relType,
        a.objektType 
        FROM
            unnest(relationer) AS a ;

    


    -- Ad 2)
    -- 0..1 relations

    
    
    FOREACH organisationfunktion_relation_navn IN ARRAY ARRAY['organisatoriskfunktionstype'::OrganisationfunktionRelationKode ,  'primær'::OrganisationfunktionRelationKode  ]::OrganisationfunktionRelationKode[]  LOOP
        INSERT INTO organisationfunktion_relation (organisationfunktion_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
        SELECT
            new_organisationfunktion_registrering.id,
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.rel_maal_uuid,
            a.rel_maal_urn,
            a.rel_type,
            a.objekt_type 
            FROM (
                -- Build an array of the timeperiod of the virkning of the
                -- relations of the new registrering to pass to
                -- _subtract_tstzrange_arr on the relations of the previous
                -- registrering.
                SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                  FROM organisationfunktion_relation b
                 WHERE b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id AND b.rel_type = organisationfunktion_relation_navn) d
            JOIN organisationfunktion_relation a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id AND a.rel_type = organisationfunktion_relation_navn;
    END LOOP;

    -- 0..n relations
    -- We only have to check if there are any of the relations with the
    -- given name present in the new registration, otherwise copy the ones
    -- from the previous registration.

    
    FOREACH organisationfunktion_relation_navn IN ARRAY ARRAY['adresser'::OrganisationfunktionRelationKode, 'opgaver'::OrganisationfunktionRelationKode, 'tilknyttedebrugere'::OrganisationfunktionRelationKode, 'tilknyttedeenheder'::OrganisationfunktionRelationKode, 'tilknyttedeorganisationer'::OrganisationfunktionRelationKode, 'tilknyttedeitsystemer'::OrganisationfunktionRelationKode, 'tilknyttedeinteressefaellesskaber'::OrganisationfunktionRelationKode, 'tilknyttedepersoner'::OrganisationfunktionRelationKode, 'tilknyttedefunktioner'::OrganisationfunktionRelationKode, 'tilknyttedeklasser'::OrganisationfunktionRelationKode]::OrganisationfunktionRelationKode[] LOOP
        IF NOT EXISTS (
                    SELECT 1
                      FROM organisationfunktion_relation
                     WHERE organisationfunktion_registrering_id = new_organisationfunktion_registrering.id AND rel_type = organisationfunktion_relation_navn) THEN
                    
                    INSERT INTO organisationfunktion_relation (organisationfunktion_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type )
                    SELECT
                        new_organisationfunktion_registrering.id,  virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type
        FROM organisationfunktion_relation
        WHERE
            organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id AND rel_type = organisationfunktion_relation_navn ;

    
        END IF;
    END LOOP;
    
    END IF;


    -- Handle tilstande (states)
    
    IF tilsGyldighed IS NOT NULL AND coalesce(array_length(tilsGyldighed, 1), 0) = 0 THEN
        -- raise debug 'Skipping [Gyldighed] as it is explicit set to empty array';
    ELSE
        -- 1) Insert tilstande/states given as part of this update
        -- 2) Insert tilstande/states of previous registration, taking
        --      overlapping virknings into consideration (using function
        --      subtract_tstzrange)

        -- organisationfunktion_tils_gyldighed

        -- Ad 1)
        INSERT INTO organisationfunktion_tils_gyldighed(virkning, gyldighed, organisationfunktion_registrering_id)
             SELECT a.virkning, a.gyldighed, new_organisationfunktion_registrering.id
               FROM unnest(tilsGyldighed) AS a;

        -- Ad 2
        INSERT INTO organisationfunktion_tils_gyldighed(virkning, gyldighed, organisationfunktion_registrering_id)
        SELECT
            ROW (c.tz_range_leftover,
                (a.virkning).AktoerRef,
                (a.virkning).AktoerTypeKode,
                (a.virkning).NoteTekst)::virkning,
            a.gyldighed,
            new_organisationfunktion_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisationfunktion_tils_gyldighed of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisationfunktion_tils_gyldighed of the previous registrering
            SELECT coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
              FROM organisationfunktion_tils_gyldighed b
             WHERE b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id) d
              JOIN organisationfunktion_tils_gyldighed a ON TRUE
              JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id;
    END IF;
    


    -- Handle attributter (attributes)
    
    -- organisationfunktion_attr_egenskaber

    -- Generate and insert any merged objects, if any fields are null
    -- in attrOrganisationfunktionObj
    IF attrEgenskaber IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrEgenskaber) a
                    JOIN unnest(attrEgenskaber) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.brugervendtnoegle,a.funktionsnavn,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update organisationfunktion with uuid [%], as the organisationfunktion have overlapping virknings in the given egenskaber array :%', organisationfunktion_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).funktionsnavn IS NULL  THEN
            
            INSERT INTO organisationfunktion_attr_egenskaber ( brugervendtnoegle,funktionsnavn, virkning, organisationfunktion_registrering_id)
                SELECT
                    
                        
                        
                            coalesce(attrEgenskaberObj.brugervendtnoegle, a.brugervendtnoegle),
                    
                        
                        
                            coalesce(attrEgenskaberObj.funktionsnavn, a.funktionsnavn),
                    
                    ROW ((a.virkning).TimePeriod * (attrEgenskaberObj.virkning).TimePeriod,
                            (attrEgenskaberObj.virkning).AktoerRef,
                            (attrEgenskaberObj.virkning).AktoerTypeKode,
                            (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                            new_organisationfunktion_registrering.id
                        FROM organisationfunktion_attr_egenskaber a
                    WHERE
                        a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id
                        AND (a.virkning).TimePeriod && (attrEgenskaberObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrEgenskaberObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO organisationfunktion_attr_egenskaber ( brugervendtnoegle,funktionsnavn, virkning, organisationfunktion_registrering_id)
                SELECT
                    
                     attrEgenskaberObj.brugervendtnoegle,
                    
                     attrEgenskaberObj.funktionsnavn,
                    
                    ROW (b.tz_range_leftover,
                        (attrEgenskaberObj.virkning).AktoerRef,
                        (attrEgenskaberObj.virkning).AktoerTypeKode,
                        (attrEgenskaberObj.virkning).NoteTekst)::Virkning,
                        new_organisationfunktion_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the organisationfunktion_attr_egenskaber of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM organisationfunktion_attr_egenskaber b
                    WHERE b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrEgenskaberObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrEgenskaberObj raw (if there were no null-valued fields)
            

            INSERT INTO organisationfunktion_attr_egenskaber ( brugervendtnoegle,funktionsnavn, virkning, organisationfunktion_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.funktionsnavn, attrEgenskaberObj.virkning, new_organisationfunktion_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO organisationfunktion_attr_egenskaber ( brugervendtnoegle,funktionsnavn, virkning, organisationfunktion_registrering_id)
    SELECT
        
        
            a.brugervendtnoegle,
        
            a.funktionsnavn,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_organisationfunktion_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisationfunktion_attr_egenskaber of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisationfunktion_attr_egenskaber of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                organisationfunktion_attr_egenskaber b
            WHERE
                b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id) d
            JOIN organisationfunktion_attr_egenskaber a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id ;

END IF;

    -- organisationfunktion_attr_udvidelser

    -- Generate and insert any merged objects, if any fields are null
    -- in attrOrganisationfunktionObj
    IF attrUdvidelser IS NOT NULL THEN
        --Input validation:
        --Verify that there is no overlap in virkning in the array given
        IF EXISTS (
                SELECT a.* FROM
                    unnest(attrUdvidelser) a
                    JOIN unnest(attrUdvidelser) b ON (a.virkning).TimePeriod && (b.virkning).TimePeriod
                GROUP BY
                    a.primær,a.fraktion,a.udvidelse_1,a.udvidelse_2,a.udvidelse_3,a.udvidelse_4,a.udvidelse_5,a.udvidelse_6,a.udvidelse_7,a.udvidelse_8,a.udvidelse_9,a.udvidelse_10,
                    a.virkning
                    
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update organisationfunktion with uuid [%], as the organisationfunktion have overlapping virknings in the given udvidelser array :%', organisationfunktion_uuid, to_json(attrUdvidelser) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrUdvidelserObj IN ARRAY attrUdvidelser LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrUdvidelserObj).primær IS NULL  OR  (attrUdvidelserObj).fraktion IS NULL  OR  (attrUdvidelserObj).udvidelse_1 IS NULL  OR  (attrUdvidelserObj).udvidelse_2 IS NULL  OR  (attrUdvidelserObj).udvidelse_3 IS NULL  OR  (attrUdvidelserObj).udvidelse_4 IS NULL  OR  (attrUdvidelserObj).udvidelse_5 IS NULL  OR  (attrUdvidelserObj).udvidelse_6 IS NULL  OR  (attrUdvidelserObj).udvidelse_7 IS NULL  OR  (attrUdvidelserObj).udvidelse_8 IS NULL  OR  (attrUdvidelserObj).udvidelse_9 IS NULL  OR  (attrUdvidelserObj).udvidelse_10 IS NULL  THEN
            
            INSERT INTO organisationfunktion_attr_udvidelser ( primær,fraktion,udvidelse_1,udvidelse_2,udvidelse_3,udvidelse_4,udvidelse_5,udvidelse_6,udvidelse_7,udvidelse_8,udvidelse_9,udvidelse_10, virkning, organisationfunktion_registrering_id)
                SELECT
                    
                        
                        
                            CASE WHEN ((attrUdvidelserObj.primær).cleared) THEN
                                NULL
                            ELSE
                                coalesce((attrUdvidelserObj.primær).value, a.primær)
                            END,
                        
                    
                        
                        
                            CASE WHEN ((attrUdvidelserObj.fraktion).cleared) THEN
                                NULL
                            ELSE
                                coalesce((attrUdvidelserObj.fraktion).value, a.fraktion)
                            END,
                        
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_1, a.udvidelse_1),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_2, a.udvidelse_2),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_3, a.udvidelse_3),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_4, a.udvidelse_4),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_5, a.udvidelse_5),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_6, a.udvidelse_6),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_7, a.udvidelse_7),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_8, a.udvidelse_8),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_9, a.udvidelse_9),
                    
                        
                        
                            coalesce(attrUdvidelserObj.udvidelse_10, a.udvidelse_10),
                    
                    ROW ((a.virkning).TimePeriod * (attrUdvidelserObj.virkning).TimePeriod,
                            (attrUdvidelserObj.virkning).AktoerRef,
                            (attrUdvidelserObj.virkning).AktoerTypeKode,
                            (attrUdvidelserObj.virkning).NoteTekst)::Virkning,
                            new_organisationfunktion_registrering.id
                        FROM organisationfunktion_attr_udvidelser a
                    WHERE
                        a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id
                        AND (a.virkning).TimePeriod && (attrUdvidelserObj.virkning).TimePeriod
                        ;

        -- For any periods within the virkning of the attrUdvidelserObj,
        -- that is NOT covered by any "merged" rows inserted above, generate
        -- and insert rows.
        
            INSERT INTO organisationfunktion_attr_udvidelser ( primær,fraktion,udvidelse_1,udvidelse_2,udvidelse_3,udvidelse_4,udvidelse_5,udvidelse_6,udvidelse_7,udvidelse_8,udvidelse_9,udvidelse_10, virkning, organisationfunktion_registrering_id)
                SELECT
                    
                     attrUdvidelserObj.primær,
                    
                     attrUdvidelserObj.fraktion,
                    
                     attrUdvidelserObj.udvidelse_1,
                    
                     attrUdvidelserObj.udvidelse_2,
                    
                     attrUdvidelserObj.udvidelse_3,
                    
                     attrUdvidelserObj.udvidelse_4,
                    
                     attrUdvidelserObj.udvidelse_5,
                    
                     attrUdvidelserObj.udvidelse_6,
                    
                     attrUdvidelserObj.udvidelse_7,
                    
                     attrUdvidelserObj.udvidelse_8,
                    
                     attrUdvidelserObj.udvidelse_9,
                    
                     attrUdvidelserObj.udvidelse_10,
                    
                    ROW (b.tz_range_leftover,
                        (attrUdvidelserObj.virkning).AktoerRef,
                        (attrUdvidelserObj.virkning).AktoerTypeKode,
                        (attrUdvidelserObj.virkning).NoteTekst)::Virkning,
                        new_organisationfunktion_registrering.id
                    FROM (
                        -- Build an array of the timeperiod of the virkning
                        -- of the organisationfunktion_attr_udvidelser of the new
                        -- registrering to pass to _subtract_tstzrange_arr.
                        SELECT
                            coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
                        FROM organisationfunktion_attr_udvidelser b
                    WHERE b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id) AS a
                    JOIN unnest(_subtract_tstzrange_arr ((attrUdvidelserObj.virkning).TimePeriod, a.tzranges_of_new_reg)) AS b (tz_range_leftover) ON TRUE ;

        ELSE
            -- Insert attrUdvidelserObj raw (if there were no null-valued fields)
            

            INSERT INTO organisationfunktion_attr_udvidelser ( primær,fraktion,udvidelse_1,udvidelse_2,udvidelse_3,udvidelse_4,udvidelse_5,udvidelse_6,udvidelse_7,udvidelse_8,udvidelse_9,udvidelse_10, virkning, organisationfunktion_registrering_id)
                VALUES (  attrUdvidelserObj.primær,  attrUdvidelserObj.fraktion,  attrUdvidelserObj.udvidelse_1,  attrUdvidelserObj.udvidelse_2,  attrUdvidelserObj.udvidelse_3,  attrUdvidelserObj.udvidelse_4,  attrUdvidelserObj.udvidelse_5,  attrUdvidelserObj.udvidelse_6,  attrUdvidelserObj.udvidelse_7,  attrUdvidelserObj.udvidelse_8,  attrUdvidelserObj.udvidelse_9,  attrUdvidelserObj.udvidelse_10, attrUdvidelserObj.virkning, new_organisationfunktion_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrUdvidelser IS NOT NULL AND coalesce(array_length(attrUdvidelser, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of udvidelser of previous registration as an empty array was explicit given.';
        ELSE



-- Handle udvidelser of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO organisationfunktion_attr_udvidelser ( primær,fraktion,udvidelse_1,udvidelse_2,udvidelse_3,udvidelse_4,udvidelse_5,udvidelse_6,udvidelse_7,udvidelse_8,udvidelse_9,udvidelse_10, virkning, organisationfunktion_registrering_id)
    SELECT
        
        
            a.primær,
        
            a.fraktion,
        
            a.udvidelse_1,
        
            a.udvidelse_2,
        
            a.udvidelse_3,
        
            a.udvidelse_4,
        
            a.udvidelse_5,
        
            a.udvidelse_6,
        
            a.udvidelse_7,
        
            a.udvidelse_8,
        
            a.udvidelse_9,
        
            a.udvidelse_10,
        
        ROW (c.tz_range_leftover,
            (a.virkning).AktoerRef,
            (a.virkning).AktoerTypeKode,
            (a.virkning).NoteTekst)::virkning,
            new_organisationfunktion_registrering.id
        FROM (
            -- Build an array of the timeperiod of the virkning of the
            -- organisationfunktion_attr_udvidelser of the new registrering to
            -- pass to _subtract_tstzrange_arr on the
            -- organisationfunktion_attr_udvidelser of the previous registrering.
            SELECT
                coalesce(array_agg((b.virkning).TimePeriod), ARRAY[]::TSTZRANGE[]) tzranges_of_new_reg
            FROM
                organisationfunktion_attr_udvidelser b
            WHERE
                b.organisationfunktion_registrering_id = new_organisationfunktion_registrering.id) d
            JOIN organisationfunktion_attr_udvidelser a ON TRUE
            JOIN unnest(_subtract_tstzrange_arr ((a.virkning).TimePeriod, tzranges_of_new_reg)) AS c (tz_range_leftover) ON TRUE
        WHERE
            a.organisationfunktion_registrering_id = prev_organisationfunktion_registrering.id ;

END IF;






    /******************************************************************/
    -- If the new registrering is identical to the previous one, we need
    -- to throw an exception to abort the transaction.

    read_new_organisationfunktion := as_read_organisationfunktion(organisationfunktion_uuid, (new_organisationfunktion_registrering.registrering).timeperiod, null);
    read_prev_organisationfunktion := as_read_organisationfunktion(organisationfunktion_uuid, (prev_organisationfunktion_registrering.registrering).timeperiod, null);

    -- The ordering in as_list (called by as_read) ensures that the latest
    -- registration is returned at index pos 1.

    IF NOT (lower((read_new_organisationfunktion.registrering[1].registrering).TimePeriod) = lower((new_organisationfunktion_registrering.registrering).TimePeriod) and lower((read_prev_organisationfunktion.registrering[1].registrering).TimePeriod)=lower((prev_organisationfunktion_registrering.registrering).TimePeriod)) THEN
      RAISE EXCEPTION 'Error updating organisationfunktion with id [%]: The ordering of as_list_organisationfunktion should ensure that the latest registrering can be found at index 1. Expected new reg: [%]. Actual new reg at index 1: [%]. Expected prev reg: [%]. Actual prev reg at index 1: [%].', organisationfunktion_uuid, to_json(new_organisationfunktion_registrering), to_json(read_new_organisationfunktion.registrering[1].registrering), to_json(prev_organisationfunktion_registrering), to_json(prev_new_organisationfunktion.registrering[1].registrering) USING ERRCODE = 'MO500';
    END IF;

    -- We'll ignore the registreringBase part in the comparrison - except
    -- for the livcykluskode
    read_new_organisationfunktion_reg := ROW(
        ROW (null, (read_new_organisationfunktion.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_new_organisationfunktion.registrering[1]).tilsGyldighed ,
        
        (read_new_organisationfunktion.registrering[1]).attrEgenskaber ,
        (read_new_organisationfunktion.registrering[1]).attrUdvidelser ,
        (read_new_organisationfunktion.registrering[1]).relationer
    )::organisationfunktionRegistreringType;

    read_prev_organisationfunktion_reg := ROW(
        ROW(null, (read_prev_organisationfunktion.registrering[1].registrering).livscykluskode, null, null)::registreringBase,
        
        (read_prev_organisationfunktion.registrering[1]).tilsGyldighed ,
        
        (read_prev_organisationfunktion.registrering[1]).attrEgenskaber ,
        (read_prev_organisationfunktion.registrering[1]).attrUdvidelser ,
        (read_prev_organisationfunktion.registrering[1]).relationer
    )::organisationfunktionRegistreringType;


    IF read_prev_organisationfunktion_reg = read_new_organisationfunktion_reg THEN
      --RAISE NOTICE 'Note[%]. Aborted reg:%',note,to_json(read_new_organisationfunktion_reg);
      --RAISE NOTICE 'Note[%]. Previous reg:%',note,to_json(read_prev_organisationfunktion_reg);
      RAISE NOTICE 'Aborted updating organisationfunktion with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisationfunktion_uuid, to_json(read_new_organisationfunktion_reg), to_json(read_prev_organisationfunktion_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisationfunktion_registrering.id;
END; $$ LANGUAGE plpgsql VOLATILE;
