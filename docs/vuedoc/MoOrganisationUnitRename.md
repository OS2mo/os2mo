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

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `compareName` 

  Compare if the unit names are identical.
  If then return false. 

   **dependencies:** `rename`, `original`, `original`, `rename`, `original` 


## methods 

- `resetData()` 

  Resets the data fields name and validity. 

- `renameOrganisationUnit(evt)` 

  Rename a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

