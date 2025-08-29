CREATE OR REPLACE FUNCTION consolidate_organisationenhed_relation()
RETURNS TRIGGER AS $$
DECLARE
    virkning_group RECORD;
BEGIN
    -- Find groups of virkning that are duplicated in everything but their
    -- timeperiod.
    FOR virkning_group IN
        SELECT
            t.organisationenhed_registrering_id,
            t.rel_maal_uuid,
            t.rel_maal_urn,
            t.rel_type,
            t.objekt_type,
            -- Aggregate virkning ids and timeperiods for the group
            range_agg((t.virkning).timeperiod) AS timeperiods,
            array_agg(t.id) AS ids
        FROM
            organisationenhed_relation t
        INNER JOIN
            -- Only process changed rows (passed by the trigger)
            changed_rows ON t.organisationenhed_registrering_id = changed_rows.organisationenhed_registrering_id
        GROUP BY
            t.organisationenhed_registrering_id,
            t.rel_maal_uuid,
            t.rel_maal_urn,
            t.rel_type,
            t.objekt_type
        HAVING
            -- Only process groups with more than one virkning
            COUNT(*) > 1
    LOOP
        -- Delete original (potentially) unconsolidated virkninger in group
        DELETE FROM organisationenhed_relation
        WHERE id = ANY(virkning_group.ids);
        -- Insert new consolidated records. This must be done in a separate
        -- step, after the deletion, to avoid the _no_virkning_overlap
        -- constraint.
        INSERT INTO organisationenhed_relation (
            organisationenhed_registrering_id,
            virkning,
            rel_maal_uuid,
            rel_maal_urn,
            rel_type,
            objekt_type
        )
        SELECT
            virkning_group.organisationenhed_registrering_id,
            -- The consolidated virkning's aktoerref, aktoertypekode, and
            -- notetekst is set to NULL.
            ROW(consolidated_timeperiod, NULL, NULL, NULL)::virkning,
            virkning_group.rel_maal_uuid,
            virkning_group.rel_maal_urn,
            virkning_group.rel_type,
            virkning_group.objekt_type
        FROM
            -- Consolidate overlapping or adjacent timeperiods into a set of
            -- distinct and non-overlapping timeperiods.
            unnest(virkning_group.timeperiods) AS consolidated_timeperiod;
    END LOOP;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER merge_organisationenhed_relation_insert_trigger
AFTER INSERT ON organisationenhed_relation REFERENCING NEW TABLE AS changed_rows
FOR EACH STATEMENT
EXECUTE FUNCTION consolidate_organisationenhed_relation ();

CREATE OR REPLACE TRIGGER merge_organisationenhed_relation_update_trigger
AFTER UPDATE ON organisationenhed_relation REFERENCING NEW TABLE AS changed_rows
FOR EACH STATEMENT
EXECUTE FUNCTION consolidate_organisationenhed_relation ();


UPDATE organisationenhed_relation SET id = id WHERE organisationenhed_registrering_id IN ( SELECT id FROM organisationenhed_registrering WHERE organisationenhed_id = 'f06ee470-9f17-566f-acbe-e938112d46d9');

SELECT * FROM organisationenhed_relation WHERE organisationenhed_registrering_id IN ( SELECT id FROM organisationenhed_registrering WHERE organisationenhed_id = 'f06ee470-9f17-566f-acbe-e938112d46d9') ORDER BY organisationenhed_registrering_id DESC, rel_type, (virkning).timeperiod;

-- Run function on all existing rows
-- UPDATE organisationenhed_relation SET id = id;
-- TODO: select before/after, diff
