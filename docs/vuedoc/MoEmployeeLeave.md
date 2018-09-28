# mo-employee-leave 

A employee create leave component. 

## data 

- `isLoading` 

  The leave, employee, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

- `employee` 

**initial value:** `[object Object]` 

- `leave` 

**initial value:** `[object Object]` 

## computed properties 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `createLeave(evt)` 

  Create leave and check if the data fields are valid.
  Then throw a error if not. 

