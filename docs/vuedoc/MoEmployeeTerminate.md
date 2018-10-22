# mo-employee-terminate 

A employee terminate component. 

## data 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

## computed properties 

- `formValid` 

  Check validity of form. this.fields is a magic property created by vee-validate 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `loadContent(event)` 

- `terminateEmployee()` 

  Terminate employee and check if the data fields are valid.
  Then throw a error if not. 

