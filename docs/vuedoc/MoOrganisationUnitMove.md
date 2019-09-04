# mo-organisation-unit-move 

A organisation unit move component. 

## data 

- `original` 

  The move, parentUnit, uuid, original, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `parent` 

**initial value:** `null` 

- `move` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

## computed properties 

- `requiredValidity` 

  A validity of one day, corresponding to the required validity
  of units: They only need to be valid on the date of the operation. 

   **dependencies:** `move`, `move` 

- `unitValidations` 

   **dependencies:** `original` 

- `parentValidations` 

   **dependencies:** `original`, `move`, `move` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `moveOrganisationUnit(evt)` 

  Move a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

