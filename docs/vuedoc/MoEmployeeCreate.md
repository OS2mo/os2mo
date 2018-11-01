# mo-employee-create 

A employee create component. 

## data 

- `isLoading` 

  The isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

- `entry` 

  The entry - address, association, role, it, manager component.
  Used to add MoAddressEntry, MoAssociationEntry, MoRoleEntry,
  MoItSystemEntry, MoManagerEntry component in `<mo-add-many/>`. 

**initial value:** `[object Object]` 

## computed properties 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `createEmployee(evt)` 

  Create a employee and check if the data fields are valid.
  Then throw a error if not. 

