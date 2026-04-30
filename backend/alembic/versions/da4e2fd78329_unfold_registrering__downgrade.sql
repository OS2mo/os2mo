-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

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
            'DROP TRIGGER IF EXISTS %I ON actual_state.%I',
            tbl || '_unfolded_sync',
            tbl
        );
        EXECUTE format(
            'DROP TABLE IF EXISTS actual_state.%I',
            tbl || '_unfolded'
        );
    END LOOP;
END;
$$;

DROP FUNCTION IF EXISTS actual_state._registrering_unfolded_sync ();
