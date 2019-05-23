# mo-organisation-unit-rename 

A organisation unit rename component. 

## data 

- `original` 

  The rename, original, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `rename` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

## computed properties 

- `compareName` 

  Compare if the unit names are identical.
  If then return false. 

   **dependencies:** `rename`, `original`, `original`, `rename`, `original` 

- `orgUnitValidity` 

  Valid dates for orgUnit. 

   **dependencies:** `disabledToTodaysDate` 

- `disabledToTodaysDate` 

  Disabled dates to todays date for the date picker. 

## methods 

- `resetData()` 

  Resets the data fields name and validity. 

- `renameOrganisationUnit(evt)` 

  Rename a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

