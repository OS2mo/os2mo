# mo-employee-terminate 

A employee terminate component. 

## props 

- `show` ***Boolean*** (*optional*) `default: false` 

## data 

- `confirmCheckbox` 

**initial value:** `true` 

## computed properties 

- `isDisabled` 

   **dependencies:** `formValid`, `confirmCheckbox` 

- `validity` 

   **dependencies:** `endDate`, `endDate` 


## events 

- `submitted` 

## methods 

- `loadContent(event)` 

- `terminateEmployee()` 

  Terminate employee and check if the data fields are valid.
  Then throw a error if not. 

- `onHidden()` 

