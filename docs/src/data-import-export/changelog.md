---
title: Release History
---

# CHANGELOG

2.33.1 - 2022-05-09
-------------------

[#xxxxx] OS2Sync: Moved constants into settings.

2.33.0 - 2022-05-05
-------------------

[#46511] AD Life Cycle: Add feature to add/overwrite part of AD settings when running ad_life_cycle.py

2.32.6 - 2022-05-05
-------------------

[#50123] OS2sync export: paginate calls to read all user uuids from MO to avoid crash when reading many employees.

2.32.5 - 2022-05-03
-------------------

[#49971] Add `exports_ad_life_cycle_disable_accounts` to `job-runner.sh` so it can be run from `cron.sh`.

2.32.4 - 2022-05-03
-------------------

[#49999] Fixes kle import/export scripts that are outdated because of changes to MO configuration and FastAPI trailing slashes.

2.32.3 - 2022-05-02
-------------------

[#49971] Bugfix: handle multiple email addresses per employee in `MORESTSource.get_email_address`.

2.32.2 - 2022-05-02
-------------------

[#49971] AD Write: fix use of `first_address_of_type` Jinja filter in `_get_sync_user_command`

2.32.1 - 2022-04-27
-------------------

[#49928] AD_life_cycle: 
* Cache all AD users to correctly compare to MO. 
* Resolve DAR when using loracache

2.32.0 - 2022-04-27
-------------------

[#49340] Add UUID to Ansatte report

2.31.0 - 2022-04-27
-------------------

[#49477] Optional log file path setting

2.30.0 - 2022-04-25
-------------------

[#49936] Script for moving org unit

2.29.5 - 2022-04-25
-------------------

[#49891] OS2Sync: fix issue with units without org_unit_level or org_unit_type.

2.29.4 - 2022-04-22
-------------------

[#49734] New uuids for Silkeborg FK-org

2.29.3 - 2022-04-22
-------------------

[#49891] OS2sync: fix wrong use of setting.

2.29.2 - 2022-04-22
-------------------

[#49891] OS2Sync: fix bug where uuids where compared to strings.

2.29.1 - 2022-04-21
-------------------

[#49772] OS2sync: Regenerate keycloak token by not lru_cache'ing session object.

2.29.0 - 2022-04-21
-------------------

[#49885] Export SDChangedAt state

2.28.4 - 2022-04-14
-------------------

[#49668] Add force flag to SDChangedAt. Return early.

2.28.3 - 2022-04-11
-------------------

[#49741] Lint os2sync with precommit

2.28.2 - 2022-04-11
-------------------

[#xxxxx] Fix call to OS2MO that was broken when moving away from morahelpers.

2.28.1 - 2022-04-08
-------------------

[#xxxxx] Os2sync - Fix call to os2mo_get

2.28.0 - 2022-04-08
-------------------

[#49668] Introduce misc feature flags

2.27.0 - 2022-04-08
-------------------

[#49218] Enable os2sync to use values from it-systems listed in settings as uuids in fk-org.

2.26.0 - 2022-04-08
-------------------

[#41274] AD_writer username disallowed list can now be read from a database.

2.25.0 - 2022-04-08
-------------------

[#49383] Adds OS2sync CLI to update single org_units or employees to FK-org.

2.24.8 - 2022-04-08
-------------------

[#49594] AAK LOS import: use correct BVN for "non-primary" class

2.24.7 - 2022-04-08
-------------------

[#48316] `SqlExport._add_associations`: handle missing class for "association_type"

2.24.6 - 2022-04-06
-------------------

[#49633] Fix virtual environment issues

2.24.5 - 2022-04-05
-------------------

[#49663] Fixed SD test connectivity job-runner bug

2.24.4 - 2022-04-04
-------------------

[#49597] Fixed Poetry issue

2.24.3 - 2022-04-04
-------------------

[#49602] Fix compare of parent uuids when there are no parent (an external organisation)

2.24.2 - 2022-04-01
-------------------

[#48316] LoraCache: handle associations without "association_type"

2.24.1 - 2022-04-01
-------------------

[#49253] Create SD Changed At image

2.24.0 - 2022-04-01
-------------------

[#49292] Make SD integration independent of DIPEX

2.23.1 - 2022-04-01
-------------------

[#xxxxx] Fix comparison of UUID and string of UUID in loracache-os2sync

2.23.0 - 2022-03-31
-------------------

[#49524] Optional exclude or include CPR list for SD-changed-at

2.22.6 - 2022-03-31
-------------------

[#xxxxx] Fix mistake in variable from settings.

2.22.5 - 2022-03-31
-------------------

[#xxxxx] Fix missing settings in os2sync lcdb

2.22.4 - 2022-03-30
-------------------

[#49524] Handle multiple JobPositionIdentifers when doing no salary minimum consistency check

2.22.3 - 2022-03-30
-------------------

[#49541] Adds AMG unit-type to list of MED-organization unit-types

2.22.2 - 2022-03-29
-------------------

[#49292] Release DIPEX to PYPI

2.22.1 - 2022-03-29
-------------------

[#49292] Fix black issues

2.22.0 - 2022-03-28
-------------------

[#49219] Change os2sync to use Pydantic settings. This allows configuration either by a settings.json file or by environment variables.

2.21.3 - 2022-03-25
-------------------

[#49447] Fix a bug where opus_diff_import crashed when a unit had no address

2.21.2 - 2022-03-24
-------------------

[#49339] Increase robustness of OS2phonebook export job

2.21.1 - 2022-03-22
-------------------

[#49377] Fix None/NULL stillingsbetegnelse_titel

2.21.0 - 2022-03-22
-------------------

[#47138] Rework AD username generation and exclusion code

2.20.10 - 2022-03-21
--------------------

[#49338] Reintroduce retry logic in `MoraHelper._mo_lookup`

2.20.9 - 2022-03-18
-------------------

[#49146] Fixed broken test-sd-connectivity script

2.20.8 - 2022-03-17
-------------------

[#49291] Added missing settings to FixDepartments

2.20.7 - 2022-03-17
-------------------

[#49146] Fixed bug assuming only one profession present in SD employment

2.20.6 - 2022-03-16
-------------------

[#49146] Add missing settings argument to sd-lookup

2.20.5 - 2022-03-15
-------------------

[#49146] Handle missing Pydantic settings conversions

2.20.4 - 2022-03-14
-------------------

[#49146] Use RA Utils version 1.0.0 or greater (fixes problem with loading settings.json)

2.20.3 - 2022-03-10
-------------------

[#46874] Fix recalculate_primary

2.20.2 - 2022-03-10
-------------------

[#48939] Handle SD engagements inconsistent according to no-salary-minimum

2.20.1 - 2022-03-09
-------------------

[#48939] Do not create inconsistent external engagements

2.20.0 - 2022-03-09
-------------------

[#46894] Use SD Pydantic settings model in SD-changed-at

2.19.1 - 2022-03-09
-------------------

[#45401] AD_sync removes engagement info from users when the AD-account is removed and removes AD engagement info from engagements that are no longer primary

2.19.0 - 2022-03-07
-------------------

[#46715] Use poetry for dependency management

2.18.1 - 2022-02-23
-------------------

[#48809] Skip connecting it-system during Opus import if multiple entries exist in MO.

2.18.0 - 2022-02-17
-------------------

[#46874] Better recalculate reporting

2.17.0 - 2022-02-10
-------------------

[#46894] SD Pydantic config module

2.16.0 - 2022-02-10
-------------------

[#48067] Log when creating engagement is skipped due to wierd SD data

2.15.1 - 2022-02-07
-------------------

[#48132] Patch for opus_terminate_filtered script, so it won't delete users with unfiltered engagements in the past or future.

2.15.0 - 2022-02-04
-------------------

[#48132] Add check for users and engagements that should have been filtered from opus-import and a script to remove them.

2.14.0 - 2022-02-02
-------------------

[#48375] Handle inconsistent leave start date

2.13.0 - 2022-02-01
-------------------

[#48243] Flag to choose SD engagement start date during import

2.12.1 - 2022-01-27
-------------------

[#48202] Handle Nones within fix_department.py

2.12.0 - 2022-01-27
-------------------

[#48136] Adds new columns to "Viborg eksterne" report. Deprecate MO version and support only loracache version of the script.

2.11.0 - 2022-01-26
-------------------

[#46166] Adds timestamp as a field available for AD_writer

2.10.2 - 2022-01-25
-------------------

[#48083] Makes os2sync integration able to use keycloak authentication.

2.10.1 - 2022-01-24
-------------------

[#48067] Fix BC anniversary date problem

2.10.0 - 2022-01-20
-------------------

[#48050] Fix engagement termination date bug

2.9.1 - 2022-01-19
------------------

[#47241] Move ad-script and add documentation

2.9.0 - 2022-01-18
------------------

[#41612] SD_changed_at uses datetimes to allow running over any timespan, eg. several days or multiple times a day.

2.8.0 - 2022-01-17
------------------

[#47960] Introduce continuous deployment to Flux

2.7.2 - 2022-01-14
------------------

[#47734] Fix LoRaCache CLI flag

2.7.1 - 2022-01-14
------------------

[#47734] Add job for RUN_CACHE_HISTORIC_SKIP_PAST_LORACACHE 🥲

2.7.0 - 2022-01-12
------------------

[#47623] Add new dipex-job exports_ad_enddate_fixer write enddates of terminated users to AD.

2.6.2 - 2022-01-12
------------------

[#47755] Fix NTLM to always use first set of credentials for the winrm connections

2.6.1 - 2022-01-12
------------------

[#47911] Fix UUID to string bug

2.6.0 - 2022-01-12
------------------

[#46874] Added default calculate primary function

2.5.6 - 2022-01-10
------------------

[#47856] Add retry to OS2phonebook export

2.5.5 - 2022-01-10
------------------

[#47656] Fix bug that would create it-systems with random uuid usernames during opus-import

2.5.4 - 2022-01-06
------------------

[#xxxxx] Fixes a bug where opus reimport script writes to rundb

2.5.3 - 2022-01-06
------------------

[#47656] Add handeling of changing/terminating IT-system accounts to Opus-diff-import

2.5.2 - 2022-01-05
------------------

[#47734] Fix LoRaCache not properly exporting historic data when called from the CLI

2.5.1 - 2022-01-03
------------------

[#47247] Fixes for opus reimport script

2.5.0 - 2021-12-30
------------------

[#47241] Add script to reimport users or units from opus.

2.4.0 - 2021-12-22
------------------

[#47488] Add 'vacuum' command to remove_duplicates tool

2.3.0 - 2021-12-22
------------------

[#47488] Add script to remove duplicate registrations from user tables

2.2.5 - 2021-12-22
------------------

[#47581] Do not read 'USE_CACHED_LORACACHE' environment variable when using the LoRaCache CLI

2.2.4 - 2021-12-21
------------------

[#47646] Fix OS2sync LoRa cache crashing because of missing "is_primary" field

2.2.3 - 2021-12-21
------------------

[#47581] Chill with the cached LoRaCache

2.2.2 - 2021-12-21
------------------

[#47622] Loracache allow vacant association

2.2.1 - 2021-12-20
------------------

[#47632] OS2sync uses paginated calls to avoid timeouts

2.2.0 - 2021-12-17
------------------

[#47581] Add support for cached LoRaCache

2.1.3 - 2021-12-17
------------------

[#44668] Associate leave with engagement during SD import

2.1.2 - 2021-12-17
------------------

[#47457] Catch and log when a managerrole has no person attached.

2.1.1 - 2021-12-16
------------------

[#47581] Decrease LoRaCache results per page from 5000 to 1000 to avoid LoRa database timeout

2.1.0 - 2021-12-16
------------------

[#47571] Fix update-dipex.sh error by adjusting build-system in pyproject.toml

[#47267] New featureflags for customizing opus-import

2.0.3 - 2021-12-15
------------------

[#47581] LoRa cache fix params retrying

2.0.2 - 2021-12-08
------------------

[#46715] Send git version to Grafana Cloud on checkout

2.0.1 - 2021-12-08
------------------

[#46715] Trigger new release

2.0.0 - 2021-12-08
------------------

[#46715] Implement automatic versioning through autopub
