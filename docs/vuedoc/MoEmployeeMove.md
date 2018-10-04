# mo-employee-move 

A employee move component. 

## props 

- `entry-name` ***String*** (*optional*) 

  Defines a engagement type name. 

- `entry-date` ***Date*** (*optional*) 

  Defines a from date. 

- `entry-org-name` ***String*** (*optional*) 

  Defines a orgName. 

## data 

- `isLoading` 

  The move, original, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

- `original` 

**initial value:** `null` 

- `move` 

**initial value:** `[object Object]` 

## computed properties 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `dateConflict` 

  Check if the dates are valid. 

   **dependencies:** `move`, `original`, `original`, `move`, `move`, `original`, `original`, `move`, `original` 

- `validDates` 

  Check if the organisation date are valid. 

   **dependencies:** `move`, `move` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `moveEmployee(evt)` 

  Move a employee and check if the data fields are valid.
  Then throw a error if not. 

