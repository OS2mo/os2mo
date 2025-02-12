<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# CHANGELOG

## 8.4.1 - 2022-08-09

[#51183] Added missing vacate-field to EmployeeTerminate.

## 8.4.0 - 2022-07-29

[#51183] Created a new data model for Employee terminations

## 8.3.0 - 2022-07-19

[#51177] Revert "[Remove FacetClass] (21a86484)"

## 8.2.0 - 2022-07-18

[#49604] Allows "fictitious" birthdates in CPR validation

## 8.1.0 - 2022-07-18

[#51165] Created new data model for OrganisationUnit terminations

## 8.0.0 - 2022-07-15

[#51177] Bump major for FacetClass removal (21a86484)

## 7.3.0 - 2022-07-13

[#51165] Created new data model for OrganisationUnit terminations

## 7.2.0 - 2022-07-07

[#50818] Add Facet Write Model

## 7.1.0 - 2022-07-07

[#51177] Add a ClassWrite model. Removed FacetClass model.

## 7.0.2 - 2022-06-15

[#50418] Fix wrong name split

## 7.0.1 - 2022-06-14

[#50653] Added py.typed file to enable mypy typing

## 7.0.0 - 2022-06-10

[#47213] Remove is_primary flag from engagements to enable adding it to the model from graphql.

## 6.0.1 - 2022-06-03

[#50725] Fix LoRa model for class owners

## 6.0.0 - 2022-05-24

[#50418] Reorder details for employees and organisation units

## 5.13.0 - 2022-05-10

[#50067] Add EngagementAssociation model to MO models

## 5.12.4 - 2022-05-09

[#50189] Remove integration data from LoRa models

## 5.12.3 - 2022-04-26

[#49849] Fix bug in seniority parsing

## 5.12.2 - 2022-03-31

[#47920] Fix Klasse data model to include an optional description

## 5.12.1 - 2022-03-30

[#49533] Allow actor types and references in EffectiveTime

## 5.12.0 - 2022-03-25

[#49205] Remove full name from class

## 5.11.0 - 2022-03-23

[#48315] Add optional `ITUser.primary_uuid` attribute

## 5.10.0 - 2022-03-23

[#48312] Make `AssociationRead.association_type_uuid` optional

## 5.9.0 - 2022-03-21

[#49205] Make description non-optional, add full_name to ClassRead

## 5.8.0 - 2022-03-21

[#49205] Remove href attr (its computed in MO)

## 5.7.0 - 2022-03-21

[#49205] Add `note` attr to lora klasse

## 5.6.0 - 2022-03-17

[#49205] Add `owner` to mo ClassRead and lora KlasseRelations

## 5.5.0 - 2022-03-17

[#49205] Add example, href and description fields

## 5.4.0 - 2022-03-07

[#48315] Expose new `Association` fields `it_user` and `job_function`

## 5.3.2 - 2022-02-10

[#48565] Fix pypi publishing

## 5.3.1 - 2022-02-10

[#48565] Export KLE model

## 5.3.0 - 2022-02-10

[#48565] Fix KLE kle_aspect -> kle_aspects

## 5.2.0 - 2022-02-01

[#48176] Add models from GraphAPI module in MO

## 5.1.0 - 2022-01-24

[#48042] Make reference to org_unit's plural for RelatedUnit

## 5.0.0 - 2022-01-12

[#47912][#47699] Revert 'person' -> 'employee' for old MO and LoRa models.

## 4.0.3 - 2022-01-11

[#47680] String.lower object_type literal for LoRa objects.

## 4.0.2 - 2022-01-11

[#47764] Add missing description argument for some AddressRead attributes

## 4.0.1 - 2022-01-06

[#45480] Make from_simplified_fields uuid optional.

## 4.0.0 - 2022-01-05

[#47699] Use employee consistently instead of mixing person and employee

## 3.26.1 - 2022-01-03

[#47101] Add Leave reference to Engagement

## 3.26.0 - 2021-12-17

[#47099] Append uuid to attributes for RelatedUnitRead

## 3.25.0 - 2021-12-17

[#47090] Introduce LoRa OrganisationRead

## 3.24.0 - 2021-12-17

[#47090] Introduce LoRa FacetRead

## 3.23.0 - 2021-12-17

[#47100] Rename ITSystemBinding to ITUser

## 3.22.0 - 2021-12-17

[#47090] Introduce LoRa KlasseRead

## 3.21.0 - 2021-12-17

[#47098] `_uuid` suffix for `ManagerRead` attributes

## 3.20.1 - 2021-12-17

[#47090] Remove fetch.py and dependency

## 3.20.0 - 2021-12-16

[#47093] Append uuid to attributes for AssociationRead model

## 3.19.0 - 2021-12-16

[#47100] Append uuid to attributes for Role- and ITSystemRead models

## 3.18.4 - 2021-12-16

[#47091] Update Address model to include user_key

## 3.18.3 - 2021-12-16

[#47096] Append uuid to KLERead model

## 3.18.2 - 2021-12-14

[#47097] `_uuid` suffix for `LeaveRead` attributes

## 3.18.1 - 2021-12-13

[#47091] Append AddressRead fields with \_uuid

## 3.18.0 - 2021-12-08

[#47094] `_uuid` suffix for `EngagementRead` attributes

## 3.17.0 - 2021-12-03

[#47415] Add OrganisationRead model.

## 3.16.0 - 2021-12-02

[#47122] Add ITSystem base/read/write models.

## 3.15.3 - 2021-12-01

[#47088] Handle deprecated keys in EmployeeRead & fix seniority type

## 3.15.2 - 2021-11-26

[#47087] Fix field names in OrganisationUnitRead

## 3.15.1 - 2021-11-24

[#47202] Change use of Literals to str with custom validator

## 3.15.0 - 2021-11-23

[#46690] RelatedUnit base/read/write models.

## 3.14.0 - 2021-11-22

[#46691] Add Role base/read/write models

## 3.13.0 - 2021-11-22

[#46686] Add KLE base/read/write models

## 3.12.0 - 2021-11-22

[#46688] Add Manager base/read/write models

## 3.11.0 - 2021-11-18

[#46681] Add Address base/read/write models

## 3.10.0 - 2021-11-18

[#46685] Add ITSystemBinding base/read/write models

## 3.9.0 - 2021-11-18

[#46687] Add Leave base/read/write models

## 3.8.0 - 2021-11-17

[#46683] Add Engagement base/read/write models

## 3.7.0 - 2021-11-17

[#46682] Add Association base/read/write models

## 3.6.0 - 2021-11-15

[#46692] Add Employee base/read/write models

## 3.5.0 - 2021-11-11

[#46693] Add Organisation Unit base/read/write models

## 3.4.0 - 2021-11-08

[#46851] Make Address.from_simplified_fields UUID optional

## 3.3.0 - 2021-11-04

[#46741] Add from_simplified_fields to ITSystemBinding

## 3.2.0 - 2021-10-25

[#44433] Implement details: ITSystem, Role, Leave

## 3.1.0 - 2021-10-19

[#44543] Add OrganisationUnit details

## 3.0.0 - 2021-09-22

FacetClass now requires facet_uuid

## 2.1.3 - 2021-09-20

Accept 0 as last integer in CPR numbers

## 2.1.1 - 2021-07-13

Patch Address from simplified fields method

## 2.1.0 - 2021-07-13

Address.org is now an optional field

## 2.0.1 - 2021-07-01

Patch exceptions

## 2.0.0 - 2021-07-01

MO has been rearranged: details are now a submodule. The employee model has been updated to reflect MO payloads more closely.

## 1.0.1 - 2021-06-23

Export FacetClass

## 1.0.0 - 2021-06-10

Fully tested data models for OS2Mo & LoRa.

## 0.3.3 - 2021-05-12

Security update - pin Pydantic to 1.8.2

## 0.3.2 - 2021-05-07

Bugfix: KlasseProperties in /lora now has Field(alias="titel")

## 0.3.1 - 2021-05-05

Name change

## 0.3.0 - 2021-05-05

Added MO models

## 0.2.0 - 2021-05-05

LoRa models added
