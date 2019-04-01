# mo-employee-move 

A employee move component. 

## props 

- `show` ***Boolean*** (*optional*) `default: false` 

## data 

- `isLoading` 

  The isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

## computed properties 

- `dateConflict` 

  Check if the dates are valid. 

   **dependencies:** `from`, `original`, `original`, `from`, `original` 

- `validity` 

   **dependencies:** `from` 


## events 

- `submitted` 

## methods 

- `moveEmployee(evt)` 

  Move a employee and check if the data fields are valid.
  Then throw a error if not. 

- `onHidden()` 

