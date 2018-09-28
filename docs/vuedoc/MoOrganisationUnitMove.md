# mo-organisation-unit-move 

A organisation unit move component. 

## data 

- `currentUnit` 

  The move, currentUnit, uuid, original, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `''` 

- `uuid` 

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

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `moveOrganisationUnit(evt)` 

  Move a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

- `getCurrentUnit(unitUuid)` 

  Get current organisation unit. 

