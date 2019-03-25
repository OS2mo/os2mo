# organisation-detail-tabs 

A organisation detail tabs component. 

## props 

- `uuid` ***String*** (*required*) 

  Defines a unique identifier which must be unique. 

- `org-unit-info` ***Object*** (*optional*) 

- `content` ***Object*** (*optional*) 

- `timemachine-friendly` ***Boolean*** (*optional*) 

  This Boolean property indicates the timemachine output. 

## data 

- `latestTab` 

  keep track of the latest tap shown 

**initial value:** `[object Object]` 

- `org_unit` 

  The org_unit, address, engagement, association, role, manager component value.
  Used to detect changes and restore the value for columns. 

**initial value:** `[object Object]` 

- `address` 

**initial value:** `[object Object]` 

- `engagement` 

**initial value:** `[object Object]` 

- `association` 

**initial value:** `[object Object]` 

- `role` 

**initial value:** `[object Object]` 

- `it` 

**initial value:** `[object Object]` 

- `manager` 

**initial value:** `[object Object]` 

- `related_unit` 

**initial value:** `[object Object]` 

- `components` 

  The MoOrganisationUnitEntry, MoAddressEntry component.
  Used to add edit and create for orgUnit and address. 

**initial value:** `[object Object]` 

## events 

- `show` 

## methods 

- `loadContent(contentType, event)` 

