-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

-- Restores the object db functions as they were before this migration,
-- extracted verbatim from a database migrated to the previous head
-- (d903192968e9) using pg_get_functiondef.

-- Drop the overloads introduced by the upgrade before restoring the old
-- signatures, so the schema round-trips exactly.

DROP FUNCTION IF EXISTS actual_state.as_create_or_import_bruger(
    brugerregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_facet(
    facetregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_itsystem(
    itsystemregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_klasse(
    klasseregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_klassifikation(
    klassifikationregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_organisationenhed(
    organisationenhedregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_organisationfunktion(
    organisationfunktionregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_create_or_import_organisation(
    organisationregistreringtype, uuid
);
DROP FUNCTION IF EXISTS actual_state.as_list_bruger(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_facet(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_itsystem(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_klasse(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_klassifikation(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_organisationenhed(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_organisationfunktion(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_list_organisation(
    uuid[], tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_read_bruger(uuid, tstzrange, tstzrange);
DROP FUNCTION IF EXISTS actual_state.as_read_facet(uuid, tstzrange, tstzrange);
DROP FUNCTION IF EXISTS actual_state.as_read_itsystem(
    uuid, tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_read_klasse(uuid, tstzrange, tstzrange);
DROP FUNCTION IF EXISTS actual_state.as_read_klassifikation(
    uuid, tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_read_organisationenhed(
    uuid, tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_read_organisationfunktion(
    uuid, tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_read_organisation(
    uuid, tstzrange, tstzrange
);
DROP FUNCTION IF EXISTS actual_state.as_search_bruger(
    integer,
    uuid,
    brugerregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_facet(
    integer,
    uuid,
    facetregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_itsystem(
    integer,
    uuid,
    itsystemregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_klasse(
    integer,
    uuid,
    klasseregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_klassifikation(
    integer,
    uuid,
    klassifikationregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_organisationenhed(
    integer,
    uuid,
    organisationenhedregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_organisationfunktion(
    integer,
    uuid,
    organisationfunktionregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_search_organisation(
    integer,
    uuid,
    organisationregistreringtype,
    tstzrange,
    integer,
    text[],
    uuid[],
    text[]
);
DROP FUNCTION IF EXISTS actual_state.as_update_bruger(
    uuid,
    uuid,
    text,
    livscykluskode,
    brugeregenskaberattrtype[],
    brugerudvidelserattrtype[],
    brugergyldighedtilstype[],
    brugerrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_facet(
    uuid,
    uuid,
    text,
    livscykluskode,
    facetegenskaberattrtype[],
    facetpublicerettilstype[],
    facetrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_itsystem(
    uuid,
    uuid,
    text,
    livscykluskode,
    itsystemegenskaberattrtype[],
    itsystemgyldighedtilstype[],
    itsystemrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_klasse(
    uuid,
    uuid,
    text,
    livscykluskode,
    klasseegenskaberattrtype[],
    klassepublicerettilstype[],
    klasserelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_klassifikation(
    uuid,
    uuid,
    text,
    livscykluskode,
    klassifikationegenskaberattrtype[],
    klassifikationpublicerettilstype[],
    klassifikationrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_organisationenhed(
    uuid,
    uuid,
    text,
    livscykluskode,
    organisationenhedegenskaberattrtype[],
    organisationenhedgyldighedtilstype[],
    organisationenhedrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_organisationfunktion(
    uuid,
    uuid,
    text,
    livscykluskode,
    organisationfunktionegenskaberattrtype[],
    organisationfunktionudvidelserattrtype[],
    organisationfunktiongyldighedtilstype[],
    organisationfunktionrelationtype[],
    timestamp with time zone
);
DROP FUNCTION IF EXISTS actual_state.as_update_organisation(
    uuid,
    uuid,
    text,
    livscykluskode,
    organisationegenskaberattrtype[],
    organisationgyldighedtilstype[],
    organisationrelationtype[],
    timestamp with time zone
);

-- as_create_or_import_bruger(brugerregistreringtype,uuid,brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_bruger(
    bruger_registrering brugerregistreringtype,
    bruger_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::brugerregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE bruger_registrering_id bigint;
    bruger_attr_egenskaber_obj brugerEgenskaberAttrType;
    bruger_attr_udvidelser_obj brugerUdvidelserAttrType;



    bruger_tils_gyldighed_obj brugerGyldighedTilsType;


    bruger_relationer BrugerRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_bruger_registrering bruger_registrering;
BEGIN
    IF bruger_uuid IS NULL THEN LOOP
        bruger_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from bruger WHERE id=bruger_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from bruger WHERE id=bruger_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (bruger_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (bruger_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (bruger_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_bruger.',(bruger_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO bruger (ID) SELECT
        bruger_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        bruger_registrering_id:=nextval('bruger_registrering_id_seq');

        INSERT INTO bruger_registrering (id, bruger_id,
            registrering) SELECT bruger_registrering_id,
        bruger_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (bruger_registrering.registrering).livscykluskode,
        (bruger_registrering.registrering).brugerref,
        (bruger_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_bruger_registrering :=
            _as_create_bruger_registrering(bruger_uuid,
                (bruger_registrering.registrering).livscykluskode,
                (bruger_registrering.registrering).brugerref,
                (bruger_registrering.registrering).note);

            bruger_registrering_id := new_bruger_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(bruger_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [bruger]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF bruger_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(bruger_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH bruger_attr_egenskaber_obj IN ARRAY bruger_registrering.attrEgenskaber
  LOOP


    INSERT INTO bruger_attr_egenskaber (

      brugervendtnoegle,
      brugernavn,
      brugertype,
      virkning,
      bruger_registrering_id
    )
    SELECT

     bruger_attr_egenskaber_obj.brugervendtnoegle,
      bruger_attr_egenskaber_obj.brugernavn,
      bruger_attr_egenskaber_obj.brugertype,
      bruger_attr_egenskaber_obj.virkning,
      bruger_registrering_id
    ;


  END LOOP;
END IF;


IF bruger_registrering.attrUdvidelser IS NOT NULL and coalesce(array_length(bruger_registrering.attrUdvidelser,1),0)>0 THEN
  FOREACH bruger_attr_udvidelser_obj IN ARRAY bruger_registrering.attrUdvidelser
  LOOP


    INSERT INTO bruger_attr_udvidelser (

      fornavn,
      efternavn,
      kaldenavn_fornavn,
      kaldenavn_efternavn,
      seniority,
      virkning,
      bruger_registrering_id
    )
    SELECT

     bruger_attr_udvidelser_obj.fornavn,
      bruger_attr_udvidelser_obj.efternavn,
      bruger_attr_udvidelser_obj.kaldenavn_fornavn,
      bruger_attr_udvidelser_obj.kaldenavn_efternavn,
      bruger_attr_udvidelser_obj.seniority,
      bruger_attr_udvidelser_obj.virkning,
      bruger_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(bruger_registrering.tilsGyldighed, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [gyldighed] for bruger. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF bruger_registrering.tilsGyldighed IS NOT NULL AND coalesce(array_length(bruger_registrering.tilsGyldighed,1),0)>0 THEN
  FOREACH bruger_tils_gyldighed_obj IN ARRAY bruger_registrering.tilsGyldighed
  LOOP

    INSERT INTO bruger_tils_gyldighed (
      virkning,
      gyldighed,
      bruger_registrering_id
    )
    SELECT
      bruger_tils_gyldighed_obj.virkning,
      bruger_tils_gyldighed_obj.gyldighed,
      bruger_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO bruger_relation (
      bruger_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      bruger_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(bruger_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_bruger(array[bruger_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[bruger_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import bruger with uuid [%]. Object does not met stipulated criteria:%',bruger_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN bruger_uuid;

END;
$function$

;

-- as_create_or_import_facet(facetregistreringtype,uuid,facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_facet(
    facet_registrering facetregistreringtype,
    facet_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr facetregistreringtype[] DEFAULT NULL::facetregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE facet_registrering_id bigint;


    facet_attr_egenskaber_obj facetEgenskaberAttrType;



    facet_tils_publiceret_obj facetPubliceretTilsType;


    facet_relationer FacetRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_facet_registrering facet_registrering;
BEGIN
    IF facet_uuid IS NULL THEN LOOP
        facet_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from facet WHERE id=facet_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from facet WHERE id=facet_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (facet_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (facet_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (facet_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_facet.',(facet_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO facet (ID) SELECT
        facet_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        facet_registrering_id:=nextval('facet_registrering_id_seq');

        INSERT INTO facet_registrering (id, facet_id,
            registrering) SELECT facet_registrering_id,
        facet_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (facet_registrering.registrering).livscykluskode,
        (facet_registrering.registrering).brugerref,
        (facet_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_facet_registrering :=
            _as_create_facet_registrering(facet_uuid,
                (facet_registrering.registrering).livscykluskode,
                (facet_registrering.registrering).brugerref,
                (facet_registrering.registrering).note);

            facet_registrering_id := new_facet_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(facet_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [facet]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF facet_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(facet_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH facet_attr_egenskaber_obj IN ARRAY facet_registrering.attrEgenskaber
  LOOP


    INSERT INTO facet_attr_egenskaber (

      brugervendtnoegle,
      beskrivelse,
      opbygning,
      ophavsret,
      plan,
      supplement,
      retskilde,
      virkning,
      facet_registrering_id
    )
    SELECT

     facet_attr_egenskaber_obj.brugervendtnoegle,
      facet_attr_egenskaber_obj.beskrivelse,
      facet_attr_egenskaber_obj.opbygning,
      facet_attr_egenskaber_obj.ophavsret,
      facet_attr_egenskaber_obj.plan,
      facet_attr_egenskaber_obj.supplement,
      facet_attr_egenskaber_obj.retskilde,
      facet_attr_egenskaber_obj.virkning,
      facet_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(facet_registrering.tilsPubliceret, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [publiceret] for facet. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF facet_registrering.tilsPubliceret IS NOT NULL AND coalesce(array_length(facet_registrering.tilsPubliceret,1),0)>0 THEN
  FOREACH facet_tils_publiceret_obj IN ARRAY facet_registrering.tilsPubliceret
  LOOP

    INSERT INTO facet_tils_publiceret (
      virkning,
      publiceret,
      facet_registrering_id
    )
    SELECT
      facet_tils_publiceret_obj.virkning,
      facet_tils_publiceret_obj.publiceret,
      facet_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO facet_relation (
      facet_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      facet_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(facet_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_facet(array[facet_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[facet_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import facet with uuid [%]. Object does not met stipulated criteria:%',facet_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN facet_uuid;

END;
$function$

;

-- as_create_or_import_itsystem(itsystemregistreringtype,uuid,itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_itsystem(
    itsystem_registrering itsystemregistreringtype,
    itsystem_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::itsystemregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE itsystem_registrering_id bigint;


    itsystem_attr_egenskaber_obj itsystemEgenskaberAttrType;



    itsystem_tils_gyldighed_obj itsystemGyldighedTilsType;


    itsystem_relationer ItsystemRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_itsystem_registrering itsystem_registrering;
BEGIN
    IF itsystem_uuid IS NULL THEN LOOP
        itsystem_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from itsystem WHERE id=itsystem_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from itsystem WHERE id=itsystem_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (itsystem_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (itsystem_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (itsystem_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_itsystem.',(itsystem_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO itsystem (ID) SELECT
        itsystem_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        itsystem_registrering_id:=nextval('itsystem_registrering_id_seq');

        INSERT INTO itsystem_registrering (id, itsystem_id,
            registrering) SELECT itsystem_registrering_id,
        itsystem_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (itsystem_registrering.registrering).livscykluskode,
        (itsystem_registrering.registrering).brugerref,
        (itsystem_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_itsystem_registrering :=
            _as_create_itsystem_registrering(itsystem_uuid,
                (itsystem_registrering.registrering).livscykluskode,
                (itsystem_registrering.registrering).brugerref,
                (itsystem_registrering.registrering).note);

            itsystem_registrering_id := new_itsystem_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(itsystem_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [itsystem]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF itsystem_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(itsystem_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH itsystem_attr_egenskaber_obj IN ARRAY itsystem_registrering.attrEgenskaber
  LOOP


    INSERT INTO itsystem_attr_egenskaber (

      brugervendtnoegle,
      itsystemnavn,
      itsystemtype,
      konfigurationreference,
      virkning,
      itsystem_registrering_id
    )
    SELECT

     itsystem_attr_egenskaber_obj.brugervendtnoegle,
      itsystem_attr_egenskaber_obj.itsystemnavn,
      itsystem_attr_egenskaber_obj.itsystemtype,
      itsystem_attr_egenskaber_obj.konfigurationreference,
      itsystem_attr_egenskaber_obj.virkning,
      itsystem_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(itsystem_registrering.tilsGyldighed, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [gyldighed] for itsystem. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF itsystem_registrering.tilsGyldighed IS NOT NULL AND coalesce(array_length(itsystem_registrering.tilsGyldighed,1),0)>0 THEN
  FOREACH itsystem_tils_gyldighed_obj IN ARRAY itsystem_registrering.tilsGyldighed
  LOOP

    INSERT INTO itsystem_tils_gyldighed (
      virkning,
      gyldighed,
      itsystem_registrering_id
    )
    SELECT
      itsystem_tils_gyldighed_obj.virkning,
      itsystem_tils_gyldighed_obj.gyldighed,
      itsystem_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO itsystem_relation (
      itsystem_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      itsystem_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(itsystem_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_itsystem(array[itsystem_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[itsystem_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import itsystem with uuid [%]. Object does not met stipulated criteria:%',itsystem_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN itsystem_uuid;

END;
$function$

;

-- as_create_or_import_klasse(klasseregistreringtype,uuid,klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_klasse(
    klasse_registrering klasseregistreringtype,
    klasse_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::klasseregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE klasse_registrering_id bigint;


    klasse_attr_egenskaber_obj klasseEgenskaberAttrType;



    klasse_tils_publiceret_obj klassePubliceretTilsType;


    klasse_relationer KlasseRelationType;


    klasse_attr_egenskaber_id bigint;
    klasse_attr_egenskaber_soegeord_obj KlasseSoegeordType;


    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_klasse_registrering klasse_registrering;
BEGIN
    IF klasse_uuid IS NULL THEN LOOP
        klasse_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from klasse WHERE id=klasse_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from klasse WHERE id=klasse_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (klasse_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (klasse_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (klasse_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_klasse.',(klasse_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO klasse (ID) SELECT
        klasse_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        klasse_registrering_id:=nextval('klasse_registrering_id_seq');

        INSERT INTO klasse_registrering (id, klasse_id,
            registrering) SELECT klasse_registrering_id,
        klasse_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (klasse_registrering.registrering).livscykluskode,
        (klasse_registrering.registrering).brugerref,
        (klasse_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_klasse_registrering :=
            _as_create_klasse_registrering(klasse_uuid,
                (klasse_registrering.registrering).livscykluskode,
                (klasse_registrering.registrering).brugerref,
                (klasse_registrering.registrering).note);

            klasse_registrering_id := new_klasse_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(klasse_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [klasse]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF klasse_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(klasse_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH klasse_attr_egenskaber_obj IN ARRAY klasse_registrering.attrEgenskaber
  LOOP


  klasse_attr_egenskaber_id:=nextval('klasse_attr_egenskaber_id_seq');

    INSERT INTO klasse_attr_egenskaber (
      id,
      brugervendtnoegle,
      beskrivelse,
      eksempel,
      omfang,
      titel,
      retskilde,
      aendringsnotat,
      virkning,
      klasse_registrering_id
    )
    SELECT
     klasse_attr_egenskaber_id,
     klasse_attr_egenskaber_obj.brugervendtnoegle,
      klasse_attr_egenskaber_obj.beskrivelse,
      klasse_attr_egenskaber_obj.eksempel,
      klasse_attr_egenskaber_obj.omfang,
      klasse_attr_egenskaber_obj.titel,
      klasse_attr_egenskaber_obj.retskilde,
      klasse_attr_egenskaber_obj.aendringsnotat,
      klasse_attr_egenskaber_obj.virkning,
      klasse_registrering_id
    ;


 /************/
 --Insert Soegeord
  IF klasse_attr_egenskaber_obj.soegeord IS NOT NULL AND coalesce(array_length(klasse_attr_egenskaber_obj.soegeord,1),0)>1 THEN
    FOREACH klasse_attr_egenskaber_soegeord_obj IN ARRAY klasse_attr_egenskaber_obj.soegeord
      LOOP

      IF (klasse_attr_egenskaber_soegeord_obj.soegeordidentifikator IS NOT NULL AND klasse_attr_egenskaber_soegeord_obj.soegeordidentifikator<>'')
      OR (klasse_attr_egenskaber_soegeord_obj.beskrivelse IS NOT NULL AND klasse_attr_egenskaber_soegeord_obj.beskrivelse<>'' )
      OR (klasse_attr_egenskaber_soegeord_obj.soegeordskategori IS NOT NULL AND klasse_attr_egenskaber_soegeord_obj.soegeordskategori<>'') THEN

      INSERT INTO klasse_attr_egenskaber_soegeord (
        soegeordidentifikator,
        beskrivelse,
        soegeordskategori,
        klasse_attr_egenskaber_id
      )
      SELECT
        klasse_attr_egenskaber_soegeord_obj.soegeordidentifikator,
        klasse_attr_egenskaber_soegeord_obj.beskrivelse,
        klasse_attr_egenskaber_soegeord_obj.soegeordskategori,
        klasse_attr_egenskaber_id
      ;
      END IF;

     END LOOP;
    END IF;

  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(klasse_registrering.tilsPubliceret, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [publiceret] for klasse. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF klasse_registrering.tilsPubliceret IS NOT NULL AND coalesce(array_length(klasse_registrering.tilsPubliceret,1),0)>0 THEN
  FOREACH klasse_tils_publiceret_obj IN ARRAY klasse_registrering.tilsPubliceret
  LOOP

    INSERT INTO klasse_tils_publiceret (
      virkning,
      publiceret,
      klasse_registrering_id
    )
    SELECT
      klasse_tils_publiceret_obj.virkning,
      klasse_tils_publiceret_obj.publiceret,
      klasse_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO klasse_relation (
      klasse_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      klasse_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(klasse_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_klasse(array[klasse_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[klasse_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import klasse with uuid [%]. Object does not met stipulated criteria:%',klasse_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN klasse_uuid;

END;
$function$

;

-- as_create_or_import_klassifikation(klassifikationregistreringtype,uuid,klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_klassifikation(
    klassifikation_registrering klassifikationregistreringtype,
    klassifikation_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::klassifikationregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE klassifikation_registrering_id bigint;


    klassifikation_attr_egenskaber_obj klassifikationEgenskaberAttrType;



    klassifikation_tils_publiceret_obj klassifikationPubliceretTilsType;


    klassifikation_relationer KlassifikationRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_klassifikation_registrering klassifikation_registrering;
BEGIN
    IF klassifikation_uuid IS NULL THEN LOOP
        klassifikation_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from klassifikation WHERE id=klassifikation_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from klassifikation WHERE id=klassifikation_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (klassifikation_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (klassifikation_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (klassifikation_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_klassifikation.',(klassifikation_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO klassifikation (ID) SELECT
        klassifikation_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        klassifikation_registrering_id:=nextval('klassifikation_registrering_id_seq');

        INSERT INTO klassifikation_registrering (id, klassifikation_id,
            registrering) SELECT klassifikation_registrering_id,
        klassifikation_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (klassifikation_registrering.registrering).livscykluskode,
        (klassifikation_registrering.registrering).brugerref,
        (klassifikation_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_klassifikation_registrering :=
            _as_create_klassifikation_registrering(klassifikation_uuid,
                (klassifikation_registrering.registrering).livscykluskode,
                (klassifikation_registrering.registrering).brugerref,
                (klassifikation_registrering.registrering).note);

            klassifikation_registrering_id := new_klassifikation_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(klassifikation_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [klassifikation]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF klassifikation_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(klassifikation_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH klassifikation_attr_egenskaber_obj IN ARRAY klassifikation_registrering.attrEgenskaber
  LOOP


    INSERT INTO klassifikation_attr_egenskaber (

      brugervendtnoegle,
      beskrivelse,
      kaldenavn,
      ophavsret,
      virkning,
      klassifikation_registrering_id
    )
    SELECT

     klassifikation_attr_egenskaber_obj.brugervendtnoegle,
      klassifikation_attr_egenskaber_obj.beskrivelse,
      klassifikation_attr_egenskaber_obj.kaldenavn,
      klassifikation_attr_egenskaber_obj.ophavsret,
      klassifikation_attr_egenskaber_obj.virkning,
      klassifikation_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(klassifikation_registrering.tilsPubliceret, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [publiceret] for klassifikation. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF klassifikation_registrering.tilsPubliceret IS NOT NULL AND coalesce(array_length(klassifikation_registrering.tilsPubliceret,1),0)>0 THEN
  FOREACH klassifikation_tils_publiceret_obj IN ARRAY klassifikation_registrering.tilsPubliceret
  LOOP

    INSERT INTO klassifikation_tils_publiceret (
      virkning,
      publiceret,
      klassifikation_registrering_id
    )
    SELECT
      klassifikation_tils_publiceret_obj.virkning,
      klassifikation_tils_publiceret_obj.publiceret,
      klassifikation_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO klassifikation_relation (
      klassifikation_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      klassifikation_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(klassifikation_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_klassifikation(array[klassifikation_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[klassifikation_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import klassifikation with uuid [%]. Object does not met stipulated criteria:%',klassifikation_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN klassifikation_uuid;

END;
$function$

;

-- as_create_or_import_organisationenhed(organisationenhedregistreringtype,uuid,organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_organisationenhed(
    organisationenhed_registrering organisationenhedregistreringtype,
    organisationenhed_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::organisationenhedregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE organisationenhed_registrering_id bigint;


    organisationenhed_attr_egenskaber_obj organisationenhedEgenskaberAttrType;



    organisationenhed_tils_gyldighed_obj organisationenhedGyldighedTilsType;


    organisationenhed_relationer OrganisationenhedRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_organisationenhed_registrering organisationenhed_registrering;
BEGIN
    IF organisationenhed_uuid IS NULL THEN LOOP
        organisationenhed_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from organisationenhed WHERE id=organisationenhed_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from organisationenhed WHERE id=organisationenhed_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (organisationenhed_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (organisationenhed_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (organisationenhed_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_organisationenhed.',(organisationenhed_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO organisationenhed (ID) SELECT
        organisationenhed_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        organisationenhed_registrering_id:=nextval('organisationenhed_registrering_id_seq');

        INSERT INTO organisationenhed_registrering (id, organisationenhed_id,
            registrering) SELECT organisationenhed_registrering_id,
        organisationenhed_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (organisationenhed_registrering.registrering).livscykluskode,
        (organisationenhed_registrering.registrering).brugerref,
        (organisationenhed_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_organisationenhed_registrering :=
            _as_create_organisationenhed_registrering(organisationenhed_uuid,
                (organisationenhed_registrering.registrering).livscykluskode,
                (organisationenhed_registrering.registrering).brugerref,
                (organisationenhed_registrering.registrering).note);

            organisationenhed_registrering_id := new_organisationenhed_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(organisationenhed_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [organisationenhed]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF organisationenhed_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(organisationenhed_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH organisationenhed_attr_egenskaber_obj IN ARRAY organisationenhed_registrering.attrEgenskaber
  LOOP


    INSERT INTO organisationenhed_attr_egenskaber (

      brugervendtnoegle,
      enhedsnavn,
      virkning,
      organisationenhed_registrering_id
    )
    SELECT

     organisationenhed_attr_egenskaber_obj.brugervendtnoegle,
      organisationenhed_attr_egenskaber_obj.enhedsnavn,
      organisationenhed_attr_egenskaber_obj.virkning,
      organisationenhed_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(organisationenhed_registrering.tilsGyldighed, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [gyldighed] for organisationenhed. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF organisationenhed_registrering.tilsGyldighed IS NOT NULL AND coalesce(array_length(organisationenhed_registrering.tilsGyldighed,1),0)>0 THEN
  FOREACH organisationenhed_tils_gyldighed_obj IN ARRAY organisationenhed_registrering.tilsGyldighed
  LOOP

    INSERT INTO organisationenhed_tils_gyldighed (
      virkning,
      gyldighed,
      organisationenhed_registrering_id
    )
    SELECT
      organisationenhed_tils_gyldighed_obj.virkning,
      organisationenhed_tils_gyldighed_obj.gyldighed,
      organisationenhed_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO organisationenhed_relation (
      organisationenhed_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      organisationenhed_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(organisationenhed_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationenhed(array[organisationenhed_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[organisationenhed_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import organisationenhed with uuid [%]. Object does not met stipulated criteria:%',organisationenhed_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN organisationenhed_uuid;

END;
$function$

;

-- as_create_or_import_organisationfunktion(organisationfunktionregistreringtype,uuid,organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_organisationfunktion(
    organisationfunktion_registrering organisationfunktionregistreringtype,
    organisationfunktion_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::organisationfunktionregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE organisationfunktion_registrering_id bigint;


    organisationfunktion_attr_egenskaber_obj organisationfunktionEgenskaberAttrType;

    organisationfunktion_attr_udvidelser_obj organisationfunktionUdvidelserAttrType;



    organisationfunktion_tils_gyldighed_obj organisationfunktionGyldighedTilsType;


    organisationfunktion_relationer OrganisationfunktionRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_organisationfunktion_registrering organisationfunktion_registrering;
BEGIN
    IF organisationfunktion_uuid IS NULL THEN LOOP
        organisationfunktion_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from organisationfunktion WHERE id=organisationfunktion_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from organisationfunktion WHERE id=organisationfunktion_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (organisationfunktion_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (organisationfunktion_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (organisationfunktion_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_organisationfunktion.',(organisationfunktion_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO organisationfunktion (ID) SELECT
        organisationfunktion_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        organisationfunktion_registrering_id:=nextval('organisationfunktion_registrering_id_seq');

        INSERT INTO organisationfunktion_registrering (id, organisationfunktion_id,
            registrering) SELECT organisationfunktion_registrering_id,
        organisationfunktion_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (organisationfunktion_registrering.registrering).livscykluskode,
        (organisationfunktion_registrering.registrering).brugerref,
        (organisationfunktion_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_organisationfunktion_registrering :=
            _as_create_organisationfunktion_registrering(organisationfunktion_uuid,
                (organisationfunktion_registrering.registrering).livscykluskode,
                (organisationfunktion_registrering.registrering).brugerref,
                (organisationfunktion_registrering.registrering).note);

            organisationfunktion_registrering_id := new_organisationfunktion_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(organisationfunktion_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [organisationfunktion]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF organisationfunktion_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(organisationfunktion_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH organisationfunktion_attr_egenskaber_obj IN ARRAY organisationfunktion_registrering.attrEgenskaber
  LOOP


    INSERT INTO organisationfunktion_attr_egenskaber (

      brugervendtnoegle,
      funktionsnavn,
      virkning,
      organisationfunktion_registrering_id
    )
    SELECT

     organisationfunktion_attr_egenskaber_obj.brugervendtnoegle,
      organisationfunktion_attr_egenskaber_obj.funktionsnavn,
      organisationfunktion_attr_egenskaber_obj.virkning,
      organisationfunktion_registrering_id
    ;


  END LOOP;
END IF;


IF organisationfunktion_registrering.attrUdvidelser IS NOT NULL and coalesce(array_length(organisationfunktion_registrering.attrUdvidelser,1),0)>0 THEN
  FOREACH organisationfunktion_attr_udvidelser_obj IN ARRAY organisationfunktion_registrering.attrUdvidelser
  LOOP


    INSERT INTO organisationfunktion_attr_udvidelser (

      primær,
      fraktion,
      udvidelse_1,
      udvidelse_2,
      udvidelse_3,
      udvidelse_4,
      udvidelse_5,
      udvidelse_6,
      udvidelse_7,
      udvidelse_8,
      udvidelse_9,
      udvidelse_10,
      virkning,
      organisationfunktion_registrering_id
    )
    SELECT

     organisationfunktion_attr_udvidelser_obj.primær,
      organisationfunktion_attr_udvidelser_obj.fraktion,
      organisationfunktion_attr_udvidelser_obj.udvidelse_1,
      organisationfunktion_attr_udvidelser_obj.udvidelse_2,
      organisationfunktion_attr_udvidelser_obj.udvidelse_3,
      organisationfunktion_attr_udvidelser_obj.udvidelse_4,
      organisationfunktion_attr_udvidelser_obj.udvidelse_5,
      organisationfunktion_attr_udvidelser_obj.udvidelse_6,
      organisationfunktion_attr_udvidelser_obj.udvidelse_7,
      organisationfunktion_attr_udvidelser_obj.udvidelse_8,
      organisationfunktion_attr_udvidelser_obj.udvidelse_9,
      organisationfunktion_attr_udvidelser_obj.udvidelse_10,
      organisationfunktion_attr_udvidelser_obj.virkning,
      organisationfunktion_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(organisationfunktion_registrering.tilsGyldighed, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [gyldighed] for organisationfunktion. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF organisationfunktion_registrering.tilsGyldighed IS NOT NULL AND coalesce(array_length(organisationfunktion_registrering.tilsGyldighed,1),0)>0 THEN
  FOREACH organisationfunktion_tils_gyldighed_obj IN ARRAY organisationfunktion_registrering.tilsGyldighed
  LOOP

    INSERT INTO organisationfunktion_tils_gyldighed (
      virkning,
      gyldighed,
      organisationfunktion_registrering_id
    )
    SELECT
      organisationfunktion_tils_gyldighed_obj.virkning,
      organisationfunktion_tils_gyldighed_obj.gyldighed,
      organisationfunktion_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO organisationfunktion_relation (
      organisationfunktion_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      organisationfunktion_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(organisationfunktion_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationfunktion(array[organisationfunktion_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[organisationfunktion_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import organisationfunktion with uuid [%]. Object does not met stipulated criteria:%',organisationfunktion_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN organisationfunktion_uuid;

END;
$function$

;

-- as_create_or_import_organisation(organisationregistreringtype,uuid,organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_create_or_import_organisation(
    organisation_registrering organisationregistreringtype,
    organisation_uuid uuid DEFAULT NULL::uuid,
    auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::organisationregistreringtype[]
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$ DECLARE organisation_registrering_id bigint;


    organisation_attr_egenskaber_obj organisationEgenskaberAttrType;



    organisation_tils_gyldighed_obj organisationGyldighedTilsType;


    organisation_relationer OrganisationRelationType;



    auth_filtered_uuids uuid[];



    does_exist boolean;
    new_organisation_registrering organisation_registrering;
BEGIN
    IF organisation_uuid IS NULL THEN LOOP
        organisation_uuid:=uuid_generate_v4(); EXIT WHEN NOT EXISTS (SELECT id
            from organisation WHERE id=organisation_uuid); END LOOP; END IF;

    IF EXISTS (SELECT id from organisation WHERE id=organisation_uuid) THEN
        does_exist = True; ELSE

        does_exist = False; END IF;

    IF
        (organisation_registrering.registrering).livscykluskode<>'Opstaaet'::Livscykluskode
        and
        (organisation_registrering.registrering).livscykluskode<>'Importeret'::Livscykluskode
        and
        (organisation_registrering.registrering).livscykluskode<>'Rettet'::Livscykluskode
        THEN RAISE EXCEPTION 'Invalid livscykluskode[%] invoking
        as_create_or_import_organisation.',(organisation_registrering.registrering).livscykluskode
        USING ERRCODE='MO400'; END IF;

    IF NOT does_exist THEN INSERT INTO organisation (ID) SELECT
        organisation_uuid; END IF;

    /*********************************/
    --Insert new registrering

    IF NOT does_exist THEN
        organisation_registrering_id:=nextval('organisation_registrering_id_seq');

        INSERT INTO organisation_registrering (id, organisation_id,
            registrering) SELECT organisation_registrering_id,
        organisation_uuid, ROW (
            TSTZRANGE(clock_timestamp(),'infinity'::TIMESTAMPTZ,'[)' ),
        (organisation_registrering.registrering).livscykluskode,
        (organisation_registrering.registrering).brugerref,
        (organisation_registrering.registrering).note):: RegistreringBase ;
    ELSE
        -- This is an update, not an import or create
            new_organisation_registrering :=
            _as_create_organisation_registrering(organisation_uuid,
                (organisation_registrering.registrering).livscykluskode,
                (organisation_registrering.registrering).brugerref,
                (organisation_registrering.registrering).note);

            organisation_registrering_id := new_organisation_registrering.id;
    END IF;


/*********************************/
--Insert attributes


/************/
--Verification
--For now all declared attributes are mandatory (the fields are all optional,though)

IF coalesce(array_length(organisation_registrering.attrEgenskaber,
    1),0)<1 THEN RAISE EXCEPTION 'Savner påkrævet attribut [egenskaber] for
    [organisation]. Oprettelse afbrydes.' USING ERRCODE='MO400'; END IF;

IF organisation_registrering.attrEgenskaber IS NOT NULL and coalesce(array_length(organisation_registrering.attrEgenskaber,1),0)>0 THEN
  FOREACH organisation_attr_egenskaber_obj IN ARRAY organisation_registrering.attrEgenskaber
  LOOP


    INSERT INTO organisation_attr_egenskaber (

      brugervendtnoegle,
      organisationsnavn,
      virkning,
      organisation_registrering_id
    )
    SELECT

     organisation_attr_egenskaber_obj.brugervendtnoegle,
      organisation_attr_egenskaber_obj.organisationsnavn,
      organisation_attr_egenskaber_obj.virkning,
      organisation_registrering_id
    ;


  END LOOP;
END IF;

/*********************************/
--Insert states (tilstande)


--Verification
--For now all declared states are mandatory.
IF coalesce(array_length(organisation_registrering.tilsGyldighed, 1),0)<1 THEN
  RAISE EXCEPTION 'Savner påkraevet tilstand [gyldighed] for organisation. Oprettelse afbrydes.' USING ERRCODE='MO400';
END IF;

IF organisation_registrering.tilsGyldighed IS NOT NULL AND coalesce(array_length(organisation_registrering.tilsGyldighed,1),0)>0 THEN
  FOREACH organisation_tils_gyldighed_obj IN ARRAY organisation_registrering.tilsGyldighed
  LOOP

    INSERT INTO organisation_tils_gyldighed (
      virkning,
      gyldighed,
      organisation_registrering_id
    )
    SELECT
      organisation_tils_gyldighed_obj.virkning,
      organisation_tils_gyldighed_obj.gyldighed,
      organisation_registrering_id;

  END LOOP;
END IF;

/*********************************/
--Insert relations



    INSERT INTO organisation_relation (
      organisation_registrering_id,
      virkning,
      rel_maal_uuid,
      rel_maal_urn,
      rel_type,
      objekt_type
    )
    SELECT
      organisation_registrering_id,
      a.virkning,
      a.uuid,
      a.urn,
      a.relType,
      a.objektType
    FROM unnest(organisation_registrering.relationer) a
  ;




/*** Verify that the object meets the stipulated access allowed criteria  ***/
/*** NOTICE: We are doing this check *after* the insertion of data BUT *before* transaction commit, to reuse code / avoid fragmentation  ***/
auth_filtered_uuids:=_as_filter_unauth_organisation(array[organisation_uuid]::uuid[],auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=1 AND auth_filtered_uuids @>ARRAY[organisation_uuid]) THEN
  RAISE EXCEPTION 'Unable to create/import organisation with uuid [%]. Object does not met stipulated criteria:%',organisation_uuid,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/




RETURN organisation_uuid;

END;
$function$

;

-- _as_filter_unauth_bruger(uuid[],brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_bruger(
    bruger_uuids uuid[], registreringobjarr brugerregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	bruger_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	bruger_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj BrugerEgenskaberAttrType;
	attrUdvidelserTypeObj BrugerUdvidelserAttrType;

  	tilsGyldighedTypeObj BrugerGyldighedTilsType;
	relationTypeObj BrugerRelationType;
	registreringObj BrugerRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN bruger_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF bruger_uuids IS NULL OR coalesce(array_length(bruger_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

bruger_candidates:= bruger_uuids;



--RAISE DEBUG 'bruger_candidates_is_initialized step 1:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 1:%',bruger_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_bruger: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(bruger_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			bruger_candidates:=array(
			SELECT DISTINCT
			b.bruger_id
			FROM  bruger_attr_egenskaber a
			JOIN bruger_registrering b on a.bruger_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.brugernavn IS NULL
					OR
					a.brugernavn = attrEgenskaberTypeObj.brugernavn
				)
				AND
				(
					attrEgenskaberTypeObj.brugertype IS NULL
					OR
					a.brugertype = attrEgenskaberTypeObj.brugertype
				)
				AND b.bruger_id = ANY (bruger_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--/**********************************************************//
--Filtration on attribute: Udvidelser
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrUdvidelser IS NULL THEN
	--RAISE DEBUG 'as_search_bruger: skipping filtration on attrUdvidelser';
ELSE
	IF coalesce(array_length(bruger_candidates,1),0)>0 THEN
		FOREACH attrUdvidelserTypeObj IN ARRAY registreringObj.attrUdvidelser
		LOOP
			bruger_candidates:=array(
			SELECT DISTINCT
			b.bruger_id
			FROM  bruger_attr_udvidelser a
			JOIN bruger_registrering b on a.bruger_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrUdvidelserTypeObj.fornavn IS NULL
					OR
					a.fornavn = attrUdvidelserTypeObj.fornavn
				)
				AND
				(
					attrUdvidelserTypeObj.efternavn IS NULL
					OR
					a.efternavn = attrUdvidelserTypeObj.efternavn
				)
				AND
				(
					attrUdvidelserTypeObj.kaldenavn_fornavn IS NULL
					OR
					a.kaldenavn_fornavn = attrUdvidelserTypeObj.kaldenavn_fornavn
				)
				AND
				(
					attrUdvidelserTypeObj.kaldenavn_efternavn IS NULL
					OR
					a.kaldenavn_efternavn = attrUdvidelserTypeObj.kaldenavn_efternavn
				)
				AND
				(
					attrUdvidelserTypeObj.seniority IS NULL
					OR
					a.seniority = attrUdvidelserTypeObj.seniority
				)
				AND b.bruger_id = ANY (bruger_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'bruger_candidates_is_initialized step 3:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 3:%',bruger_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
	--RAISE DEBUG 'as_search_bruger: skipping filtration on tilsGyldighed';
ELSE
	IF coalesce(array_length(bruger_candidates,1),0)>0 THEN

		FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
		LOOP
			bruger_candidates:=array(
			SELECT DISTINCT
			b.bruger_id
			FROM  bruger_tils_gyldighed a
			JOIN bruger_registrering b on a.bruger_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsGyldighedTypeObj.gyldighed IS NULL
					OR
					tilsGyldighedTypeObj.gyldighed = a.gyldighed
				)
				AND b.bruger_id = ANY (bruger_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer BrugerRelationType[]
*/


--RAISE DEBUG 'bruger_candidates_is_initialized step 4:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 4:%',bruger_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_bruger: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(bruger_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			bruger_candidates:=array(
			SELECT DISTINCT
			b.bruger_id
			FROM  bruger_relation a
			JOIN bruger_registrering b on a.bruger_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.bruger_id = ANY (bruger_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'bruger_candidates_is_initialized step 5:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 5:%',bruger_candidates;

bruger_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (bruger_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (bruger_candidates) b(id)
);

--optimization
IF coalesce(array_length(bruger_passed_auth_filter,1),0)=coalesce(array_length(bruger_uuids,1),0) AND bruger_passed_auth_filter @>bruger_uuids THEN
	RETURN bruger_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN bruger_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_facet(uuid[],facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_facet(
    facet_uuids uuid[], registreringobjarr facetregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	facet_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	facet_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj FacetEgenskaberAttrType;

  	tilsPubliceretTypeObj FacetPubliceretTilsType;
	relationTypeObj FacetRelationType;
	registreringObj FacetRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN facet_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF facet_uuids IS NULL OR coalesce(array_length(facet_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

facet_candidates:= facet_uuids;



--RAISE DEBUG 'facet_candidates_is_initialized step 1:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 1:%',facet_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_facet: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(facet_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			facet_candidates:=array(
			SELECT DISTINCT
			b.facet_id
			FROM  facet_attr_egenskaber a
			JOIN facet_registrering b on a.facet_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.beskrivelse IS NULL
					OR
					a.beskrivelse = attrEgenskaberTypeObj.beskrivelse
				)
				AND
				(
					attrEgenskaberTypeObj.opbygning IS NULL
					OR
					a.opbygning = attrEgenskaberTypeObj.opbygning
				)
				AND
				(
					attrEgenskaberTypeObj.ophavsret IS NULL
					OR
					a.ophavsret = attrEgenskaberTypeObj.ophavsret
				)
				AND
				(
					attrEgenskaberTypeObj.plan IS NULL
					OR
					a.plan = attrEgenskaberTypeObj.plan
				)
				AND
				(
					attrEgenskaberTypeObj.supplement IS NULL
					OR
					a.supplement = attrEgenskaberTypeObj.supplement
				)
				AND
				(
					attrEgenskaberTypeObj.retskilde IS NULL
					OR
					a.retskilde = attrEgenskaberTypeObj.retskilde
				)
				AND b.facet_id = ANY (facet_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'facet_candidates_is_initialized step 3:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 3:%',facet_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
	--RAISE DEBUG 'as_search_facet: skipping filtration on tilsPubliceret';
ELSE
	IF coalesce(array_length(facet_candidates,1),0)>0 THEN

		FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
		LOOP
			facet_candidates:=array(
			SELECT DISTINCT
			b.facet_id
			FROM  facet_tils_publiceret a
			JOIN facet_registrering b on a.facet_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsPubliceretTypeObj.publiceret IS NULL
					OR
					tilsPubliceretTypeObj.publiceret = a.publiceret
				)
				AND b.facet_id = ANY (facet_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer FacetRelationType[]
*/


--RAISE DEBUG 'facet_candidates_is_initialized step 4:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 4:%',facet_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_facet: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(facet_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			facet_candidates:=array(
			SELECT DISTINCT
			b.facet_id
			FROM  facet_relation a
			JOIN facet_registrering b on a.facet_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.facet_id = ANY (facet_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'facet_candidates_is_initialized step 5:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 5:%',facet_candidates;

facet_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (facet_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (facet_candidates) b(id)
);

--optimization
IF coalesce(array_length(facet_passed_auth_filter,1),0)=coalesce(array_length(facet_uuids,1),0) AND facet_passed_auth_filter @>facet_uuids THEN
	RETURN facet_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN facet_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_itsystem(uuid[],itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_itsystem(
    itsystem_uuids uuid[], registreringobjarr itsystemregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	itsystem_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	itsystem_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj ItsystemEgenskaberAttrType;

  	tilsGyldighedTypeObj ItsystemGyldighedTilsType;
	relationTypeObj ItsystemRelationType;
	registreringObj ItsystemRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN itsystem_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF itsystem_uuids IS NULL OR coalesce(array_length(itsystem_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

itsystem_candidates:= itsystem_uuids;



--RAISE DEBUG 'itsystem_candidates_is_initialized step 1:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 1:%',itsystem_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_itsystem: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(itsystem_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			itsystem_candidates:=array(
			SELECT DISTINCT
			b.itsystem_id
			FROM  itsystem_attr_egenskaber a
			JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.itsystemnavn IS NULL
					OR
					a.itsystemnavn = attrEgenskaberTypeObj.itsystemnavn
				)
				AND
				(
					attrEgenskaberTypeObj.itsystemtype IS NULL
					OR
					a.itsystemtype = attrEgenskaberTypeObj.itsystemtype
				)
				AND
				(
					attrEgenskaberTypeObj.konfigurationreference IS NULL
					OR
						((coalesce(array_length(attrEgenskaberTypeObj.konfigurationreference,1),0)=0 AND coalesce(array_length(a.konfigurationreference,1),0)=0 ) OR (attrEgenskaberTypeObj.konfigurationreference @> a.konfigurationreference AND a.konfigurationreference @>attrEgenskaberTypeObj.konfigurationreference  ))
				)
				AND b.itsystem_id = ANY (itsystem_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'itsystem_candidates_is_initialized step 3:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 3:%',itsystem_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
	--RAISE DEBUG 'as_search_itsystem: skipping filtration on tilsGyldighed';
ELSE
	IF coalesce(array_length(itsystem_candidates,1),0)>0 THEN

		FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
		LOOP
			itsystem_candidates:=array(
			SELECT DISTINCT
			b.itsystem_id
			FROM  itsystem_tils_gyldighed a
			JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsGyldighedTypeObj.gyldighed IS NULL
					OR
					tilsGyldighedTypeObj.gyldighed = a.gyldighed
				)
				AND b.itsystem_id = ANY (itsystem_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer ItsystemRelationType[]
*/


--RAISE DEBUG 'itsystem_candidates_is_initialized step 4:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 4:%',itsystem_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_itsystem: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(itsystem_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			itsystem_candidates:=array(
			SELECT DISTINCT
			b.itsystem_id
			FROM  itsystem_relation a
			JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.itsystem_id = ANY (itsystem_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'itsystem_candidates_is_initialized step 5:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 5:%',itsystem_candidates;

itsystem_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (itsystem_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (itsystem_candidates) b(id)
);

--optimization
IF coalesce(array_length(itsystem_passed_auth_filter,1),0)=coalesce(array_length(itsystem_uuids,1),0) AND itsystem_passed_auth_filter @>itsystem_uuids THEN
	RETURN itsystem_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN itsystem_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_klasse(uuid[],klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_klasse(
    klasse_uuids uuid[], registreringobjarr klasseregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	klasse_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	klasse_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj KlasseEgenskaberAttrType;

  	tilsPubliceretTypeObj KlassePubliceretTilsType;
	relationTypeObj KlasseRelationType;
	registreringObj KlasseRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN klasse_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF klasse_uuids IS NULL OR coalesce(array_length(klasse_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

klasse_candidates:= klasse_uuids;



--RAISE DEBUG 'klasse_candidates_is_initialized step 1:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 1:%',klasse_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_klasse: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(klasse_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			klasse_candidates:=array(
			SELECT DISTINCT
			b.klasse_id
			FROM  klasse_attr_egenskaber a
			JOIN klasse_registrering b on a.klasse_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.beskrivelse IS NULL
					OR
					a.beskrivelse = attrEgenskaberTypeObj.beskrivelse
				)
				AND
				(
					attrEgenskaberTypeObj.eksempel IS NULL
					OR
					a.eksempel = attrEgenskaberTypeObj.eksempel
				)
				AND
				(
					attrEgenskaberTypeObj.omfang IS NULL
					OR
					a.omfang = attrEgenskaberTypeObj.omfang
				)
				AND
				(
					attrEgenskaberTypeObj.titel IS NULL
					OR
					a.titel = attrEgenskaberTypeObj.titel
				)
				AND
				(
					attrEgenskaberTypeObj.retskilde IS NULL
					OR
					a.retskilde = attrEgenskaberTypeObj.retskilde
				)
				AND
				(
					attrEgenskaberTypeObj.aendringsnotat IS NULL
					OR
					a.aendringsnotat = attrEgenskaberTypeObj.aendringsnotat
				)
				AND b.klasse_id = ANY (klasse_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'klasse_candidates_is_initialized step 3:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 3:%',klasse_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
	--RAISE DEBUG 'as_search_klasse: skipping filtration on tilsPubliceret';
ELSE
	IF coalesce(array_length(klasse_candidates,1),0)>0 THEN

		FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
		LOOP
			klasse_candidates:=array(
			SELECT DISTINCT
			b.klasse_id
			FROM  klasse_tils_publiceret a
			JOIN klasse_registrering b on a.klasse_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsPubliceretTypeObj.publiceret IS NULL
					OR
					tilsPubliceretTypeObj.publiceret = a.publiceret
				)
				AND b.klasse_id = ANY (klasse_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer KlasseRelationType[]
*/


--RAISE DEBUG 'klasse_candidates_is_initialized step 4:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 4:%',klasse_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_klasse: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(klasse_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			klasse_candidates:=array(
			SELECT DISTINCT
			b.klasse_id
			FROM  klasse_relation a
			JOIN klasse_registrering b on a.klasse_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.klasse_id = ANY (klasse_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'klasse_candidates_is_initialized step 5:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 5:%',klasse_candidates;

klasse_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (klasse_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (klasse_candidates) b(id)
);

--optimization
IF coalesce(array_length(klasse_passed_auth_filter,1),0)=coalesce(array_length(klasse_uuids,1),0) AND klasse_passed_auth_filter @>klasse_uuids THEN
	RETURN klasse_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN klasse_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_klassifikation(uuid[],klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_klassifikation(
    klassifikation_uuids uuid[],
    registreringobjarr klassifikationregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	klassifikation_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	klassifikation_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj KlassifikationEgenskaberAttrType;

  	tilsPubliceretTypeObj KlassifikationPubliceretTilsType;
	relationTypeObj KlassifikationRelationType;
	registreringObj KlassifikationRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN klassifikation_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF klassifikation_uuids IS NULL OR coalesce(array_length(klassifikation_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

klassifikation_candidates:= klassifikation_uuids;



--RAISE DEBUG 'klassifikation_candidates_is_initialized step 1:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 1:%',klassifikation_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_klassifikation: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(klassifikation_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			klassifikation_candidates:=array(
			SELECT DISTINCT
			b.klassifikation_id
			FROM  klassifikation_attr_egenskaber a
			JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.beskrivelse IS NULL
					OR
					a.beskrivelse = attrEgenskaberTypeObj.beskrivelse
				)
				AND
				(
					attrEgenskaberTypeObj.kaldenavn IS NULL
					OR
					a.kaldenavn = attrEgenskaberTypeObj.kaldenavn
				)
				AND
				(
					attrEgenskaberTypeObj.ophavsret IS NULL
					OR
					a.ophavsret = attrEgenskaberTypeObj.ophavsret
				)
				AND b.klassifikation_id = ANY (klassifikation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'klassifikation_candidates_is_initialized step 3:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 3:%',klassifikation_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
	--RAISE DEBUG 'as_search_klassifikation: skipping filtration on tilsPubliceret';
ELSE
	IF coalesce(array_length(klassifikation_candidates,1),0)>0 THEN

		FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
		LOOP
			klassifikation_candidates:=array(
			SELECT DISTINCT
			b.klassifikation_id
			FROM  klassifikation_tils_publiceret a
			JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsPubliceretTypeObj.publiceret IS NULL
					OR
					tilsPubliceretTypeObj.publiceret = a.publiceret
				)
				AND b.klassifikation_id = ANY (klassifikation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer KlassifikationRelationType[]
*/


--RAISE DEBUG 'klassifikation_candidates_is_initialized step 4:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 4:%',klassifikation_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_klassifikation: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(klassifikation_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			klassifikation_candidates:=array(
			SELECT DISTINCT
			b.klassifikation_id
			FROM  klassifikation_relation a
			JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.klassifikation_id = ANY (klassifikation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'klassifikation_candidates_is_initialized step 5:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 5:%',klassifikation_candidates;

klassifikation_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (klassifikation_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (klassifikation_candidates) b(id)
);

--optimization
IF coalesce(array_length(klassifikation_passed_auth_filter,1),0)=coalesce(array_length(klassifikation_uuids,1),0) AND klassifikation_passed_auth_filter @>klassifikation_uuids THEN
	RETURN klassifikation_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN klassifikation_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_organisationenhed(uuid[],organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_organisationenhed(
    organisationenhed_uuids uuid[],
    registreringobjarr organisationenhedregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	organisationenhed_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	organisationenhed_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj OrganisationenhedEgenskaberAttrType;

  	tilsGyldighedTypeObj OrganisationenhedGyldighedTilsType;
	relationTypeObj OrganisationenhedRelationType;
	registreringObj OrganisationenhedRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN organisationenhed_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF organisationenhed_uuids IS NULL OR coalesce(array_length(organisationenhed_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

organisationenhed_candidates:= organisationenhed_uuids;



--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 1:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 1:%',organisationenhed_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_organisationenhed: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(organisationenhed_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			organisationenhed_candidates:=array(
			SELECT DISTINCT
			b.organisationenhed_id
			FROM  organisationenhed_attr_egenskaber a
			JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.enhedsnavn IS NULL
					OR
					a.enhedsnavn = attrEgenskaberTypeObj.enhedsnavn
				)
				AND b.organisationenhed_id = ANY (organisationenhed_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 3:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 3:%',organisationenhed_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
	--RAISE DEBUG 'as_search_organisationenhed: skipping filtration on tilsGyldighed';
ELSE
	IF coalesce(array_length(organisationenhed_candidates,1),0)>0 THEN

		FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
		LOOP
			organisationenhed_candidates:=array(
			SELECT DISTINCT
			b.organisationenhed_id
			FROM  organisationenhed_tils_gyldighed a
			JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsGyldighedTypeObj.gyldighed IS NULL
					OR
					tilsGyldighedTypeObj.gyldighed = a.gyldighed
				)
				AND b.organisationenhed_id = ANY (organisationenhed_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer OrganisationenhedRelationType[]
*/


--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 4:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 4:%',organisationenhed_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_organisationenhed: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(organisationenhed_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			organisationenhed_candidates:=array(
			SELECT DISTINCT
			b.organisationenhed_id
			FROM  organisationenhed_relation a
			JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.organisationenhed_id = ANY (organisationenhed_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 5:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 5:%',organisationenhed_candidates;

organisationenhed_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (organisationenhed_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (organisationenhed_candidates) b(id)
);

--optimization
IF coalesce(array_length(organisationenhed_passed_auth_filter,1),0)=coalesce(array_length(organisationenhed_uuids,1),0) AND organisationenhed_passed_auth_filter @>organisationenhed_uuids THEN
	RETURN organisationenhed_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN organisationenhed_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_organisationfunktion(uuid[],organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_organisationfunktion(
    organisationfunktion_uuids uuid[],
    registreringobjarr organisationfunktionregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	organisationfunktion_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	organisationfunktion_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj OrganisationfunktionEgenskaberAttrType;
	attrUdvidelserTypeObj OrganisationfunktionUdvidelserAttrType;

  	tilsGyldighedTypeObj OrganisationfunktionGyldighedTilsType;
	relationTypeObj OrganisationfunktionRelationType;
	registreringObj OrganisationfunktionRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN organisationfunktion_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF organisationfunktion_uuids IS NULL OR coalesce(array_length(organisationfunktion_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

organisationfunktion_candidates:= organisationfunktion_uuids;



--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 1:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 1:%',organisationfunktion_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(organisationfunktion_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			organisationfunktion_candidates:=array(
			SELECT DISTINCT
			b.organisationfunktion_id
			FROM  organisationfunktion_attr_egenskaber a
			JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.funktionsnavn IS NULL
					OR
					a.funktionsnavn = attrEgenskaberTypeObj.funktionsnavn
				)
				AND b.organisationfunktion_id = ANY (organisationfunktion_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--/**********************************************************//
--Filtration on attribute: Udvidelser
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrUdvidelser IS NULL THEN
	--RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on attrUdvidelser';
ELSE
	IF coalesce(array_length(organisationfunktion_candidates,1),0)>0 THEN
		FOREACH attrUdvidelserTypeObj IN ARRAY registreringObj.attrUdvidelser
		LOOP
			organisationfunktion_candidates:=array(
			SELECT DISTINCT
			b.organisationfunktion_id
			FROM  organisationfunktion_attr_udvidelser a
			JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrUdvidelserTypeObj.primær IS NULL
					OR
					a.primær = attrUdvidelserTypeObj.primær
				)
				AND
				(
					attrUdvidelserTypeObj.fraktion IS NULL
					OR
					a.fraktion = attrUdvidelserTypeObj.fraktion
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_1 IS NULL
					OR
					a.udvidelse_1 = attrUdvidelserTypeObj.udvidelse_1
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_2 IS NULL
					OR
					a.udvidelse_2 = attrUdvidelserTypeObj.udvidelse_2
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_3 IS NULL
					OR
					a.udvidelse_3 = attrUdvidelserTypeObj.udvidelse_3
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_4 IS NULL
					OR
					a.udvidelse_4 = attrUdvidelserTypeObj.udvidelse_4
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_5 IS NULL
					OR
					a.udvidelse_5 = attrUdvidelserTypeObj.udvidelse_5
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_6 IS NULL
					OR
					a.udvidelse_6 = attrUdvidelserTypeObj.udvidelse_6
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_7 IS NULL
					OR
					a.udvidelse_7 = attrUdvidelserTypeObj.udvidelse_7
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_8 IS NULL
					OR
					a.udvidelse_8 = attrUdvidelserTypeObj.udvidelse_8
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_9 IS NULL
					OR
					a.udvidelse_9 = attrUdvidelserTypeObj.udvidelse_9
				)
				AND
				(
					attrUdvidelserTypeObj.udvidelse_10 IS NULL
					OR
					a.udvidelse_10 = attrUdvidelserTypeObj.udvidelse_10
				)
				AND b.organisationfunktion_id = ANY (organisationfunktion_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 3:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 3:%',organisationfunktion_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
	--RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on tilsGyldighed';
ELSE
	IF coalesce(array_length(organisationfunktion_candidates,1),0)>0 THEN

		FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
		LOOP
			organisationfunktion_candidates:=array(
			SELECT DISTINCT
			b.organisationfunktion_id
			FROM  organisationfunktion_tils_gyldighed a
			JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsGyldighedTypeObj.gyldighed IS NULL
					OR
					tilsGyldighedTypeObj.gyldighed = a.gyldighed
				)
				AND b.organisationfunktion_id = ANY (organisationfunktion_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer OrganisationfunktionRelationType[]
*/


--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 4:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 4:%',organisationfunktion_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(organisationfunktion_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			organisationfunktion_candidates:=array(
			SELECT DISTINCT
			b.organisationfunktion_id
			FROM  organisationfunktion_relation a
			JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.organisationfunktion_id = ANY (organisationfunktion_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 5:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 5:%',organisationfunktion_candidates;

organisationfunktion_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (organisationfunktion_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (organisationfunktion_candidates) b(id)
);

--optimization
IF coalesce(array_length(organisationfunktion_passed_auth_filter,1),0)=coalesce(array_length(organisationfunktion_uuids,1),0) AND organisationfunktion_passed_auth_filter @>organisationfunktion_uuids THEN
	RETURN organisationfunktion_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN organisationfunktion_passed_auth_filter;


END;
$function$

;

-- _as_filter_unauth_organisation(uuid[],organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state._as_filter_unauth_organisation(
    organisation_uuids uuid[], registreringobjarr organisationregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	organisation_passed_auth_filter uuid[]:=ARRAY[]::uuid[];
	organisation_candidates uuid[];
	--to_be_applyed_filter_uuids uuid[];
	attrEgenskaberTypeObj OrganisationEgenskaberAttrType;

  	tilsGyldighedTypeObj OrganisationGyldighedTilsType;
	relationTypeObj OrganisationRelationType;
	registreringObj OrganisationRegistreringType;
	actual_virkning TIMESTAMPTZ:=current_timestamp;
BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

IF registreringObjArr IS NULL THEN
	RETURN organisation_uuids; --special case: All is allowed, no criteria present
END IF;

IF coalesce(array_length(registreringObjArr,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: Nothing is allowed. Empty list of criteria where at least one has to be met.
END IF;

IF organisation_uuids IS NULL OR coalesce(array_length(organisation_uuids,1),0)=0 THEN
	RETURN ARRAY[]::uuid[]; --special case: No candidates given to filter.
END IF;



FOREACH registreringObj IN ARRAY registreringObjArr
LOOP

organisation_candidates:= organisation_uuids;



--RAISE DEBUG 'organisation_candidates_is_initialized step 1:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 1:%',organisation_candidates;
--/****************************//

--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
	--RAISE DEBUG 'as_search_organisation: skipping filtration on attrEgenskaber';
ELSE
	IF coalesce(array_length(organisation_candidates,1),0)>0 THEN
		FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
		LOOP
			organisation_candidates:=array(
			SELECT DISTINCT
			b.organisation_id
			FROM  organisation_attr_egenskaber a
			JOIN organisation_registrering b on a.organisation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					attrEgenskaberTypeObj.brugervendtnoegle IS NULL
					OR
					a.brugervendtnoegle = attrEgenskaberTypeObj.brugervendtnoegle
				)
				AND
				(
					attrEgenskaberTypeObj.organisationsnavn IS NULL
					OR
					a.organisationsnavn = attrEgenskaberTypeObj.organisationsnavn
				)
				AND b.organisation_id = ANY (organisation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
			);

		END LOOP;
	END IF;
END IF;
--RAISE DEBUG 'organisation_candidates_is_initialized step 3:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 3:%',organisation_candidates;

--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
	--RAISE DEBUG 'as_search_organisation: skipping filtration on tilsGyldighed';
ELSE
	IF coalesce(array_length(organisation_candidates,1),0)>0 THEN

		FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
		LOOP
			organisation_candidates:=array(
			SELECT DISTINCT
			b.organisation_id
			FROM  organisation_tils_gyldighed a
			JOIN organisation_registrering b on a.organisation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					tilsGyldighedTypeObj.gyldighed IS NULL
					OR
					tilsGyldighedTypeObj.gyldighed = a.gyldighed
				)
				AND b.organisation_id = ANY (organisation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);

		END LOOP;
	END IF;
END IF;

/*
--relationer OrganisationRelationType[]
*/


--RAISE DEBUG 'organisation_candidates_is_initialized step 4:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 4:%',organisation_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL OR coalesce(array_length((registreringObj).relationer,1),0)=0 THEN
	--RAISE DEBUG 'as_search_organisation: skipping filtration on relationer';
ELSE
	IF coalesce(array_length(organisation_candidates,1),0)>0 THEN
		FOREACH relationTypeObj IN ARRAY registreringObj.relationer
		LOOP
			organisation_candidates:=array(
			SELECT DISTINCT
			b.organisation_id
			FROM  organisation_relation a
			JOIN organisation_registrering b on a.organisation_registrering_id=b.id and upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			WHERE
				(
					relationTypeObj.relType IS NULL
					OR
					relationTypeObj.relType = a.rel_type
				)
				AND
				(
					relationTypeObj.uuid IS NULL
					OR
					relationTypeObj.uuid = a.rel_maal_uuid
				)
				AND
				(
					relationTypeObj.objektType IS NULL
					OR
					relationTypeObj.objektType = a.objekt_type
				)
				AND
				(
					relationTypeObj.urn IS NULL
					OR
					relationTypeObj.urn = a.rel_maal_urn
				)
				AND b.organisation_id = ANY (organisation_candidates)
				AND (a.virkning).TimePeriod @> actual_virkning
	);
		END LOOP;
	END IF;
END IF;
--/**********************//

--RAISE DEBUG 'organisation_candidates_is_initialized step 5:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 5:%',organisation_candidates;

organisation_passed_auth_filter:=array(
SELECT
a.id
FROM
unnest (organisation_passed_auth_filter) a(id)
UNION
SELECT
b.id
FROM
unnest (organisation_candidates) b(id)
);

--optimization
IF coalesce(array_length(organisation_passed_auth_filter,1),0)=coalesce(array_length(organisation_uuids,1),0) AND organisation_passed_auth_filter @>organisation_uuids THEN
	RETURN organisation_passed_auth_filter;
END IF;


END LOOP; --LOOP registreringObj


RETURN organisation_passed_auth_filter;


END;
$function$

;

-- as_list_bruger(uuid[],tstzrange,tstzrange,brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_bruger(
    bruger_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::brugerregistreringtype[]
)
RETURNS brugertype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result BrugerType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_bruger(bruger_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(bruger_uuids,1),0) AND auth_filtered_uuids @>bruger_uuids) THEN
  RAISE EXCEPTION 'Unable to list bruger with uuids [%]. All objects do not fullfill the stipulated criteria:%',bruger_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.brugerObj) into result
FROM
(
SELECT
ROW(
	a.bruger_id,
	array_agg(
		ROW (
			a.registrering,
			a.BrugerTilsGyldighedArr,
			a.BrugerAttrEgenskaberArr,
			a.BrugerAttrUdvidelserArr,
			a.BrugerRelationArr
		)::BrugerRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: BrugerType  brugerObj
FROM
(
	SELECT
	a.bruger_id,
	a.bruger_registrering_id,
	a.registrering,
	a.BrugerAttrEgenskaberArr,
	a.BrugerAttrUdvidelserArr,
	a.BrugerTilsGyldighedArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: BrugerRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) BrugerRelationArr
	FROM
	(
			SELECT
			a.bruger_id,
			a.bruger_registrering_id,
			a.registrering,
			a.BrugerAttrEgenskaberArr,
			a.BrugerAttrUdvidelserArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.gyldighed
						) ::BrugerGyldighedTilsType
					ELSE NULL
					END
					order by b.gyldighed,b.virkning
				)) BrugerTilsGyldighedArr
			FROM
			(
					SELECT
					a.bruger_id,
					a.bruger_registrering_id,
					a.registrering,
					a.BrugerAttrUdvidelserArr,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.brugernavn,
					 		b.brugertype,
					   		b.virkning

							)::BrugerEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.brugernavn,b.brugertype,b.virkning

					)) BrugerAttrEgenskaberArr

					FROM
					(
					SELECT
					a.bruger_id,
					a.bruger_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.fornavn,
					 		b.efternavn,
					 		b.kaldenavn_fornavn,
					 		b.kaldenavn_efternavn,
					 		b.seniority,
					   		b.virkning

							)::BrugerUdvidelserAttrType
						ELSE
						NULL
						END

						order by b.fornavn,b.efternavn,b.kaldenavn_fornavn,b.kaldenavn_efternavn,b.seniority,b.virkning

					)) BrugerAttrUdvidelserArr

					FROM
					(
					SELECT
					a.id bruger_id,
					b.id bruger_registrering_id,
					b.registrering
					FROM		bruger a
					JOIN 		bruger_registrering b 	ON b.bruger_id=a.id
					WHERE a.id = ANY (bruger_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN bruger_attr_udvidelser as b ON b.bruger_registrering_id=a.bruger_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.bruger_id,
					a.bruger_registrering_id,
					a.registrering
					) as a
					LEFT JOIN bruger_attr_egenskaber as b ON b.bruger_registrering_id=a.bruger_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.bruger_id,
					a.bruger_registrering_id,
					a.registrering,
					a.BrugerAttrUdvidelserArr
			) as a
			LEFT JOIN bruger_tils_gyldighed as b ON b.bruger_registrering_id=a.bruger_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.bruger_id,
			a.bruger_registrering_id,
			a.registrering,
			a.BrugerAttrUdvidelserArr,
			a.BrugerAttrEgenskaberArr
	) as a
	LEFT JOIN bruger_relation b ON b.bruger_registrering_id=a.bruger_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.bruger_id,
	a.bruger_registrering_id,
	a.registrering,
	a.BrugerAttrUdvidelserArr,
	a.BrugerAttrEgenskaberArr,
	a.BrugerTilsGyldighedArr
) as a

WHERE a.bruger_id IS NOT NULL
GROUP BY
a.bruger_id
order by a.bruger_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_facet(uuid[],tstzrange,tstzrange,facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_facet(
    facet_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr facetregistreringtype[] DEFAULT NULL::facetregistreringtype[]
)
RETURNS facettype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result FacetType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_facet(facet_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(facet_uuids,1),0) AND auth_filtered_uuids @>facet_uuids) THEN
  RAISE EXCEPTION 'Unable to list facet with uuids [%]. All objects do not fullfill the stipulated criteria:%',facet_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.facetObj) into result
FROM
(
SELECT
ROW(
	a.facet_id,
	array_agg(
		ROW (
			a.registrering,
			a.FacetTilsPubliceretArr,
			a.FacetAttrEgenskaberArr,
			a.FacetRelationArr
		)::FacetRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: FacetType  facetObj
FROM
(
	SELECT
	a.facet_id,
	a.facet_registrering_id,
	a.registrering,
	a.FacetAttrEgenskaberArr,
	a.FacetTilsPubliceretArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: FacetRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) FacetRelationArr
	FROM
	(
			SELECT
			a.facet_id,
			a.facet_registrering_id,
			a.registrering,
			a.FacetAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.publiceret
						) ::FacetPubliceretTilsType
					ELSE NULL
					END
					order by b.publiceret,b.virkning
				)) FacetTilsPubliceretArr
			FROM
			(
					SELECT
					a.facet_id,
					a.facet_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.beskrivelse,
					 		b.opbygning,
					 		b.ophavsret,
					 		b.plan,
					 		b.supplement,
					 		b.retskilde,
					   		b.virkning

							)::FacetEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.beskrivelse,b.opbygning,b.ophavsret,b.plan,b.supplement,b.retskilde,b.virkning

					)) FacetAttrEgenskaberArr

					FROM
					(
					SELECT
					a.id facet_id,
					b.id facet_registrering_id,
					b.registrering
					FROM		facet a
					JOIN 		facet_registrering b 	ON b.facet_id=a.id
					WHERE a.id = ANY (facet_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN facet_attr_egenskaber as b ON b.facet_registrering_id=a.facet_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.facet_id,
					a.facet_registrering_id,
					a.registrering
			) as a
			LEFT JOIN facet_tils_publiceret as b ON b.facet_registrering_id=a.facet_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.facet_id,
			a.facet_registrering_id,
			a.registrering,
			a.FacetAttrEgenskaberArr
	) as a
	LEFT JOIN facet_relation b ON b.facet_registrering_id=a.facet_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.facet_id,
	a.facet_registrering_id,
	a.registrering,
	a.FacetAttrEgenskaberArr,
	a.FacetTilsPubliceretArr
) as a

WHERE a.facet_id IS NOT NULL
GROUP BY
a.facet_id
order by a.facet_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_itsystem(uuid[],tstzrange,tstzrange,itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_itsystem(
    itsystem_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::itsystemregistreringtype[]
)
RETURNS itsystemtype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result ItsystemType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_itsystem(itsystem_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(itsystem_uuids,1),0) AND auth_filtered_uuids @>itsystem_uuids) THEN
  RAISE EXCEPTION 'Unable to list itsystem with uuids [%]. All objects do not fullfill the stipulated criteria:%',itsystem_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.itsystemObj) into result
FROM
(
SELECT
ROW(
	a.itsystem_id,
	array_agg(
		ROW (
			a.registrering,
			a.ItsystemTilsGyldighedArr,
			a.ItsystemAttrEgenskaberArr,
			a.ItsystemRelationArr
		)::ItsystemRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: ItsystemType  itsystemObj
FROM
(
	SELECT
	a.itsystem_id,
	a.itsystem_registrering_id,
	a.registrering,
	a.ItsystemAttrEgenskaberArr,
	a.ItsystemTilsGyldighedArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: ItsystemRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) ItsystemRelationArr
	FROM
	(
			SELECT
			a.itsystem_id,
			a.itsystem_registrering_id,
			a.registrering,
			a.ItsystemAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.gyldighed
						) ::ItsystemGyldighedTilsType
					ELSE NULL
					END
					order by b.gyldighed,b.virkning
				)) ItsystemTilsGyldighedArr
			FROM
			(
					SELECT
					a.itsystem_id,
					a.itsystem_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.itsystemnavn,
					 		b.itsystemtype,
					 		b.konfigurationreference,
					   		b.virkning

							)::ItsystemEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.itsystemnavn,b.itsystemtype,b.konfigurationreference,b.virkning

					)) ItsystemAttrEgenskaberArr

					FROM
					(
					SELECT
					a.id itsystem_id,
					b.id itsystem_registrering_id,
					b.registrering
					FROM		itsystem a
					JOIN 		itsystem_registrering b 	ON b.itsystem_id=a.id
					WHERE a.id = ANY (itsystem_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN itsystem_attr_egenskaber as b ON b.itsystem_registrering_id=a.itsystem_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.itsystem_id,
					a.itsystem_registrering_id,
					a.registrering
			) as a
			LEFT JOIN itsystem_tils_gyldighed as b ON b.itsystem_registrering_id=a.itsystem_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.itsystem_id,
			a.itsystem_registrering_id,
			a.registrering,
			a.ItsystemAttrEgenskaberArr
	) as a
	LEFT JOIN itsystem_relation b ON b.itsystem_registrering_id=a.itsystem_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.itsystem_id,
	a.itsystem_registrering_id,
	a.registrering,
	a.ItsystemAttrEgenskaberArr,
	a.ItsystemTilsGyldighedArr
) as a

WHERE a.itsystem_id IS NOT NULL
GROUP BY
a.itsystem_id
order by a.itsystem_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_klasse(uuid[],tstzrange,tstzrange,klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_klasse(
    klasse_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::klasseregistreringtype[]
)
RETURNS klassetype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result KlasseType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_klasse(klasse_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(klasse_uuids,1),0) AND auth_filtered_uuids @>klasse_uuids) THEN
  RAISE EXCEPTION 'Unable to list klasse with uuids [%]. All objects do not fullfill the stipulated criteria:%',klasse_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.klasseObj) into result
FROM
(
SELECT
ROW(
	a.klasse_id,
	array_agg(
		ROW (
			a.registrering,
			a.KlasseTilsPubliceretArr,
			a.KlasseAttrEgenskaberArr,
			a.KlasseRelationArr
		)::KlasseRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: KlasseType  klasseObj
FROM
(
	SELECT
	a.klasse_id,
	a.klasse_registrering_id,
	a.registrering,
	a.KlasseAttrEgenskaberArr,
	a.KlasseTilsPubliceretArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: KlasseRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) KlasseRelationArr
	FROM
	(
			SELECT
			a.klasse_id,
			a.klasse_registrering_id,
			a.registrering,
			a.KlasseAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.publiceret
						) ::KlassePubliceretTilsType
					ELSE NULL
					END
					order by b.publiceret,b.virkning
				)) KlasseTilsPubliceretArr
			FROM
			(
					SELECT
					a.klasse_id,
					a.klasse_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN a.attr_id is not null THEN

						ROW(

                                                       a.brugervendtnoegle,
                                                       a.beskrivelse,
                                                       a.eksempel,
                                                       a.omfang,
                                                       a.titel,
                                                       a.retskilde,
                                                       a.aendringsnotat,
                                                       a.KlasseAttrEgenskaberSoegeordTypeArr,
                                                       a.virkning

							)::KlasseEgenskaberAttrType
						ELSE
						NULL
						END

                        order by a.brugervendtnoegle,a.beskrivelse,a.eksempel,a.omfang,a.titel,a.retskilde,a.aendringsnotat,a.virkning,a.KlasseAttrEgenskaberSoegeordTypeArr

					)) KlasseAttrEgenskaberArr

                               FROM
                               (
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
                                               _remove_nulls_in_array(array_agg(
                                                       CASE
                                                       WHEN c.id is not null THEN
                                                       ROW(
                                                               c.soegeordidentifikator,
                                                               c.beskrivelse,
                                                               c.soegeordskategori
                                                       )::KlasseSoegeordType
                                               ELSE
                                               NULL
                                               END
                                               order by c.soegeordidentifikator,c.beskrivelse,c.soegeordskategori
                                       )) KlasseAttrEgenskaberSoegeordTypeArr

					FROM
					(
					SELECT
					a.id klasse_id,
					b.id klasse_registrering_id,
					b.registrering
					FROM		klasse a
					JOIN 		klasse_registrering b 	ON b.klasse_id=a.id
					WHERE a.id = ANY (klasse_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN klasse_attr_egenskaber as b ON b.klasse_registrering_id=a.klasse_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

                                               LEFT JOIN klasse_attr_egenskaber_soegeord as c ON c.klasse_attr_egenskaber_id=b.id
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
                                               b.virkning
                               ) as a

					GROUP BY
					a.klasse_id,
					a.klasse_registrering_id,
					a.registrering
			) as a
			LEFT JOIN klasse_tils_publiceret as b ON b.klasse_registrering_id=a.klasse_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.klasse_id,
			a.klasse_registrering_id,
			a.registrering,
			a.KlasseAttrEgenskaberArr
	) as a
	LEFT JOIN klasse_relation b ON b.klasse_registrering_id=a.klasse_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.klasse_id,
	a.klasse_registrering_id,
	a.registrering,
	a.KlasseAttrEgenskaberArr,
	a.KlasseTilsPubliceretArr
) as a

WHERE a.klasse_id IS NOT NULL
GROUP BY
a.klasse_id
order by a.klasse_id
) as x
;




RETURN result;

END;
$function$

;

-- as_list_klassifikation(uuid[],tstzrange,tstzrange,klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_klassifikation(
    klassifikation_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::klassifikationregistreringtype[]
)
RETURNS klassifikationtype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result KlassifikationType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_klassifikation(klassifikation_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(klassifikation_uuids,1),0) AND auth_filtered_uuids @>klassifikation_uuids) THEN
  RAISE EXCEPTION 'Unable to list klassifikation with uuids [%]. All objects do not fullfill the stipulated criteria:%',klassifikation_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.klassifikationObj) into result
FROM
(
SELECT
ROW(
	a.klassifikation_id,
	array_agg(
		ROW (
			a.registrering,
			a.KlassifikationTilsPubliceretArr,
			a.KlassifikationAttrEgenskaberArr,
			a.KlassifikationRelationArr
		)::KlassifikationRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: KlassifikationType  klassifikationObj
FROM
(
	SELECT
	a.klassifikation_id,
	a.klassifikation_registrering_id,
	a.registrering,
	a.KlassifikationAttrEgenskaberArr,
	a.KlassifikationTilsPubliceretArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: KlassifikationRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) KlassifikationRelationArr
	FROM
	(
			SELECT
			a.klassifikation_id,
			a.klassifikation_registrering_id,
			a.registrering,
			a.KlassifikationAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.publiceret
						) ::KlassifikationPubliceretTilsType
					ELSE NULL
					END
					order by b.publiceret,b.virkning
				)) KlassifikationTilsPubliceretArr
			FROM
			(
					SELECT
					a.klassifikation_id,
					a.klassifikation_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.beskrivelse,
					 		b.kaldenavn,
					 		b.ophavsret,
					   		b.virkning

							)::KlassifikationEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.beskrivelse,b.kaldenavn,b.ophavsret,b.virkning

					)) KlassifikationAttrEgenskaberArr

					FROM
					(
					SELECT
					a.id klassifikation_id,
					b.id klassifikation_registrering_id,
					b.registrering
					FROM		klassifikation a
					JOIN 		klassifikation_registrering b 	ON b.klassifikation_id=a.id
					WHERE a.id = ANY (klassifikation_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN klassifikation_attr_egenskaber as b ON b.klassifikation_registrering_id=a.klassifikation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.klassifikation_id,
					a.klassifikation_registrering_id,
					a.registrering
			) as a
			LEFT JOIN klassifikation_tils_publiceret as b ON b.klassifikation_registrering_id=a.klassifikation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.klassifikation_id,
			a.klassifikation_registrering_id,
			a.registrering,
			a.KlassifikationAttrEgenskaberArr
	) as a
	LEFT JOIN klassifikation_relation b ON b.klassifikation_registrering_id=a.klassifikation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.klassifikation_id,
	a.klassifikation_registrering_id,
	a.registrering,
	a.KlassifikationAttrEgenskaberArr,
	a.KlassifikationTilsPubliceretArr
) as a

WHERE a.klassifikation_id IS NOT NULL
GROUP BY
a.klassifikation_id
order by a.klassifikation_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_organisationenhed(uuid[],tstzrange,tstzrange,organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_organisationenhed(
    organisationenhed_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::organisationenhedregistreringtype[]
)
RETURNS organisationenhedtype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result OrganisationenhedType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationenhed(organisationenhed_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(organisationenhed_uuids,1),0) AND auth_filtered_uuids @>organisationenhed_uuids) THEN
  RAISE EXCEPTION 'Unable to list organisationenhed with uuids [%]. All objects do not fullfill the stipulated criteria:%',organisationenhed_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.organisationenhedObj) into result
FROM
(
SELECT
ROW(
	a.organisationenhed_id,
	array_agg(
		ROW (
			a.registrering,
			a.OrganisationenhedTilsGyldighedArr,
			a.OrganisationenhedAttrEgenskaberArr,
			a.OrganisationenhedRelationArr
		)::OrganisationenhedRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: OrganisationenhedType  organisationenhedObj
FROM
(
	SELECT
	a.organisationenhed_id,
	a.organisationenhed_registrering_id,
	a.registrering,
	a.OrganisationenhedAttrEgenskaberArr,
	a.OrganisationenhedTilsGyldighedArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: OrganisationenhedRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) OrganisationenhedRelationArr
	FROM
	(
			SELECT
			a.organisationenhed_id,
			a.organisationenhed_registrering_id,
			a.registrering,
			a.OrganisationenhedAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.gyldighed
						) ::OrganisationenhedGyldighedTilsType
					ELSE NULL
					END
					order by b.gyldighed,b.virkning
				)) OrganisationenhedTilsGyldighedArr
			FROM
			(
					SELECT
					a.organisationenhed_id,
					a.organisationenhed_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.enhedsnavn,
					   		b.virkning

							)::OrganisationenhedEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.enhedsnavn,b.virkning

					)) OrganisationenhedAttrEgenskaberArr

					FROM
					(
					SELECT
					a.id organisationenhed_id,
					b.id organisationenhed_registrering_id,
					b.registrering
					FROM		organisationenhed a
					JOIN 		organisationenhed_registrering b 	ON b.organisationenhed_id=a.id
					WHERE a.id = ANY (organisationenhed_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN organisationenhed_attr_egenskaber as b ON b.organisationenhed_registrering_id=a.organisationenhed_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.organisationenhed_id,
					a.organisationenhed_registrering_id,
					a.registrering
			) as a
			LEFT JOIN organisationenhed_tils_gyldighed as b ON b.organisationenhed_registrering_id=a.organisationenhed_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.organisationenhed_id,
			a.organisationenhed_registrering_id,
			a.registrering,
			a.OrganisationenhedAttrEgenskaberArr
	) as a
	LEFT JOIN organisationenhed_relation b ON b.organisationenhed_registrering_id=a.organisationenhed_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.organisationenhed_id,
	a.organisationenhed_registrering_id,
	a.registrering,
	a.OrganisationenhedAttrEgenskaberArr,
	a.OrganisationenhedTilsGyldighedArr
) as a

WHERE a.organisationenhed_id IS NOT NULL
GROUP BY
a.organisationenhed_id
order by a.organisationenhed_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_organisationfunktion(uuid[],tstzrange,tstzrange,organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_organisationfunktion(
    organisationfunktion_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::organisationfunktionregistreringtype[]
)
RETURNS organisationfunktiontype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result OrganisationfunktionType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationfunktion(organisationfunktion_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(organisationfunktion_uuids,1),0) AND auth_filtered_uuids @>organisationfunktion_uuids) THEN
  RAISE EXCEPTION 'Unable to list organisationfunktion with uuids [%]. All objects do not fullfill the stipulated criteria:%',organisationfunktion_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.organisationfunktionObj) into result
FROM
(
SELECT
ROW(
	a.organisationfunktion_id,
	array_agg(
		ROW (
			a.registrering,
			a.OrganisationfunktionTilsGyldighedArr,
			a.OrganisationfunktionAttrEgenskaberArr,
			a.OrganisationfunktionAttrUdvidelserArr,
			a.OrganisationfunktionRelationArr
		)::OrganisationfunktionRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: OrganisationfunktionType  organisationfunktionObj
FROM
(
	SELECT
	a.organisationfunktion_id,
	a.organisationfunktion_registrering_id,
	a.registrering,
	a.OrganisationfunktionAttrEgenskaberArr,
	a.OrganisationfunktionAttrUdvidelserArr,
	a.OrganisationfunktionTilsGyldighedArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: OrganisationfunktionRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) OrganisationfunktionRelationArr
	FROM
	(
			SELECT
			a.organisationfunktion_id,
			a.organisationfunktion_registrering_id,
			a.registrering,
			a.OrganisationfunktionAttrEgenskaberArr,
			a.OrganisationfunktionAttrUdvidelserArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.gyldighed
						) ::OrganisationfunktionGyldighedTilsType
					ELSE NULL
					END
					order by b.gyldighed,b.virkning
				)) OrganisationfunktionTilsGyldighedArr
			FROM
			(
					SELECT
					a.organisationfunktion_id,
					a.organisationfunktion_registrering_id,
					a.registrering,
					a.OrganisationfunktionAttrUdvidelserArr,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.funktionsnavn,
					   		b.virkning

							)::OrganisationfunktionEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.funktionsnavn,b.virkning

					)) OrganisationfunktionAttrEgenskaberArr

					FROM
					(
					SELECT
					a.organisationfunktion_id,
					a.organisationfunktion_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.primær,
					 		b.fraktion,
					 		b.udvidelse_1,
					 		b.udvidelse_2,
					 		b.udvidelse_3,
					 		b.udvidelse_4,
					 		b.udvidelse_5,
					 		b.udvidelse_6,
					 		b.udvidelse_7,
					 		b.udvidelse_8,
					 		b.udvidelse_9,
					 		b.udvidelse_10,
					   		b.virkning

							)::OrganisationfunktionUdvidelserAttrType
						ELSE
						NULL
						END

						order by b.primær,b.fraktion,b.udvidelse_1,b.udvidelse_2,b.udvidelse_3,b.udvidelse_4,b.udvidelse_5,b.udvidelse_6,b.udvidelse_7,b.udvidelse_8,b.udvidelse_9,b.udvidelse_10,b.virkning

					)) OrganisationfunktionAttrUdvidelserArr

					FROM
					(
					SELECT
					a.id organisationfunktion_id,
					b.id organisationfunktion_registrering_id,
					b.registrering
					FROM		organisationfunktion a
					JOIN 		organisationfunktion_registrering b 	ON b.organisationfunktion_id=a.id
					WHERE a.id = ANY (organisationfunktion_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN organisationfunktion_attr_udvidelser as b ON b.organisationfunktion_registrering_id=a.organisationfunktion_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.organisationfunktion_id,
					a.organisationfunktion_registrering_id,
					a.registrering
					) as a
					LEFT JOIN organisationfunktion_attr_egenskaber as b ON b.organisationfunktion_registrering_id=a.organisationfunktion_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.organisationfunktion_id,
					a.organisationfunktion_registrering_id,
					a.registrering,
					a.OrganisationfunktionAttrUdvidelserArr
			) as a
			LEFT JOIN organisationfunktion_tils_gyldighed as b ON b.organisationfunktion_registrering_id=a.organisationfunktion_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.organisationfunktion_id,
			a.organisationfunktion_registrering_id,
			a.registrering,
			a.OrganisationfunktionAttrUdvidelserArr,
			a.OrganisationfunktionAttrEgenskaberArr
	) as a
	LEFT JOIN organisationfunktion_relation b ON b.organisationfunktion_registrering_id=a.organisationfunktion_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.organisationfunktion_id,
	a.organisationfunktion_registrering_id,
	a.registrering,
	a.OrganisationfunktionAttrUdvidelserArr,
	a.OrganisationfunktionAttrEgenskaberArr,
	a.OrganisationfunktionTilsGyldighedArr
) as a

WHERE a.organisationfunktion_id IS NOT NULL
GROUP BY
a.organisationfunktion_id
order by a.organisationfunktion_id
) as x
;



RETURN result;

END;
$function$

;

-- as_list_organisation(uuid[],tstzrange,tstzrange,organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_list_organisation(
    organisation_uuids uuid[],
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::organisationregistreringtype[]
)
RETURNS organisationtype[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	auth_filtered_uuids uuid[];
	result OrganisationType[];
BEGIN


/*** Verify that the object meets the stipulated access allowed criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisation(organisation_uuids,auth_criteria_arr);
IF NOT (coalesce(array_length(auth_filtered_uuids,1),0)=coalesce(array_length(organisation_uuids,1),0) AND auth_filtered_uuids @>organisation_uuids) THEN
  RAISE EXCEPTION 'Unable to list organisation with uuids [%]. All objects do not fullfill the stipulated criteria:%',organisation_uuids,to_json(auth_criteria_arr)  USING ERRCODE = 'MO401';
END IF;
/*********************/

SELECT
array_agg(x.organisationObj) into result
FROM
(
SELECT
ROW(
	a.organisation_id,
	array_agg(
		ROW (
			a.registrering,
			a.OrganisationTilsGyldighedArr,
			a.OrganisationAttrEgenskaberArr,
			a.OrganisationRelationArr
		)::OrganisationRegistreringType
		order by upper((a.registrering).TimePeriod) DESC
	)
):: OrganisationType  organisationObj
FROM
(
	SELECT
	a.organisation_id,
	a.organisation_registrering_id,
	a.registrering,
	a.OrganisationAttrEgenskaberArr,
	a.OrganisationTilsGyldighedArr,
	_remove_nulls_in_array(array_agg(
		CASE
		WHEN b.id is not null THEN
		ROW (
				b.rel_type,
				b.virkning,
				b.rel_maal_uuid,
				b.rel_maal_urn,
				b.objekt_type
			):: OrganisationRelationType
		ELSE
		NULL
		END

		order by b.rel_maal_uuid,b.rel_maal_urn,b.rel_type,b.objekt_type,b.virkning

	)) OrganisationRelationArr
	FROM
	(
			SELECT
			a.organisation_id,
			a.organisation_registrering_id,
			a.registrering,
			a.OrganisationAttrEgenskaberArr,
			_remove_nulls_in_array(array_agg
				(
					CASE
					WHEN b.id is not null THEN
					ROW(
						b.virkning,
						b.gyldighed
						) ::OrganisationGyldighedTilsType
					ELSE NULL
					END
					order by b.gyldighed,b.virkning
				)) OrganisationTilsGyldighedArr
			FROM
			(
					SELECT
					a.organisation_id,
					a.organisation_registrering_id,
					a.registrering,
					_remove_nulls_in_array(array_agg(
						CASE

						WHEN b.id is not null THEN

						ROW(

					 		b.brugervendtnoegle,
					 		b.organisationsnavn,
					   		b.virkning

							)::OrganisationEgenskaberAttrType
						ELSE
						NULL
						END

						order by b.brugervendtnoegle,b.organisationsnavn,b.virkning

					)) OrganisationAttrEgenskaberArr

					FROM
					(
					SELECT
					a.id organisation_id,
					b.id organisation_registrering_id,
					b.registrering
					FROM		organisation a
					JOIN 		organisation_registrering b 	ON b.organisation_id=a.id
					WHERE a.id = ANY (organisation_uuids) AND ((registrering_tstzrange is null AND upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ) OR registrering_tstzrange && (b.registrering).timeperiod)--filter ON registrering_tstzrange
					) as a
					LEFT JOIN organisation_attr_egenskaber as b ON b.organisation_registrering_id=a.organisation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given

					GROUP BY
					a.organisation_id,
					a.organisation_registrering_id,
					a.registrering
			) as a
			LEFT JOIN organisation_tils_gyldighed as b ON b.organisation_registrering_id=a.organisation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
			GROUP BY
			a.organisation_id,
			a.organisation_registrering_id,
			a.registrering,
			a.OrganisationAttrEgenskaberArr
	) as a
	LEFT JOIN organisation_relation b ON b.organisation_registrering_id=a.organisation_registrering_id AND (virkning_tstzrange is null OR (b.virkning).TimePeriod && virkning_tstzrange) --filter ON virkning_tstzrange if given
	GROUP BY
	a.organisation_id,
	a.organisation_registrering_id,
	a.registrering,
	a.OrganisationAttrEgenskaberArr,
	a.OrganisationTilsGyldighedArr
) as a

WHERE a.organisation_id IS NOT NULL
GROUP BY
a.organisation_id
order by a.organisation_id
) as x
;



RETURN result;

END;
$function$

;

-- as_read_bruger(uuid,tstzrange,tstzrange,brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_bruger(
    bruger_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::brugerregistreringtype[]
)
RETURNS brugertype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr BrugerType[];
BEGIN
    resArr := as_list_bruger(ARRAY[bruger_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_facet(uuid,tstzrange,tstzrange,facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_facet(
    facet_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr facetregistreringtype[] DEFAULT NULL::facetregistreringtype[]
)
RETURNS facettype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr FacetType[];
BEGIN
    resArr := as_list_facet(ARRAY[facet_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_itsystem(uuid,tstzrange,tstzrange,itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_itsystem(
    itsystem_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::itsystemregistreringtype[]
)
RETURNS itsystemtype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr ItsystemType[];
BEGIN
    resArr := as_list_itsystem(ARRAY[itsystem_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_klasse(uuid,tstzrange,tstzrange,klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_klasse(
    klasse_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::klasseregistreringtype[]
)
RETURNS klassetype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr KlasseType[];
BEGIN
    resArr := as_list_klasse(ARRAY[klasse_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_klassifikation(uuid,tstzrange,tstzrange,klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_klassifikation(
    klassifikation_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::klassifikationregistreringtype[]
)
RETURNS klassifikationtype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr KlassifikationType[];
BEGIN
    resArr := as_list_klassifikation(ARRAY[klassifikation_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_organisationenhed(uuid,tstzrange,tstzrange,organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_organisationenhed(
    organisationenhed_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::organisationenhedregistreringtype[]
)
RETURNS organisationenhedtype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr OrganisationenhedType[];
BEGIN
    resArr := as_list_organisationenhed(ARRAY[organisationenhed_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_organisationfunktion(uuid,tstzrange,tstzrange,organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_organisationfunktion(
    organisationfunktion_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::organisationfunktionregistreringtype[]
)
RETURNS organisationfunktiontype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr OrganisationfunktionType[];
BEGIN
    resArr := as_list_organisationfunktion(ARRAY[organisationfunktion_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_read_organisation(uuid,tstzrange,tstzrange,organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_read_organisation(
    organisation_uuid uuid,
    registrering_tstzrange tstzrange,
    virkning_tstzrange tstzrange,
    auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::organisationregistreringtype[]
)
RETURNS organisationtype
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
	resArr OrganisationType[];
BEGIN
    resArr := as_list_organisation(ARRAY[organisation_uuid], registrering_tstzrange, virkning_tstzrange, auth_criteria_arr);
    IF resArr is not null and coalesce(array_length(resArr, 1), 0) = 1 THEN
	    RETURN resArr[1];
    ELSE
        RETURN null;
    END IF;
END;
$function$

;

-- as_search_bruger(integer,uuid,brugerregistreringtype,tstzrange,integer,text[],uuid[],text[],brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_bruger(
    firstresult integer,
    bruger_uuid uuid,
    registreringobj brugerregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::brugerregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    bruger_candidates uuid[];
    bruger_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj BrugerEgenskaberAttrType;
    attrUdvidelserTypeObj BrugerUdvidelserAttrType;


    tilsGyldighedTypeObj BrugerGyldighedTilsType;

    relationTypeObj BrugerRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

bruger_candidates_is_initialized := false;

IF bruger_uuid is not NULL THEN
    bruger_candidates:= ARRAY[bruger_uuid];
    bruger_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        bruger_candidates:=array(
                SELECT DISTINCT
                b.bruger_id
                FROM
                bruger a
                JOIN bruger_registrering b on b.bruger_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'bruger_candidates_is_initialized step 1:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 1:%',bruger_candidates;
--/****************************//


--RAISE NOTICE 'bruger_candidates_is_initialized step 2:%',bruger_candidates_is_initialized;
--RAISE NOTICE 'bruger_candidates step 2:%',bruger_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_bruger: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(bruger_candidates,1),0)>0 OR NOT bruger_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id
            FROM  bruger_attr_egenskaber a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.brugernavn IS NULL
                    OR
                    a.brugernavn ILIKE attrEgenskaberTypeObj.brugernavn --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.brugertype IS NULL
                    OR
                    a.brugertype ILIKE attrEgenskaberTypeObj.brugertype --case insensitive
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

            );


            bruger_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************************************************//
--Filtration on attribute: Udvidelser
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrUdvidelser IS NULL THEN
    --RAISE DEBUG 'as_search_bruger: skipping filtration on attrUdvidelser';
ELSE

    IF (coalesce(array_length(bruger_candidates,1),0)>0 OR NOT bruger_candidates_is_initialized) THEN

        FOREACH attrUdvidelserTypeObj IN ARRAY registreringObj.attrUdvidelser

        LOOP
            bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id
            FROM  bruger_attr_udvidelser a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id

            WHERE
                (
                    (
                        attrUdvidelserTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrUdvidelserTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrUdvidelserTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).AktoerRef IS NULL OR (attrUdvidelserTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).AktoerTypeKode IS NULL OR (attrUdvidelserTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrUdvidelserTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrUdvidelserTypeObj.virkning IS NULL OR (attrUdvidelserTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrUdvidelserTypeObj.fornavn IS NULL
                    OR
                    a.fornavn ILIKE attrUdvidelserTypeObj.fornavn --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.efternavn IS NULL
                    OR
                    a.efternavn ILIKE attrUdvidelserTypeObj.efternavn --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.kaldenavn_fornavn IS NULL
                    OR
                    a.kaldenavn_fornavn ILIKE attrUdvidelserTypeObj.kaldenavn_fornavn --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.kaldenavn_efternavn IS NULL
                    OR
                    a.kaldenavn_efternavn ILIKE attrUdvidelserTypeObj.kaldenavn_efternavn --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.seniority IS NULL
                    OR
                    a.seniority ILIKE attrUdvidelserTypeObj.seniority --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

            );


            bruger_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'bruger_candidates_is_initialized step 3:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 3:%',bruger_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        bruger_candidates:=array(

            SELECT DISTINCT
            b.bruger_id

            FROM  bruger_attr_egenskaber a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.brugernavn ILIKE anyAttrValue OR
                        a.brugertype ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

            UNION

            SELECT DISTINCT
            b.bruger_id

            FROM  bruger_attr_udvidelser a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id

            WHERE
            (
                        a.fornavn ILIKE anyAttrValue OR
                        a.efternavn ILIKE anyAttrValue OR
                        a.kaldenavn_fornavn ILIKE anyAttrValue OR
                        a.kaldenavn_efternavn ILIKE anyAttrValue OR
                        a.seniority ILIKE anyAttrValue

            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )


        );

    bruger_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
    --RAISE DEBUG 'as_search_bruger: skipping filtration on tilsGyldighed';
ELSE
    IF (coalesce(array_length(bruger_candidates,1),0)>0 OR bruger_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
        LOOP
            bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id
            FROM  bruger_tils_gyldighed a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id
            WHERE
                (
                    tilsGyldighedTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsGyldighedTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerRef IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsGyldighedTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsGyldighedTypeObj.virkning) IS NULL OR (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsGyldighedTypeObj.gyldighed IS NULL
                    OR
                    tilsGyldighedTypeObj.gyldighed = a.gyldighed
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

    );


            bruger_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer BrugerRelationType[]
*/


--RAISE DEBUG 'bruger_candidates_is_initialized step 4:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 4:%',bruger_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_bruger: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(bruger_candidates,1),0)>0 OR NOT bruger_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id
            FROM  bruger_relation a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

    );

            bruger_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id

            FROM  bruger_relation a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )


            );

    bruger_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        bruger_candidates:=array(
            SELECT DISTINCT
            b.bruger_id

            FROM  bruger_relation a
            JOIN bruger_registrering b on a.bruger_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )


            );

    bruger_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'bruger_candidates_is_initialized step 5:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 5:%',bruger_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT bruger_candidates_is_initialized THEN
        bruger_candidates:=array(
        SELECT DISTINCT
            bruger_id
        FROM
            bruger_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT bruger_candidates_is_initialized) OR b.bruger_id = ANY (bruger_candidates) )

        )
        ;

        bruger_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT bruger_candidates_is_initialized THEN
    --No filters applied!
    bruger_candidates:=array(
        SELECT DISTINCT id FROM bruger a
    );
ELSE
    bruger_candidates:=array(
        SELECT DISTINCT id FROM unnest(bruger_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'bruger_candidates_is_initialized step 6:%',bruger_candidates_is_initialized;
--RAISE DEBUG 'bruger_candidates step 6:%',bruger_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_bruger(bruger_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_bruger(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_facet(integer,uuid,facetregistreringtype,tstzrange,integer,text[],uuid[],text[],facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_facet(
    firstresult integer,
    facet_uuid uuid,
    registreringobj facetregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr facetregistreringtype[] DEFAULT NULL::facetregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    facet_candidates uuid[];
    facet_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj FacetEgenskaberAttrType;


    tilsPubliceretTypeObj FacetPubliceretTilsType;

    relationTypeObj FacetRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

facet_candidates_is_initialized := false;

IF facet_uuid is not NULL THEN
    facet_candidates:= ARRAY[facet_uuid];
    facet_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        facet_candidates:=array(
                SELECT DISTINCT
                b.facet_id
                FROM
                facet a
                JOIN facet_registrering b on b.facet_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'facet_candidates_is_initialized step 1:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 1:%',facet_candidates;
--/****************************//


--RAISE NOTICE 'facet_candidates_is_initialized step 2:%',facet_candidates_is_initialized;
--RAISE NOTICE 'facet_candidates step 2:%',facet_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_facet: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(facet_candidates,1),0)>0 OR NOT facet_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            facet_candidates:=array(
            SELECT DISTINCT
            b.facet_id
            FROM  facet_attr_egenskaber a
            JOIN facet_registrering b on a.facet_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.beskrivelse IS NULL
                    OR
                    a.beskrivelse ILIKE attrEgenskaberTypeObj.beskrivelse --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.opbygning IS NULL
                    OR
                    a.opbygning ILIKE attrEgenskaberTypeObj.opbygning --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.ophavsret IS NULL
                    OR
                    a.ophavsret ILIKE attrEgenskaberTypeObj.ophavsret --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.plan IS NULL
                    OR
                    a.plan ILIKE attrEgenskaberTypeObj.plan --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.supplement IS NULL
                    OR
                    a.supplement ILIKE attrEgenskaberTypeObj.supplement --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.retskilde IS NULL
                    OR
                    a.retskilde ILIKE attrEgenskaberTypeObj.retskilde --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )

            );


            facet_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'facet_candidates_is_initialized step 3:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 3:%',facet_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        facet_candidates:=array(

            SELECT DISTINCT
            b.facet_id

            FROM  facet_attr_egenskaber a
            JOIN facet_registrering b on a.facet_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.beskrivelse ILIKE anyAttrValue OR
                        a.opbygning ILIKE anyAttrValue OR
                        a.ophavsret ILIKE anyAttrValue OR
                        a.plan ILIKE anyAttrValue OR
                        a.supplement ILIKE anyAttrValue OR
                        a.retskilde ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )


        );

    facet_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
    --RAISE DEBUG 'as_search_facet: skipping filtration on tilsPubliceret';
ELSE
    IF (coalesce(array_length(facet_candidates,1),0)>0 OR facet_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
        LOOP
            facet_candidates:=array(
            SELECT DISTINCT
            b.facet_id
            FROM  facet_tils_publiceret a
            JOIN facet_registrering b on a.facet_registrering_id=b.id
            WHERE
                (
                    tilsPubliceretTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsPubliceretTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerRef IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsPubliceretTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsPubliceretTypeObj.virkning) IS NULL OR (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsPubliceretTypeObj.publiceret IS NULL
                    OR
                    tilsPubliceretTypeObj.publiceret = a.publiceret
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )

    );


            facet_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer FacetRelationType[]
*/


--RAISE DEBUG 'facet_candidates_is_initialized step 4:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 4:%',facet_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_facet: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(facet_candidates,1),0)>0 OR NOT facet_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            facet_candidates:=array(
            SELECT DISTINCT
            b.facet_id
            FROM  facet_relation a
            JOIN facet_registrering b on a.facet_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )

    );

            facet_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        facet_candidates:=array(
            SELECT DISTINCT
            b.facet_id

            FROM  facet_relation a
            JOIN facet_registrering b on a.facet_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )


            );

    facet_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        facet_candidates:=array(
            SELECT DISTINCT
            b.facet_id

            FROM  facet_relation a
            JOIN facet_registrering b on a.facet_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )


            );

    facet_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'facet_candidates_is_initialized step 5:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 5:%',facet_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT facet_candidates_is_initialized THEN
        facet_candidates:=array(
        SELECT DISTINCT
            facet_id
        FROM
            facet_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT facet_candidates_is_initialized) OR b.facet_id = ANY (facet_candidates) )

        )
        ;

        facet_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT facet_candidates_is_initialized THEN
    --No filters applied!
    facet_candidates:=array(
        SELECT DISTINCT id FROM facet a
    );
ELSE
    facet_candidates:=array(
        SELECT DISTINCT id FROM unnest(facet_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'facet_candidates_is_initialized step 6:%',facet_candidates_is_initialized;
--RAISE DEBUG 'facet_candidates step 6:%',facet_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_facet(facet_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_facet(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_itsystem(integer,uuid,itsystemregistreringtype,tstzrange,integer,text[],uuid[],text[],itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_itsystem(
    firstresult integer,
    itsystem_uuid uuid,
    registreringobj itsystemregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::itsystemregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    itsystem_candidates uuid[];
    itsystem_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj ItsystemEgenskaberAttrType;


    tilsGyldighedTypeObj ItsystemGyldighedTilsType;

    relationTypeObj ItsystemRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

itsystem_candidates_is_initialized := false;

IF itsystem_uuid is not NULL THEN
    itsystem_candidates:= ARRAY[itsystem_uuid];
    itsystem_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        itsystem_candidates:=array(
                SELECT DISTINCT
                b.itsystem_id
                FROM
                itsystem a
                JOIN itsystem_registrering b on b.itsystem_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'itsystem_candidates_is_initialized step 1:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 1:%',itsystem_candidates;
--/****************************//


--RAISE NOTICE 'itsystem_candidates_is_initialized step 2:%',itsystem_candidates_is_initialized;
--RAISE NOTICE 'itsystem_candidates step 2:%',itsystem_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_itsystem: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(itsystem_candidates,1),0)>0 OR NOT itsystem_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            itsystem_candidates:=array(
            SELECT DISTINCT
            b.itsystem_id
            FROM  itsystem_attr_egenskaber a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.itsystemnavn IS NULL
                    OR
                    a.itsystemnavn ILIKE attrEgenskaberTypeObj.itsystemnavn --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.itsystemtype IS NULL
                    OR
                    a.itsystemtype ILIKE attrEgenskaberTypeObj.itsystemtype --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.konfigurationreference IS NULL
                    OR
                    _as_search_match_array(attrEgenskaberTypeObj.konfigurationreference,a.konfigurationreference)
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )

            );


            itsystem_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'itsystem_candidates_is_initialized step 3:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 3:%',itsystem_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        itsystem_candidates:=array(

            SELECT DISTINCT
            b.itsystem_id

            FROM  itsystem_attr_egenskaber a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.itsystemnavn ILIKE anyAttrValue OR
                        a.itsystemtype ILIKE anyAttrValue OR
                        _as_search_ilike_array(anyAttrValue,a.konfigurationreference)
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )


        );

    itsystem_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
    --RAISE DEBUG 'as_search_itsystem: skipping filtration on tilsGyldighed';
ELSE
    IF (coalesce(array_length(itsystem_candidates,1),0)>0 OR itsystem_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
        LOOP
            itsystem_candidates:=array(
            SELECT DISTINCT
            b.itsystem_id
            FROM  itsystem_tils_gyldighed a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id
            WHERE
                (
                    tilsGyldighedTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsGyldighedTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerRef IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsGyldighedTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsGyldighedTypeObj.virkning) IS NULL OR (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsGyldighedTypeObj.gyldighed IS NULL
                    OR
                    tilsGyldighedTypeObj.gyldighed = a.gyldighed
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )

    );


            itsystem_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer ItsystemRelationType[]
*/


--RAISE DEBUG 'itsystem_candidates_is_initialized step 4:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 4:%',itsystem_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_itsystem: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(itsystem_candidates,1),0)>0 OR NOT itsystem_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            itsystem_candidates:=array(
            SELECT DISTINCT
            b.itsystem_id
            FROM  itsystem_relation a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )

    );

            itsystem_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        itsystem_candidates:=array(
            SELECT DISTINCT
            b.itsystem_id

            FROM  itsystem_relation a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )


            );

    itsystem_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        itsystem_candidates:=array(
            SELECT DISTINCT
            b.itsystem_id

            FROM  itsystem_relation a
            JOIN itsystem_registrering b on a.itsystem_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )


            );

    itsystem_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'itsystem_candidates_is_initialized step 5:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 5:%',itsystem_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT itsystem_candidates_is_initialized THEN
        itsystem_candidates:=array(
        SELECT DISTINCT
            itsystem_id
        FROM
            itsystem_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT itsystem_candidates_is_initialized) OR b.itsystem_id = ANY (itsystem_candidates) )

        )
        ;

        itsystem_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT itsystem_candidates_is_initialized THEN
    --No filters applied!
    itsystem_candidates:=array(
        SELECT DISTINCT id FROM itsystem a
    );
ELSE
    itsystem_candidates:=array(
        SELECT DISTINCT id FROM unnest(itsystem_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'itsystem_candidates_is_initialized step 6:%',itsystem_candidates_is_initialized;
--RAISE DEBUG 'itsystem_candidates step 6:%',itsystem_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_itsystem(itsystem_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_itsystem(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_klasse(integer,uuid,klasseregistreringtype,tstzrange,integer,text[],uuid[],text[],klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_klasse(
    firstresult integer,
    klasse_uuid uuid,
    registreringobj klasseregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::klasseregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    klasse_candidates uuid[];
    klasse_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj KlasseEgenskaberAttrType;


    tilsPubliceretTypeObj KlassePubliceretTilsType;

    relationTypeObj KlasseRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


    manipulatedAttrEgenskaberArr KlasseEgenskaberAttrType[]:='{}';
    soegeordObj KlasseSoegeordType;

BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

klasse_candidates_is_initialized := false;

IF klasse_uuid is not NULL THEN
    klasse_candidates:= ARRAY[klasse_uuid];
    klasse_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        klasse_candidates:=array(
                SELECT DISTINCT
                b.klasse_id
                FROM
                klasse a
                JOIN klasse_registrering b on b.klasse_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'klasse_candidates_is_initialized step 1:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 1:%',klasse_candidates;
--/****************************//


--RAISE NOTICE 'klasse_candidates_is_initialized step 2:%',klasse_candidates_is_initialized;
--RAISE NOTICE 'klasse_candidates step 2:%',klasse_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_klasse: skipping filtration on attrEgenskaber';
ELSE


--To help facilitate the comparrison efforts (while diverging at a minimum form the templated db-kode,
--we'll manipulate the attrEgenskaber array so to make sure that every object only has 1 sogeord element - duplicating the parent elements in attrEgenskaber as needed  )

FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber
LOOP
       IF  (attrEgenskaberTypeObj).soegeord IS NULL OR coalesce(array_length((attrEgenskaberTypeObj).soegeord,1),0)<2 THEN
       manipulatedAttrEgenskaberArr:=array_append(manipulatedAttrEgenskaberArr,attrEgenskaberTypeObj); --The element only has 0 or 1 soegeord element, så no manipulations is needed.
       ELSE
               FOREACH soegeordObj IN ARRAY (attrEgenskaberTypeObj).soegeord
               LOOP
                       manipulatedAttrEgenskaberArr:=array_append(manipulatedAttrEgenskaberArr,
                               ROW (
                                       attrEgenskaberTypeObj.brugervendtnoegle,
                                       attrEgenskaberTypeObj.beskrivelse,
                                       attrEgenskaberTypeObj.eksempel,
                                       attrEgenskaberTypeObj.omfang,
                                       attrEgenskaberTypeObj.titel,
                                       attrEgenskaberTypeObj.retskilde,
                                       attrEgenskaberTypeObj.aendringsnotat,
                                       ARRAY[soegeordObj]::KlasseSoegeordType[], --NOTICE: Only 1 element in array
                                       attrEgenskaberTypeObj.virkning
                                       )::KlasseEgenskaberAttrType
                               );
               END LOOP;
       END IF;
END LOOP;

    IF (coalesce(array_length(klasse_candidates,1),0)>0 OR NOT klasse_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY manipulatedAttrEgenskaberArr

        LOOP
            klasse_candidates:=array(
            SELECT DISTINCT
            b.klasse_id
            FROM  klasse_attr_egenskaber a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id

            LEFT JOIN klasse_attr_egenskaber_soegeord c on a.id=c.klasse_attr_egenskaber_id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.beskrivelse IS NULL
                    OR
                    a.beskrivelse ILIKE attrEgenskaberTypeObj.beskrivelse --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.eksempel IS NULL
                    OR
                    a.eksempel ILIKE attrEgenskaberTypeObj.eksempel --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.omfang IS NULL
                    OR
                    a.omfang ILIKE attrEgenskaberTypeObj.omfang --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.titel IS NULL
                    OR
                    a.titel ILIKE attrEgenskaberTypeObj.titel --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.retskilde IS NULL
                    OR
                    a.retskilde ILIKE attrEgenskaberTypeObj.retskilde --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.aendringsnotat IS NULL
                    OR
                    a.aendringsnotat ILIKE attrEgenskaberTypeObj.aendringsnotat --case insensitive
                )
                AND

                (
                        (attrEgenskaberTypeObj.soegeord IS NULL OR array_length(attrEgenskaberTypeObj.soegeord,1)=0)
                        OR
                        (
                                (
                                        (attrEgenskaberTypeObj.soegeord[1]).soegeordidentifikator IS NULL
                                        OR
                                        c.soegeordidentifikator ILIKE (attrEgenskaberTypeObj.soegeord[1]).soegeordidentifikator
                                )
                                AND
                                (
                                        (attrEgenskaberTypeObj.soegeord[1]).beskrivelse IS NULL
                                        OR
                                        c.beskrivelse ILIKE (attrEgenskaberTypeObj.soegeord[1]).beskrivelse
                                )
                                AND
                                (
                                        (attrEgenskaberTypeObj.soegeord[1]).soegeordskategori IS NULL
                                        OR
                                        c.soegeordskategori ILIKE (attrEgenskaberTypeObj.soegeord[1]).soegeordskategori
                                )
                        )
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )

            );


            klasse_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'klasse_candidates_is_initialized step 3:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 3:%',klasse_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        klasse_candidates:=array(

            SELECT DISTINCT
            b.klasse_id

            FROM  klasse_attr_egenskaber a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id

            LEFT JOIN klasse_attr_egenskaber_soegeord c on a.id=c.klasse_attr_egenskaber_id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.beskrivelse ILIKE anyAttrValue OR
                        a.eksempel ILIKE anyAttrValue OR
                        a.omfang ILIKE anyAttrValue OR
                        a.titel ILIKE anyAttrValue OR
                        a.retskilde ILIKE anyAttrValue OR
                        a.aendringsnotat ILIKE anyAttrValue
                OR
                c.soegeordidentifikator ILIKE anyAttrValue
                OR
                c.beskrivelse ILIKE anyAttrValue
                OR
                c.soegeordskategori ILIKE anyAttrValue

            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )


        );

    klasse_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
    --RAISE DEBUG 'as_search_klasse: skipping filtration on tilsPubliceret';
ELSE
    IF (coalesce(array_length(klasse_candidates,1),0)>0 OR klasse_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
        LOOP
            klasse_candidates:=array(
            SELECT DISTINCT
            b.klasse_id
            FROM  klasse_tils_publiceret a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id
            WHERE
                (
                    tilsPubliceretTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsPubliceretTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerRef IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsPubliceretTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsPubliceretTypeObj.virkning) IS NULL OR (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsPubliceretTypeObj.publiceret IS NULL
                    OR
                    tilsPubliceretTypeObj.publiceret = a.publiceret
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )

    );


            klasse_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer KlasseRelationType[]
*/


--RAISE DEBUG 'klasse_candidates_is_initialized step 4:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 4:%',klasse_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_klasse: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(klasse_candidates,1),0)>0 OR NOT klasse_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            klasse_candidates:=array(
            SELECT DISTINCT
            b.klasse_id
            FROM  klasse_relation a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )

    );

            klasse_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        klasse_candidates:=array(
            SELECT DISTINCT
            b.klasse_id

            FROM  klasse_relation a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )


            );

    klasse_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        klasse_candidates:=array(
            SELECT DISTINCT
            b.klasse_id

            FROM  klasse_relation a
            JOIN klasse_registrering b on a.klasse_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )


            );

    klasse_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'klasse_candidates_is_initialized step 5:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 5:%',klasse_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT klasse_candidates_is_initialized THEN
        klasse_candidates:=array(
        SELECT DISTINCT
            klasse_id
        FROM
            klasse_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klasse_candidates_is_initialized) OR b.klasse_id = ANY (klasse_candidates) )

        )
        ;

        klasse_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT klasse_candidates_is_initialized THEN
    --No filters applied!
    klasse_candidates:=array(
        SELECT DISTINCT id FROM klasse a
    );
ELSE
    klasse_candidates:=array(
        SELECT DISTINCT id FROM unnest(klasse_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'klasse_candidates_is_initialized step 6:%',klasse_candidates_is_initialized;
--RAISE DEBUG 'klasse_candidates step 6:%',klasse_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_klasse(klasse_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_klasse(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_klassifikation(integer,uuid,klassifikationregistreringtype,tstzrange,integer,text[],uuid[],text[],klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_klassifikation(
    firstresult integer,
    klassifikation_uuid uuid,
    registreringobj klassifikationregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::klassifikationregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    klassifikation_candidates uuid[];
    klassifikation_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj KlassifikationEgenskaberAttrType;


    tilsPubliceretTypeObj KlassifikationPubliceretTilsType;

    relationTypeObj KlassifikationRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

klassifikation_candidates_is_initialized := false;

IF klassifikation_uuid is not NULL THEN
    klassifikation_candidates:= ARRAY[klassifikation_uuid];
    klassifikation_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        klassifikation_candidates:=array(
                SELECT DISTINCT
                b.klassifikation_id
                FROM
                klassifikation a
                JOIN klassifikation_registrering b on b.klassifikation_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'klassifikation_candidates_is_initialized step 1:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 1:%',klassifikation_candidates;
--/****************************//


--RAISE NOTICE 'klassifikation_candidates_is_initialized step 2:%',klassifikation_candidates_is_initialized;
--RAISE NOTICE 'klassifikation_candidates step 2:%',klassifikation_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_klassifikation: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(klassifikation_candidates,1),0)>0 OR NOT klassifikation_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            klassifikation_candidates:=array(
            SELECT DISTINCT
            b.klassifikation_id
            FROM  klassifikation_attr_egenskaber a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.beskrivelse IS NULL
                    OR
                    a.beskrivelse ILIKE attrEgenskaberTypeObj.beskrivelse --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.kaldenavn IS NULL
                    OR
                    a.kaldenavn ILIKE attrEgenskaberTypeObj.kaldenavn --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.ophavsret IS NULL
                    OR
                    a.ophavsret ILIKE attrEgenskaberTypeObj.ophavsret --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )

            );


            klassifikation_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'klassifikation_candidates_is_initialized step 3:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 3:%',klassifikation_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        klassifikation_candidates:=array(

            SELECT DISTINCT
            b.klassifikation_id

            FROM  klassifikation_attr_egenskaber a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.beskrivelse ILIKE anyAttrValue OR
                        a.kaldenavn ILIKE anyAttrValue OR
                        a.ophavsret ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )


        );

    klassifikation_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Publiceret
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsPubliceret IS NULL THEN
    --RAISE DEBUG 'as_search_klassifikation: skipping filtration on tilsPubliceret';
ELSE
    IF (coalesce(array_length(klassifikation_candidates,1),0)>0 OR klassifikation_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsPubliceretTypeObj IN ARRAY registreringObj.tilsPubliceret
        LOOP
            klassifikation_candidates:=array(
            SELECT DISTINCT
            b.klassifikation_id
            FROM  klassifikation_tils_publiceret a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id
            WHERE
                (
                    tilsPubliceretTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsPubliceretTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerRef IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsPubliceretTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsPubliceretTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsPubliceretTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsPubliceretTypeObj.virkning) IS NULL OR (tilsPubliceretTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsPubliceretTypeObj.publiceret IS NULL
                    OR
                    tilsPubliceretTypeObj.publiceret = a.publiceret
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )

    );


            klassifikation_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer KlassifikationRelationType[]
*/


--RAISE DEBUG 'klassifikation_candidates_is_initialized step 4:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 4:%',klassifikation_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_klassifikation: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(klassifikation_candidates,1),0)>0 OR NOT klassifikation_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            klassifikation_candidates:=array(
            SELECT DISTINCT
            b.klassifikation_id
            FROM  klassifikation_relation a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )

    );

            klassifikation_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        klassifikation_candidates:=array(
            SELECT DISTINCT
            b.klassifikation_id

            FROM  klassifikation_relation a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )


            );

    klassifikation_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        klassifikation_candidates:=array(
            SELECT DISTINCT
            b.klassifikation_id

            FROM  klassifikation_relation a
            JOIN klassifikation_registrering b on a.klassifikation_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )


            );

    klassifikation_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'klassifikation_candidates_is_initialized step 5:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 5:%',klassifikation_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT klassifikation_candidates_is_initialized THEN
        klassifikation_candidates:=array(
        SELECT DISTINCT
            klassifikation_id
        FROM
            klassifikation_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT klassifikation_candidates_is_initialized) OR b.klassifikation_id = ANY (klassifikation_candidates) )

        )
        ;

        klassifikation_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT klassifikation_candidates_is_initialized THEN
    --No filters applied!
    klassifikation_candidates:=array(
        SELECT DISTINCT id FROM klassifikation a
    );
ELSE
    klassifikation_candidates:=array(
        SELECT DISTINCT id FROM unnest(klassifikation_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'klassifikation_candidates_is_initialized step 6:%',klassifikation_candidates_is_initialized;
--RAISE DEBUG 'klassifikation_candidates step 6:%',klassifikation_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_klassifikation(klassifikation_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_klassifikation(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_organisationenhed(integer,uuid,organisationenhedregistreringtype,tstzrange,integer,text[],uuid[],text[],organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_organisationenhed(
    firstresult integer,
    organisationenhed_uuid uuid,
    registreringobj organisationenhedregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::organisationenhedregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    organisationenhed_candidates uuid[];
    organisationenhed_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj OrganisationenhedEgenskaberAttrType;


    tilsGyldighedTypeObj OrganisationenhedGyldighedTilsType;

    relationTypeObj OrganisationenhedRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

organisationenhed_candidates_is_initialized := false;

IF organisationenhed_uuid is not NULL THEN
    organisationenhed_candidates:= ARRAY[organisationenhed_uuid];
    organisationenhed_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        organisationenhed_candidates:=array(
                SELECT DISTINCT
                b.organisationenhed_id
                FROM
                organisationenhed a
                JOIN organisationenhed_registrering b on b.organisationenhed_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 1:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 1:%',organisationenhed_candidates;
--/****************************//


--RAISE NOTICE 'organisationenhed_candidates_is_initialized step 2:%',organisationenhed_candidates_is_initialized;
--RAISE NOTICE 'organisationenhed_candidates step 2:%',organisationenhed_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_organisationenhed: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(organisationenhed_candidates,1),0)>0 OR NOT organisationenhed_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            organisationenhed_candidates:=array(
            SELECT DISTINCT
            b.organisationenhed_id
            FROM  organisationenhed_attr_egenskaber a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.enhedsnavn IS NULL
                    OR
                    a.enhedsnavn ILIKE attrEgenskaberTypeObj.enhedsnavn --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )

            );


            organisationenhed_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 3:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 3:%',organisationenhed_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        organisationenhed_candidates:=array(

            SELECT DISTINCT
            b.organisationenhed_id

            FROM  organisationenhed_attr_egenskaber a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.enhedsnavn ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )


        );

    organisationenhed_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
    --RAISE DEBUG 'as_search_organisationenhed: skipping filtration on tilsGyldighed';
ELSE
    IF (coalesce(array_length(organisationenhed_candidates,1),0)>0 OR organisationenhed_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
        LOOP
            organisationenhed_candidates:=array(
            SELECT DISTINCT
            b.organisationenhed_id
            FROM  organisationenhed_tils_gyldighed a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id
            WHERE
                (
                    tilsGyldighedTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsGyldighedTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerRef IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsGyldighedTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsGyldighedTypeObj.virkning) IS NULL OR (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsGyldighedTypeObj.gyldighed IS NULL
                    OR
                    tilsGyldighedTypeObj.gyldighed = a.gyldighed
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )

    );


            organisationenhed_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer OrganisationenhedRelationType[]
*/


--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 4:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 4:%',organisationenhed_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_organisationenhed: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(organisationenhed_candidates,1),0)>0 OR NOT organisationenhed_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            organisationenhed_candidates:=array(
            SELECT DISTINCT
            b.organisationenhed_id
            FROM  organisationenhed_relation a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )

    );

            organisationenhed_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        organisationenhed_candidates:=array(
            SELECT DISTINCT
            b.organisationenhed_id

            FROM  organisationenhed_relation a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )


            );

    organisationenhed_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        organisationenhed_candidates:=array(
            SELECT DISTINCT
            b.organisationenhed_id

            FROM  organisationenhed_relation a
            JOIN organisationenhed_registrering b on a.organisationenhed_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )


            );

    organisationenhed_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 5:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 5:%',organisationenhed_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT organisationenhed_candidates_is_initialized THEN
        organisationenhed_candidates:=array(
        SELECT DISTINCT
            organisationenhed_id
        FROM
            organisationenhed_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationenhed_candidates_is_initialized) OR b.organisationenhed_id = ANY (organisationenhed_candidates) )

        )
        ;

        organisationenhed_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT organisationenhed_candidates_is_initialized THEN
    --No filters applied!
    organisationenhed_candidates:=array(
        SELECT DISTINCT id FROM organisationenhed a
    );
ELSE
    organisationenhed_candidates:=array(
        SELECT DISTINCT id FROM unnest(organisationenhed_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'organisationenhed_candidates_is_initialized step 6:%',organisationenhed_candidates_is_initialized;
--RAISE DEBUG 'organisationenhed_candidates step 6:%',organisationenhed_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationenhed(organisationenhed_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_organisationenhed(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_organisationfunktion(integer,uuid,organisationfunktionregistreringtype,tstzrange,integer,text[],uuid[],text[],organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_organisationfunktion(
    firstresult integer,
    organisationfunktion_uuid uuid,
    registreringobj organisationfunktionregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::organisationfunktionregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    organisationfunktion_candidates uuid[];
    organisationfunktion_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj OrganisationfunktionEgenskaberAttrType;
    attrUdvidelserTypeObj OrganisationfunktionUdvidelserAttrType;


    tilsGyldighedTypeObj OrganisationfunktionGyldighedTilsType;

    relationTypeObj OrganisationfunktionRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

organisationfunktion_candidates_is_initialized := false;

IF organisationfunktion_uuid is not NULL THEN
    organisationfunktion_candidates:= ARRAY[organisationfunktion_uuid];
    organisationfunktion_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        organisationfunktion_candidates:=array(
                SELECT DISTINCT
                b.organisationfunktion_id
                FROM
                organisationfunktion a
                JOIN organisationfunktion_registrering b on b.organisationfunktion_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 1:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 1:%',organisationfunktion_candidates;
--/****************************//


--RAISE NOTICE 'organisationfunktion_candidates_is_initialized step 2:%',organisationfunktion_candidates_is_initialized;
--RAISE NOTICE 'organisationfunktion_candidates step 2:%',organisationfunktion_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(organisationfunktion_candidates,1),0)>0 OR NOT organisationfunktion_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id
            FROM  organisationfunktion_attr_egenskaber a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.funktionsnavn IS NULL
                    OR
                    a.funktionsnavn ILIKE attrEgenskaberTypeObj.funktionsnavn --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

            );


            organisationfunktion_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************************************************//
--Filtration on attribute: Udvidelser
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrUdvidelser IS NULL THEN
    --RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on attrUdvidelser';
ELSE

    IF (coalesce(array_length(organisationfunktion_candidates,1),0)>0 OR NOT organisationfunktion_candidates_is_initialized) THEN

        FOREACH attrUdvidelserTypeObj IN ARRAY registreringObj.attrUdvidelser

        LOOP
            organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id
            FROM  organisationfunktion_attr_udvidelser a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id

            WHERE
                (
                    (
                        attrUdvidelserTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrUdvidelserTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrUdvidelserTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).AktoerRef IS NULL OR (attrUdvidelserTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).AktoerTypeKode IS NULL OR (attrUdvidelserTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrUdvidelserTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrUdvidelserTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrUdvidelserTypeObj.virkning IS NULL OR (attrUdvidelserTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrUdvidelserTypeObj.primær IS NULL
                    OR
                    a.primær = attrUdvidelserTypeObj.primær
                )
                AND
                (
                    attrUdvidelserTypeObj.fraktion IS NULL
                    OR
                    a.fraktion = attrUdvidelserTypeObj.fraktion
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_1 IS NULL
                    OR
                    a.udvidelse_1 ILIKE attrUdvidelserTypeObj.udvidelse_1 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_2 IS NULL
                    OR
                    a.udvidelse_2 ILIKE attrUdvidelserTypeObj.udvidelse_2 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_3 IS NULL
                    OR
                    a.udvidelse_3 ILIKE attrUdvidelserTypeObj.udvidelse_3 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_4 IS NULL
                    OR
                    a.udvidelse_4 ILIKE attrUdvidelserTypeObj.udvidelse_4 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_5 IS NULL
                    OR
                    a.udvidelse_5 ILIKE attrUdvidelserTypeObj.udvidelse_5 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_6 IS NULL
                    OR
                    a.udvidelse_6 ILIKE attrUdvidelserTypeObj.udvidelse_6 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_7 IS NULL
                    OR
                    a.udvidelse_7 ILIKE attrUdvidelserTypeObj.udvidelse_7 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_8 IS NULL
                    OR
                    a.udvidelse_8 ILIKE attrUdvidelserTypeObj.udvidelse_8 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_9 IS NULL
                    OR
                    a.udvidelse_9 ILIKE attrUdvidelserTypeObj.udvidelse_9 --case insensitive
                )
                AND
                (
                    attrUdvidelserTypeObj.udvidelse_10 IS NULL
                    OR
                    a.udvidelse_10 ILIKE attrUdvidelserTypeObj.udvidelse_10 --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

            );


            organisationfunktion_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 3:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 3:%',organisationfunktion_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        organisationfunktion_candidates:=array(

            SELECT DISTINCT
            b.organisationfunktion_id

            FROM  organisationfunktion_attr_egenskaber a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.funktionsnavn ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

            UNION

            SELECT DISTINCT
            b.organisationfunktion_id

            FROM  organisationfunktion_attr_udvidelser a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id

            WHERE
            (
                                -- boolean is skipped intentionally

                                    a.fraktion::text ilike anyAttrValue OR
                        a.udvidelse_1 ILIKE anyAttrValue OR
                        a.udvidelse_2 ILIKE anyAttrValue OR
                        a.udvidelse_3 ILIKE anyAttrValue OR
                        a.udvidelse_4 ILIKE anyAttrValue OR
                        a.udvidelse_5 ILIKE anyAttrValue OR
                        a.udvidelse_6 ILIKE anyAttrValue OR
                        a.udvidelse_7 ILIKE anyAttrValue OR
                        a.udvidelse_8 ILIKE anyAttrValue OR
                        a.udvidelse_9 ILIKE anyAttrValue OR
                        a.udvidelse_10 ILIKE anyAttrValue

            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )


        );

    organisationfunktion_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
    --RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on tilsGyldighed';
ELSE
    IF (coalesce(array_length(organisationfunktion_candidates,1),0)>0 OR organisationfunktion_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
        LOOP
            organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id
            FROM  organisationfunktion_tils_gyldighed a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id
            WHERE
                (
                    tilsGyldighedTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsGyldighedTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerRef IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsGyldighedTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsGyldighedTypeObj.virkning) IS NULL OR (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsGyldighedTypeObj.gyldighed IS NULL
                    OR
                    tilsGyldighedTypeObj.gyldighed = a.gyldighed
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

    );


            organisationfunktion_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer OrganisationfunktionRelationType[]
*/


--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 4:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 4:%',organisationfunktion_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_organisationfunktion: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(organisationfunktion_candidates,1),0)>0 OR NOT organisationfunktion_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id
            FROM  organisationfunktion_relation a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

    );

            organisationfunktion_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id

            FROM  organisationfunktion_relation a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )


            );

    organisationfunktion_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        organisationfunktion_candidates:=array(
            SELECT DISTINCT
            b.organisationfunktion_id

            FROM  organisationfunktion_relation a
            JOIN organisationfunktion_registrering b on a.organisationfunktion_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )


            );

    organisationfunktion_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 5:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 5:%',organisationfunktion_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT organisationfunktion_candidates_is_initialized THEN
        organisationfunktion_candidates:=array(
        SELECT DISTINCT
            organisationfunktion_id
        FROM
            organisationfunktion_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisationfunktion_candidates_is_initialized) OR b.organisationfunktion_id = ANY (organisationfunktion_candidates) )

        )
        ;

        organisationfunktion_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT organisationfunktion_candidates_is_initialized THEN
    --No filters applied!
    organisationfunktion_candidates:=array(
        SELECT DISTINCT id FROM organisationfunktion a
    );
ELSE
    organisationfunktion_candidates:=array(
        SELECT DISTINCT id FROM unnest(organisationfunktion_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'organisationfunktion_candidates_is_initialized step 6:%',organisationfunktion_candidates_is_initialized;
--RAISE DEBUG 'organisationfunktion_candidates step 6:%',organisationfunktion_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisationfunktion(organisationfunktion_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_organisationfunktion(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_search_organisation(integer,uuid,organisationregistreringtype,tstzrange,integer,text[],uuid[],text[],organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_search_organisation(
    firstresult integer,
    organisation_uuid uuid,
    registreringobj organisationregistreringtype,
    virkningsoeg tstzrange,
    maxresults integer DEFAULT 2147483647,
    anyattrvaluearr text[] DEFAULT '{}'::text[],
    anyuuidarr uuid[] DEFAULT '{}'::uuid[],
    anyurnarr text[] DEFAULT '{}'::text[],
    auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::organisationregistreringtype[]
)
RETURNS uuid[]
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    organisation_candidates uuid[];
    organisation_candidates_is_initialized boolean;
    --to_be_applyed_filter_uuids uuid[];
    attrEgenskaberTypeObj OrganisationEgenskaberAttrType;


    tilsGyldighedTypeObj OrganisationGyldighedTilsType;

    relationTypeObj OrganisationRelationType;
    anyAttrValue text;
    anyuuid uuid;
    anyurn text;



    auth_filtered_uuids uuid[];


BEGIN

--RAISE DEBUG 'step 0:registreringObj:%',registreringObj;

organisation_candidates_is_initialized := false;

IF organisation_uuid is not NULL THEN
    organisation_candidates:= ARRAY[organisation_uuid];
    organisation_candidates_is_initialized:=true;
    IF registreringObj IS NULL THEN
    --RAISE DEBUG 'no registreringObj'
    ELSE
        organisation_candidates:=array(
                SELECT DISTINCT
                b.organisation_id
                FROM
                organisation a
                JOIN organisation_registrering b on b.organisation_id=a.id
                WHERE
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )

        );
    END IF;
END IF;


--RAISE DEBUG 'organisation_candidates_is_initialized step 1:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 1:%',organisation_candidates;
--/****************************//


--RAISE NOTICE 'organisation_candidates_is_initialized step 2:%',organisation_candidates_is_initialized;
--RAISE NOTICE 'organisation_candidates step 2:%',organisation_candidates;

--/****************************//
--filter on attributes
--/**********************************************************//
--Filtration on attribute: Egenskaber
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).attrEgenskaber IS NULL THEN
    --RAISE DEBUG 'as_search_organisation: skipping filtration on attrEgenskaber';
ELSE

    IF (coalesce(array_length(organisation_candidates,1),0)>0 OR NOT organisation_candidates_is_initialized) THEN

        FOREACH attrEgenskaberTypeObj IN ARRAY registreringObj.attrEgenskaber

        LOOP
            organisation_candidates:=array(
            SELECT DISTINCT
            b.organisation_id
            FROM  organisation_attr_egenskaber a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id

            WHERE
                (
                    (
                        attrEgenskaberTypeObj.virkning IS NULL
                        OR
                        (
                            (
                                (
                                     (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL
                                )
                                OR
                                (
                                    (attrEgenskaberTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                                )
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerRef IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).AktoerTypeKode IS NULL OR (attrEgenskaberTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                            )
                            AND
                            (
                                    (attrEgenskaberTypeObj.virkning).NoteTekst IS NULL OR  (a.virkning).NoteTekst ILIKE (attrEgenskaberTypeObj.virkning).NoteTekst
                            )
                        )
                    )
                )
                AND
                (
                    (NOT (attrEgenskaberTypeObj.virkning IS NULL OR (attrEgenskaberTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    attrEgenskaberTypeObj.brugervendtnoegle IS NULL
                    OR
                    a.brugervendtnoegle ILIKE attrEgenskaberTypeObj.brugervendtnoegle --case insensitive
                )
                AND
                (
                    attrEgenskaberTypeObj.organisationsnavn IS NULL
                    OR
                    a.organisationsnavn ILIKE attrEgenskaberTypeObj.organisationsnavn --case insensitive
                )
                AND

                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )

            );


            organisation_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--RAISE DEBUG 'organisation_candidates_is_initialized step 3:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 3:%',organisation_candidates;

--/**********************************************************//
--Filtration on anyAttrValueArr
--/**********************************************************//
IF coalesce(array_length(anyAttrValueArr ,1),0)>0 THEN

    FOREACH anyAttrValue IN ARRAY anyAttrValueArr
    LOOP
        organisation_candidates:=array(

            SELECT DISTINCT
            b.organisation_id

            FROM  organisation_attr_egenskaber a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id

            WHERE
            (
                        a.brugervendtnoegle ILIKE anyAttrValue OR
                        a.organisationsnavn ILIKE anyAttrValue
            )
            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )
            AND

                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )


        );

    organisation_candidates_is_initialized:=true;

    END LOOP;

END IF;



--RAISE DEBUG 'registrering,%',registreringObj;


--/**********************************************************//
--Filtration on state: Gyldighed
--/**********************************************************//
IF registreringObj IS NULL OR (registreringObj).tilsGyldighed IS NULL THEN
    --RAISE DEBUG 'as_search_organisation: skipping filtration on tilsGyldighed';
ELSE
    IF (coalesce(array_length(organisation_candidates,1),0)>0 OR organisation_candidates_is_initialized IS FALSE ) THEN

        FOREACH tilsGyldighedTypeObj IN ARRAY registreringObj.tilsGyldighed
        LOOP
            organisation_candidates:=array(
            SELECT DISTINCT
            b.organisation_id
            FROM  organisation_tils_gyldighed a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id
            WHERE
                (
                    tilsGyldighedTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (tilsGyldighedTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerRef IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).AktoerTypeKode IS NULL OR (tilsGyldighedTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (tilsGyldighedTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (tilsGyldighedTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT ((tilsGyldighedTypeObj.virkning) IS NULL OR (tilsGyldighedTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    tilsGyldighedTypeObj.gyldighed IS NULL
                    OR
                    tilsGyldighedTypeObj.gyldighed = a.gyldighed
                )
                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )

    );


            organisation_candidates_is_initialized:=true;


        END LOOP;
    END IF;
END IF;

/*
--relationer OrganisationRelationType[]
*/


--RAISE DEBUG 'organisation_candidates_is_initialized step 4:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 4:%',organisation_candidates;

--/**********************************************************//
--Filtration on relations
--/**********************************************************//


IF registreringObj IS NULL OR (registreringObj).relationer IS NULL THEN
    --RAISE DEBUG 'as_search_organisation: skipping filtration on relationer';
ELSE
    IF (coalesce(array_length(organisation_candidates,1),0)>0 OR NOT organisation_candidates_is_initialized) AND (registreringObj).relationer IS NOT NULL THEN
        FOREACH relationTypeObj IN ARRAY registreringObj.relationer
        LOOP
            organisation_candidates:=array(
            SELECT DISTINCT
            b.organisation_id
            FROM  organisation_relation a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id
            WHERE
                (
                    relationTypeObj.virkning IS NULL
                    OR
                    (
                        (
                             (relationTypeObj.virkning).TimePeriod IS NULL
                            OR
                            (relationTypeObj.virkning).TimePeriod && (a.virkning).TimePeriod
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerRef IS NULL OR (relationTypeObj.virkning).AktoerRef=(a.virkning).AktoerRef
                        )
                        AND
                        (
                                (relationTypeObj.virkning).AktoerTypeKode IS NULL OR (relationTypeObj.virkning).AktoerTypeKode=(a.virkning).AktoerTypeKode
                        )
                        AND
                        (
                                (relationTypeObj.virkning).NoteTekst IS NULL OR (a.virkning).NoteTekst ILIKE (relationTypeObj.virkning).NoteTekst
                        )
                    )
                )
                AND
                (
                    (NOT (relationTypeObj.virkning IS NULL OR (relationTypeObj.virkning).TimePeriod IS NULL)) --we have already filtered on virkning above
                    OR
                    (
                        virkningSoeg IS NULL
                        OR
                        virkningSoeg && (a.virkning).TimePeriod
                    )
                )
                AND
                (
                    relationTypeObj.relType IS NULL
                    OR
                    relationTypeObj.relType = a.rel_type
                )
                AND
                (
                    relationTypeObj.uuid IS NULL
                    OR
                    relationTypeObj.uuid = a.rel_maal_uuid
                )
                AND
                (
                    relationTypeObj.objektType IS NULL
                    OR
                    relationTypeObj.objektType = a.objekt_type
                )
                AND
                (
                    relationTypeObj.urn IS NULL
                    OR
                    relationTypeObj.urn = a.rel_maal_urn
                )


                AND
                        -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )

    );

            organisation_candidates_is_initialized:=true;

        END LOOP;
    END IF;
END IF;
--/**********************//

IF coalesce(array_length(anyuuidArr ,1),0)>0 THEN

    FOREACH anyuuid IN ARRAY anyuuidArr
    LOOP
        organisation_candidates:=array(
            SELECT DISTINCT
            b.organisation_id

            FROM  organisation_relation a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id
            WHERE

            anyuuid = a.rel_maal_uuid

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )


            );

    organisation_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

IF coalesce(array_length(anyurnArr ,1),0)>0 THEN

    FOREACH anyurn IN ARRAY anyurnArr
    LOOP
        organisation_candidates:=array(
            SELECT DISTINCT
            b.organisation_id

            FROM  organisation_relation a
            JOIN organisation_registrering b on a.organisation_registrering_id=b.id
            WHERE

            anyurn = a.rel_maal_urn

            AND
            (
                virkningSoeg IS NULL
                OR
                virkningSoeg && (a.virkning).TimePeriod
            )

            AND
                    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )


            );

    organisation_candidates_is_initialized:=true;
    END LOOP;
END IF;

--/**********************//

-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0




--RAISE DEBUG 'organisation_candidates_is_initialized step 5:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 5:%',organisation_candidates;

IF registreringObj IS NULL THEN
    --RAISE DEBUG 'registreringObj IS NULL';
ELSE
    IF NOT organisation_candidates_is_initialized THEN
        organisation_candidates:=array(
        SELECT DISTINCT
            organisation_id
        FROM
            organisation_registrering b
        WHERE
                -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
        -- SPDX-License-Identifier: MPL-2.0
		(
				(registreringObj.registrering) IS NULL
				OR
				(
					(
						(registreringObj.registrering).timeperiod IS NULL
						OR
						(registreringObj.registrering).timeperiod && (b.registrering).timeperiod
					)
					AND
					(
						(registreringObj.registrering).livscykluskode IS NULL
						OR
						(registreringObj.registrering).livscykluskode = (b.registrering).livscykluskode
					)
					AND
					(
						(registreringObj.registrering).brugerref IS NULL
						OR
						(registreringObj.registrering).brugerref = (b.registrering).brugerref
					)
					AND
					(
						(registreringObj.registrering).note IS NULL
						OR
						(b.registrering).note ILIKE (registreringObj.registrering).note
					)
			)
		)
		AND
		(
			(
				((b.registrering).livscykluskode <> 'Slettet'::Livscykluskode )
				AND
					(
						(registreringObj.registrering) IS NULL
						OR
						(registreringObj.registrering).livscykluskode IS NULL
					)
			)
			OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				(registreringObj.registrering).livscykluskode IS NOT NULL
			)
		)
		AND
		(
			(
			  (
			  	(registreringObj.registrering) IS NULL
			  	OR
			  	(registreringObj.registrering).timeperiod IS NULL
			  )
			  AND
			  upper((b.registrering).timeperiod)='infinity'::TIMESTAMPTZ
			)
		OR
			(
				(NOT ((registreringObj.registrering) IS NULL))
				AND
				((registreringObj.registrering).timeperiod IS NOT NULL)
			)
		)
		AND
		((NOT organisation_candidates_is_initialized) OR b.organisation_id = ANY (organisation_candidates) )

        )
        ;

        organisation_candidates_is_initialized:=true;
    END IF;
END IF;


IF NOT organisation_candidates_is_initialized THEN
    --No filters applied!
    organisation_candidates:=array(
        SELECT DISTINCT id FROM organisation a
    );
ELSE
    organisation_candidates:=array(
        SELECT DISTINCT id FROM unnest(organisation_candidates) as a(id)
        );
END IF;

--RAISE DEBUG 'organisation_candidates_is_initialized step 6:%',organisation_candidates_is_initialized;
--RAISE DEBUG 'organisation_candidates step 6:%',organisation_candidates;


/*** Filter out the objects that does not meets the stipulated access criteria  ***/
auth_filtered_uuids:=_as_filter_unauth_organisation(organisation_candidates,auth_criteria_arr);
/*********************/
IF firstResult > 0 or maxResults < 2147483647 THEN
   auth_filtered_uuids = _as_sorted_organisation(auth_filtered_uuids, virkningSoeg, registreringObj, firstResult, maxResults);
END IF;
return auth_filtered_uuids;


END;
$function$

;

-- as_update_bruger(uuid,uuid,text,livscykluskode,brugeregenskaberattrtype[],brugerudvidelserattrtype[],brugergyldighedtilstype[],brugerrelationtype[],timestamp with time zone,brugerregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_bruger(
    bruger_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber brugeregenskaberattrtype[],
    attrudvidelser brugerudvidelserattrtype[],
    tilsgyldighed brugergyldighedtilstype[],
    relationer brugerrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr brugerregistreringtype[] DEFAULT NULL::brugerregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.brugernavn,a.brugertype,a.virkning
                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update bruger with uuid [%], as the bruger have overlapping virknings in the given egenskaber array :%', bruger_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).brugernavn IS NULL  OR  (attrEgenskaberObj).brugertype IS NULL  THEN

            INSERT INTO bruger_attr_egenskaber (brugervendtnoegle, brugernavn, brugertype, virkning, bruger_registrering_id)
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

            INSERT INTO bruger_attr_egenskaber (brugervendtnoegle, brugernavn, brugertype, virkning, bruger_registrering_id)
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


            INSERT INTO bruger_attr_egenskaber (brugervendtnoegle, brugernavn, brugertype, virkning, bruger_registrering_id)
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.brugernavn,  attrEgenskaberObj.brugertype,  attrEgenskaberObj.virkning, new_bruger_registrering.id );
        END IF;

        END LOOP;

        END IF;

        IF attrEgenskaber IS NOT NULL AND coalesce(array_length(attrEgenskaber, 1), 0) = 0 THEN
            -- raise debug 'Skipping handling of egenskaber of previous registration as an empty array was explicit given.';
        ELSE



-- Handle egenskaber of previous registration, taking overlapping
-- virknings into consideration (using function subtract_tstzrange)

    INSERT INTO bruger_attr_egenskaber (brugervendtnoegle, brugernavn, brugertype, virkning, bruger_registrering_id)
    SELECT  a.brugervendtnoegle,
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
      RAISE EXCEPTION 'Aborted updating bruger with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', bruger_uuid, to_json(read_new_bruger_reg), to_json(read_prev_bruger_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_bruger_registrering.id;
END; $function$

;

-- as_update_facet(uuid,uuid,text,livscykluskode,facetegenskaberattrtype[],facetpublicerettilstype[],facetrelationtype[],timestamp with time zone,facetregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_facet(
    facet_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber facetegenskaberattrtype[],
    tilspubliceret facetpublicerettilstype[],
    relationer facetrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr facetregistreringtype[] DEFAULT NULL::facetregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.beskrivelse,a.opbygning,a.ophavsret,a.plan,a.supplement,a.retskilde,a.virkning
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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.opbygning,  attrEgenskaberObj.ophavsret,  attrEgenskaberObj.plan,  attrEgenskaberObj.supplement,  attrEgenskaberObj.retskilde,  attrEgenskaberObj.virkning, new_facet_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating facet with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', facet_uuid, to_json(read_new_facet_reg), to_json(read_prev_facet_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_facet_registrering.id;
END; $function$

;

-- as_update_itsystem(uuid,uuid,text,livscykluskode,itsystemegenskaberattrtype[],itsystemgyldighedtilstype[],itsystemrelationtype[],timestamp with time zone,itsystemregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_itsystem(
    itsystem_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber itsystemegenskaberattrtype[],
    tilsgyldighed itsystemgyldighedtilstype[],
    relationer itsystemrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr itsystemregistreringtype[] DEFAULT NULL::itsystemregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.itsystemnavn,a.itsystemtype,a.konfigurationreference,a.virkning
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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.itsystemnavn,  attrEgenskaberObj.itsystemtype,  attrEgenskaberObj.konfigurationreference,  attrEgenskaberObj.virkning, new_itsystem_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating itsystem with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', itsystem_uuid, to_json(read_new_itsystem_reg), to_json(read_prev_itsystem_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_itsystem_registrering.id;
END; $function$

;

-- as_update_klasse(uuid,uuid,text,livscykluskode,klasseegenskaberattrtype[],klassepublicerettilstype[],klasserelationtype[],timestamp with time zone,klasseregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_klasse(
    klasse_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber klasseegenskaberattrtype[],
    tilspubliceret klassepublicerettilstype[],
    relationer klasserelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr klasseregistreringtype[] DEFAULT NULL::klasseregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.beskrivelse,a.eksempel,a.omfang,a.titel,a.retskilde,a.aendringsnotat,a.virkning,a.soegeord
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
                VALUES ( new_id_klasse_attr_egenskaber,   attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.eksempel,  attrEgenskaberObj.omfang,  attrEgenskaberObj.titel,  attrEgenskaberObj.retskilde,  attrEgenskaberObj.aendringsnotat,  attrEgenskaberObj.virkning, new_klasse_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating klasse with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', klasse_uuid, to_json(read_new_klasse_reg), to_json(read_prev_klasse_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_klasse_registrering.id;
END; $function$

;

-- as_update_klassifikation(uuid,uuid,text,livscykluskode,klassifikationegenskaberattrtype[],klassifikationpublicerettilstype[],klassifikationrelationtype[],timestamp with time zone,klassifikationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_klassifikation(
    klassifikation_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber klassifikationegenskaberattrtype[],
    tilspubliceret klassifikationpublicerettilstype[],
    relationer klassifikationrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr klassifikationregistreringtype[] DEFAULT NULL::klassifikationregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.beskrivelse,a.kaldenavn,a.ophavsret,a.virkning

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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.beskrivelse,  attrEgenskaberObj.kaldenavn,  attrEgenskaberObj.ophavsret,  attrEgenskaberObj.virkning, new_klassifikation_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating klassifikation with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', klassifikation_uuid, to_json(read_new_klassifikation_reg), to_json(read_prev_klassifikation_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_klassifikation_registrering.id;
END; $function$

;

-- as_update_organisationenhed(uuid,uuid,text,livscykluskode,organisationenhedegenskaberattrtype[],organisationenhedgyldighedtilstype[],organisationenhedrelationtype[],timestamp with time zone,organisationenhedregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_organisationenhed(
    organisationenhed_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber organisationenhedegenskaberattrtype[],
    tilsgyldighed organisationenhedgyldighedtilstype[],
    relationer organisationenhedrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr organisationenhedregistreringtype[] DEFAULT NULL::organisationenhedregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.enhedsnavn,a.virkning

                    HAVING COUNT(*) > 1) THEN
                    RAISE EXCEPTION 'Unable to update organisationenhed with uuid [%], as the organisationenhed have overlapping virknings in the given egenskaber array :%', organisationenhed_uuid, to_json(attrEgenskaber) USING ERRCODE = 'MO400';
    END IF;

    FOREACH attrEgenskaberObj IN ARRAY attrEgenskaber LOOP
        -- To avoid needless fragmentation we'll check for presence of
        -- null values in the fields - and if none are present, we'll skip
        -- the merging operations
        IF  (attrEgenskaberObj).brugervendtnoegle IS NULL  OR  (attrEgenskaberObj).enhedsnavn IS NULL  THEN

            INSERT INTO organisationenhed_attr_egenskaber ( brugervendtnoegle,enhedsnavn, organisationenhed_registrering_id)
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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.enhedsnavn,  attrEgenskaberObj.virkning, new_organisationenhed_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating organisationenhed with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisationenhed_uuid, to_json(read_new_organisationenhed_reg), to_json(read_prev_organisationenhed_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisationenhed_registrering.id;
END; $function$

;

-- as_update_organisationfunktion(uuid,uuid,text,livscykluskode,organisationfunktionegenskaberattrtype[],organisationfunktionudvidelserattrtype[],organisationfunktiongyldighedtilstype[],organisationfunktionrelationtype[],timestamp with time zone,organisationfunktionregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_organisationfunktion(
    organisationfunktion_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber organisationfunktionegenskaberattrtype[],
    attrudvidelser organisationfunktionudvidelserattrtype[],
    tilsgyldighed organisationfunktiongyldighedtilstype[],
    relationer organisationfunktionrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr organisationfunktionregistreringtype[] DEFAULT NULL::organisationfunktionregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.funktionsnavn,a.virkning
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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.funktionsnavn,  attrEgenskaberObj.virkning, new_organisationfunktion_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating organisationfunktion with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisationfunktion_uuid, to_json(read_new_organisationfunktion_reg), to_json(read_prev_organisationfunktion_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisationfunktion_registrering.id;
END; $function$

;

-- as_update_organisation(uuid,uuid,text,livscykluskode,organisationegenskaberattrtype[],organisationgyldighedtilstype[],organisationrelationtype[],timestamp with time zone,organisationregistreringtype[])

CREATE OR REPLACE FUNCTION actual_state.as_update_organisation(
    organisation_uuid uuid,
    brugerref uuid,
    note text,
    livscykluskode livscykluskode,
    attregenskaber organisationegenskaberattrtype[],
    tilsgyldighed organisationgyldighedtilstype[],
    relationer organisationrelationtype[],
    lostupdatepreventiontz timestamp with time zone DEFAULT NULL::timestamp with time zone,
    auth_criteria_arr organisationregistreringtype[] DEFAULT NULL::organisationregistreringtype[]
)
RETURNS bigint
LANGUAGE plpgsql
AS $function$
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
                    a.brugervendtnoegle,a.organisationsnavn,a.virkning
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
                VALUES (  attrEgenskaberObj.brugervendtnoegle,  attrEgenskaberObj.organisationsnavn,  attrEgenskaberObj.virkning, new_organisation_registrering.id );
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
      RAISE EXCEPTION 'Aborted updating organisation with id [%] as the given data, does not give raise to a new registration. Aborted reg:[%], previous reg:[%]', organisation_uuid, to_json(read_new_organisation_reg), to_json(read_prev_organisation_reg) USING ERRCODE = 'MO400';
    END IF;


    return new_organisation_registrering.id;
END; $function$

;
