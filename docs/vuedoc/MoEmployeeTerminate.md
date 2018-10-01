# mo-employee-terminate 

A employee terminate component. 

## data 

- `isLoading` 

  The terminate, employee, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

- `employee` 

**initial value:** `null` 

- `terminate` 

**initial value:** `[object Object]` 

## computed properties 

- `isDisabled` 

   **dependencies:** `employee`, `terminate` 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `endEmployee(evt)` 

  Terminate employee and check if the data fields are valid.
  Then throw a error if not. 

