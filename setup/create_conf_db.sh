#!/bin/bash
export PGPASSWORD=mora

declare -A DEFAULTS
DEFAULTS[show_roles]='True'
DEFAULTS[show_user_key]='True'
DEFAULTS[show_location]='True'


sudo -u postgres psql -c "CREATE USER mora WITH ENCRYPTED PASSWORD 'mora';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mora TO mora;"
sudo -u postgres psql -c "DROP DATABASE mora;"
sudo -u postgres psql -c "CREATE DATABASE mora OWNER mora;"


CREATE_QUERY="
CREATE TABLE orgunit_settings(
    id serial PRIMARY KEY,
    object UUID,
    setting varchar(255) NOT NULL,
    value varchar(255) NOT NULL
);"

echo $CREATE_QUERY
psql -h localhost -U mora -d mora -c "$CREATE_QUERY"

for key in "${!DEFAULTS[@]}"
do
    QUERY="
       INSERT INTO orgunit_settings (
           object,
           setting,
           value
       )
       values (
           Null,
          '$key',
          '${DEFAULTS[$key]}'
       );"
    psql -h localhost -U mora -d mora -c "$QUERY"
done
