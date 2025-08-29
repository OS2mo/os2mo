CREATE or replace FUNCTION virkning_timeperiod(v virkning) RETURNS tstzrange
    AS 'select (v).timeperiod;'
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
