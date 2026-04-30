-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- Unpack the RegistreringBase composite type into a parallel table
-- per `*_registrering` table, kept in sync by a trigger. Adding the
-- unpacked columns to the existing tables would change their row
-- type and break stored functions that build rows positionally
-- (e.g. _as_create_*_registrering does
-- `ROW(id, oio_id, registrering)::*_registrering`); a side table
-- avoids that and lets queries and templates remain untouched.

CREATE OR REPLACE FUNCTION actual_state._registrering_unfolded_sync ()
    RETURNS TRIGGER AS $$
BEGIN
    EXECUTE format(
        'INSERT INTO actual_state.%I (id, timeperiod, livscykluskode, brugerref, note)
         VALUES ($1, ($2).timeperiod, ($2).livscykluskode, ($2).brugerref, ($2).note)
         ON CONFLICT (id) DO UPDATE SET
             timeperiod = EXCLUDED.timeperiod,
             livscykluskode = EXCLUDED.livscykluskode,
             brugerref = EXCLUDED.brugerref,
             note = EXCLUDED.note',
        TG_TABLE_NAME || '_unfolded'
    ) USING NEW.id, NEW.registrering;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'bruger_registrering',
        'facet_registrering',
        'itsystem_registrering',
        'klasse_registrering',
        'klassifikation_registrering',
        'organisation_registrering',
        'organisationenhed_registrering',
        'organisationfunktion_registrering'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format(
            'CREATE TABLE actual_state.%I (
                id bigint PRIMARY KEY
                    REFERENCES actual_state.%I (id) ON DELETE CASCADE,
                timeperiod tstzrange NOT NULL,
                livscykluskode actual_state.livscykluskode NOT NULL,
                brugerref uuid,
                note text
            )',
            tbl || '_unfolded',
            tbl
        );
        EXECUTE format(
            'INSERT INTO actual_state.%I (id, timeperiod, livscykluskode, brugerref, note)
             SELECT id,
                    (registrering).timeperiod,
                    (registrering).livscykluskode,
                    (registrering).brugerref,
                    (registrering).note
               FROM actual_state.%I',
            tbl || '_unfolded',
            tbl
        );
        EXECUTE format(
            'CREATE TRIGGER %I
                AFTER INSERT OR UPDATE OF registrering ON actual_state.%I
                FOR EACH ROW EXECUTE FUNCTION actual_state._registrering_unfolded_sync()',
            tbl || '_unfolded_sync',
            tbl
        );
    END LOOP;
END;
$$;
