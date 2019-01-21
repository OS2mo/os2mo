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

  The isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

## computed properties 

- `dateConflict` 

  Check if the dates are valid. 

   **dependencies:** `from`, `original`, `original`, `from`, `original` 

- `validDates` 

  Check if the organisation date are valid. 

   **dependencies:** `move`, `move` 


## methods 

- `moveEmployee(evt)` 

  Move a employee and check if the data fields are valid.
  Then throw a error if not. 

