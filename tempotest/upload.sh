#!/bin/bash
# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

# Necessary psql environment variables must be set to run this script. See:
# https://www.postgresql.org/docs/current/libpq-envars.html

set -e

psql -c '
  CREATE TABLE IF NOT EXISTS os2mo_k6.runs(
      id serial PRIMARY KEY NOT NULL,
      timestamp timestamp NOT NULL DEFAULT NOW(),
      ci_job_id integer NOT NULL,
      ci_commit_sha text NOT NULL,
      ci_commit_timestamp timestamp NOT NULL,
      ci_commit_branch text,
      ci_commit_tag text,
      ci_merge_request_iid integer
  );'

psql -c '
  CREATE TABLE IF NOT EXISTS os2mo_k6.data(
      run_id integer REFERENCES os2mo_k6.runs (id) NOT NULL,
      metric_name text NOT NULL,
      timestamp timestamp NOT NULL,
      metric_value real NOT NULL,
      status smallint,
      method text,
      name text,
      "group" text,
      "check" text,
      error text,
      error_code smallint,
      scenario text,
      expected_response boolean,
      extra_tags text
  );'

# Explicit empty/unset handling because 'NULL' must be unquoted
if [ -n "$CI_COMMIT_TAG" ]; then
  export COMMIT_TAG="'$CI_COMMIT_TAG'"  # wrapped in quotes twice
else
  export COMMIT_TAG='NULL'
fi
if [ -n "$CI_MERGE_REQUEST_IID" ]; then
  export MERGE_REQUEST_IID="'$CI_MERGE_REQUEST_IID'"
else
  export MERGE_REQUEST_IID='NULL'
fi
if [ -n "$CI_COMMIT_BRANCH" ]; then
  export COMMIT_BRANCH="'$CI_COMMIT_BRANCH'"
else
  export COMMIT_BRANCH='NULL'
fi

psql \
  --single-transaction \
  -c '
  CREATE TEMP TABLE tmp(
      metric_name text NOT NULL,
      timestamp integer NOT NULL,
      metric_value real NOT NULL,
      "check" text,
      error text,
      error_code smallint,
      expected_response boolean,
      "group" text,
      method text,
      name text,
      scenario text,
      status smallint,
      extra_tags text
  );' \
  -c 'COPY tmp FROM STDIN CSV HEADER;' < "$1" \
  -c "
  WITH run AS (
    INSERT INTO os2mo_k6.runs(ci_job_id, ci_commit_sha, ci_commit_timestamp, ci_commit_branch, ci_commit_tag, ci_merge_request_iid)
    VALUES($CI_JOB_ID, '$CI_COMMIT_SHA', '$CI_COMMIT_TIMESTAMP', $COMMIT_BRANCH, $COMMIT_TAG, $MERGE_REQUEST_IID)
    RETURNING id
  )
  INSERT INTO os2mo_k6.data
  SELECT run.id, tmp.metric_name, to_timestamp(tmp.timestamp), tmp.metric_value, tmp.status, tmp.method, tmp.name, tmp.group, tmp.check, tmp.error, tmp.error_code, tmp.scenario, tmp.expected_response, tmp.extra_tags
  FROM tmp, run;"
