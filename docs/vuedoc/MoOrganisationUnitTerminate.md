# mo-organisation-unit-terminate 

A organisation unit terminate component. 

## data 

- `org_unit` 

  The terminate, org_unit, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `terminate` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

## computed properties 

- `validDates` 

  Check if the organisation date are valid. 

   **dependencies:** `org_unit`, `org_unit` 

- `validity` 

   **dependencies:** `terminate`, `terminate` 


## methods 

- `onHidden()` 

- `loadContent(event)` 

- `endOrganisationUnit(evt)` 

  Terminate a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

