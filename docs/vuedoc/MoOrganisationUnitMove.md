# mo-organisation-unit-move 

A organisation unit move component. 

## data 

- `parentUnit` 

  The move, parentUnit, uuid, original, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `''` 

- `original` 

**initial value:** `null` 

- `move` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

## computed properties 

- `validity` 

   **dependencies:** `move` 

- `parentValidations` 

   **dependencies:** `original`, `move`, `validity` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `moveOrganisationUnit(evt)` 

  Move a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

- `getCurrentUnit(unitUuid)` 

  Get current organisation unit. 

