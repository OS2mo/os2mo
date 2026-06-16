{% extends "basis.jinja.sql" %}
-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0
{% block body %}


{% for tilstand, tilstand_values in tilstande.items() %}

CREATE OR REPLACE FUNCTION _remove_nulls_in_array(inputArr {{oio_type|title}}{{tilstand|title}}TilsType[])
  RETURNS {{oio_type|title}}{{tilstand|title}}TilsType[] AS
  $$
  DECLARE result {{oio_type|title}}{{tilstand|title}}TilsType[];
  DECLARE element {{oio_type|title}}{{tilstand|title}}TilsType;
  BEGIN

 IF inputArr IS NOT NULL THEN
    FOREACH element IN ARRAY inputArr
    LOOP
      IF element IS NULL OR (( element.{{tilstand}} IS NULL ) AND element.virkning IS NULL) THEN --CAUTION: foreach on {null} will result in element gets initiated with ROW(null,null....)
     -- RAISE DEBUG 'Skipping element';
      ELSE
      result:=array_append(result,element);
      END IF;
    END LOOP;
  ELSE
    return null;
  END IF;

  RETURN result;

  END;

 $$ LANGUAGE plpgsql IMMUTABLE
;
{% endfor %}


{%-for attribut , attribut_fields in attributter.items() %}

CREATE OR REPLACE FUNCTION _remove_nulls_in_array(inputArr {{oio_type|title}}{{attribut|title}}AttrType[])
  RETURNS {{oio_type|title}}{{attribut|title}}AttrType[] AS
  $$
  DECLARE result {{oio_type|title}}{{attribut|title}}AttrType[];
   DECLARE element {{oio_type|title}}{{attribut|title}}AttrType;
  BEGIN

  IF inputArr IS NOT NULL THEN
    FOREACH element IN ARRAY inputArr
    LOOP
{% if oio_type == "klasse" %}
      IF element IS NULL OR (( element.brugervendtnoegle IS NULL AND element.beskrivelse IS NULL AND element.eksempel IS NULL AND element.omfang IS NULL AND element.titel IS NULL AND element.retskilde IS NULL AND element.aendringsnotat IS NULL ) AND element.virkning IS NULL AND (element.soegeord IS NULL OR coalesce(array_length(element.soegeord,1),0)=0 )) THEN --CAUTION: foreach on {null} will result in element gets initiated with ROW(null,null....)
{% else %}
      IF element IS NULL OR (( element.{{attribut_fields|join(' IS NULL AND element.')}} IS NULL ) AND element.virkning IS NULL) THEN --CAUTION: foreach on {null} will result in element gets initiated with ROW(null,null....)
{% endif %}
    --  RAISE DEBUG 'Skipping element';
      ELSE
      result:=array_append(result,element);
      END IF;
    END LOOP;
  ELSE
    return null;
  END IF;

  RETURN result;

  END;

 $$ LANGUAGE plpgsql IMMUTABLE
;

{% endfor %}


CREATE OR REPLACE FUNCTION _remove_nulls_in_array(inputArr {{oio_type|title}}RelationType[])
RETURNS {{oio_type|title}}RelationType[] AS
$$
 DECLARE result {{oio_type|title}}RelationType[];
 DECLARE element {{oio_type|title}}RelationType;
  BEGIN

   IF inputArr IS NOT NULL THEN
    FOREACH element IN ARRAY inputArr
    LOOP
      IF element IS NULL OR ( element.relType IS NULL AND element.uuid IS NULL AND element.urn IS NULL AND element.objektType IS NULL AND element.virkning IS NULL  ) THEN --CAUTION: foreach on {null} will result in element gets initiated with ROW(null,null....)
      --RAISE DEBUG 'Skipping element';
      ELSE
      result:=array_append(result,element);
      END IF;
    END LOOP;
  ELSE
    return null;
  END IF;

  RETURN result;

  END;

 $$ LANGUAGE plpgsql IMMUTABLE
;


{% if oio_type == "klasse" %}
CREATE OR REPLACE FUNCTION _remove_nulls_in_array(inputArr KlasseSoegeordType[])
  RETURNS KlasseSoegeordType[] AS
  $$
  DECLARE result KlasseSoegeordType[];
  DECLARE element KlasseSoegeordType;
  BEGIN

 IF inputArr IS NOT NULL THEN
    FOREACH element IN ARRAY inputArr
    LOOP
      IF element IS NULL OR (element.soegeordidentifikator IS NULL AND element.beskrivelse IS NULL AND element.soegeordskategori IS NULL ) THEN
     -- RAISE DEBUG 'Skipping element';
      ELSE
      result:=array_append(result,element);
      END IF;
    END LOOP;
  ELSE
    return null;
  END IF;

  IF array_length(result,1)=0 THEN
    RETURN NULL;
  ELSE
    RETURN result;
  END IF;

  END;

 $$ LANGUAGE plpgsql IMMUTABLE
;
{% endif %}

{% endblock %}
