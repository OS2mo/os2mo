create or replace function asd() returns trigger as $$
begin
    select id
    into strict adjacent
    from organisationenhed_relation
    where organisationenhed_registrering_id = NEW.organisationenhed_registrering_id
    and lower(virkning.timeperiod) == upper(NEW.virkning.timeperiod)
    and rel_maal_uuid = NEW.rel_maal_uuid
    and rel_maal_urn = NEW.rel_maal_urn
    and rel_type = NEW.rel_type
    and objekt_type = NEW.objekt_type;
    if found then
        update organisationenhed_relation
        set virkning.timeperiod = tstzrange(todo, todo)
        where id = adjacent.id;
        -- cancel original create/update
        return null;
    end if;

    -- TODO: det omvendte


    -- allow original create/update
    return NEW;
end;
$$ language plpgsql;

create trigger asd
before insert or update on organisationenhed_relation
for each row
execute function asd();


-- TODO:
-- set id = id


-- allw minions er på virkning.timeperiod
    --  lower_inc | upper_inc 
    -- -----------+-----------
    --  t         | f
    -- (1 row)

