# mo-employee-leave 

A employee create leave component. 

## data 

- `isLoading` 

  The isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

## computed properties 

- `formValid` 

  Check validity of form. this.fields is a magic property created by vee-validate 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `createLeave()` 

  Create leave and check if the data fields are valid.
  Then throw a error if not. 

