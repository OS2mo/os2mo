<!--
SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

CHANGELOG
=========

3.23.0 - 2021-12-17
-------------------

[#47100] Rename ITSystemBinding to ITUser

3.22.0 - 2021-12-17
-------------------

[#47090] Introduce LoRa KlasseRead

3.21.0 - 2021-12-17
-------------------

[#47098] `_uuid` suffix for `ManagerRead` attributes

3.20.1 - 2021-12-17
-------------------

[#47090] Remove fetch.py and dependency

3.20.0 - 2021-12-16
-------------------

[#47093] Append uuid to attributes for AssociationRead model

3.19.0 - 2021-12-16
-------------------

[#47100] Append uuid to attributes for Role- and ITSystemRead models

3.18.4 - 2021-12-16
-------------------

[#47091] Update Address model to include user_key

3.18.3 - 2021-12-16
-------------------

[#47096] Append uuid to KLERead model

3.18.2 - 2021-12-14
-------------------

[#47097] `_uuid` suffix for `LeaveRead` attributes

3.18.1 - 2021-12-13
-------------------

[#47091] Append AddressRead fields with _uuid

3.18.0 - 2021-12-08
-------------------

[#47094] `_uuid` suffix for `EngagementRead` attributes

3.17.0 - 2021-12-03
-------------------

[#47415] Add OrganisationRead model.

3.16.0 - 2021-12-02
-------------------

[#47122] Add ITSystem base/read/write models.

3.15.3 - 2021-12-01
-------------------

[#47088] Handle deprecated keys in EmployeeRead & fix seniority type

3.15.2 - 2021-11-26
-------------------

[#47087] Fix field names in OrganisationUnitRead

3.15.1 - 2021-11-24
-------------------

[#47202] Change use of Literals to str with custom validator

3.15.0 - 2021-11-23
-------------------

[#46690] RelatedUnit base/read/write models.

3.14.0 - 2021-11-22
-------------------

[#46691] Add Role base/read/write models

3.13.0 - 2021-11-22
-------------------

[#46686] Add KLE base/read/write models

3.12.0 - 2021-11-22
-------------------

[#46688] Add Manager base/read/write models

3.11.0 - 2021-11-18
-------------------

[#46681] Add Address base/read/write models

3.10.0 - 2021-11-18
-------------------

[#46685] Add ITSystemBinding base/read/write models

3.9.0 - 2021-11-18
------------------

[#46687] Add Leave base/read/write models

3.8.0 - 2021-11-17
------------------

[#46683] Add Engagement base/read/write models

3.7.0 - 2021-11-17
------------------

[#46682] Add Association base/read/write models

3.6.0 - 2021-11-15
------------------

[#46692] Add Employee base/read/write models

3.5.0 - 2021-11-11
------------------

[#46693] Add Organisation Unit base/read/write models

3.4.0 - 2021-11-08
------------------

[#46851] Make Address.from_simplified_fields UUID optional

3.3.0 - 2021-11-04
------------------

[#46741] Add from_simplified_fields to ITSystemBinding

3.2.0 - 2021-10-25
------------------

[#44433] Implement details: ITSystem, Role, Leave

3.1.0 - 2021-10-19
------------------

[#44543] Add OrganisationUnit details

3.0.0 - 2021-09-22
------------------

FacetClass now requires facet_uuid 

2.1.3 - 2021-09-20
------------------

Accept 0 as last integer in CPR numbers 

2.1.1 - 2021-07-13
------------------

Patch Address from simplified fields method 

2.1.0 - 2021-07-13
------------------

Address.org is now an optional field 

2.0.1 - 2021-07-01
------------------

Patch exceptions 

2.0.0 - 2021-07-01
------------------

MO has been rearranged: details are now a submodule. The employee model has been updated to reflect MO payloads more closely.

1.0.1 - 2021-06-23
------------------

Export FacetClass 

1.0.0 - 2021-06-10
------------------

Fully tested data models for OS2Mo & LoRa.

0.3.3 - 2021-05-12
------------------

Security update - pin Pydantic to 1.8.2

0.3.2 - 2021-05-07
------------------

Bugfix: KlasseProperties in /lora now has Field(alias="titel")

0.3.1 - 2021-05-05
------------------

Name change

0.3.0 - 2021-05-05
------------------

Added MO models

0.2.0 - 2021-05-05
------------------

LoRa models added
