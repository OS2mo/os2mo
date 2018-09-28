# mo-employee-create 

A employee create component. 

## data 

- `employee` 

  The employee, engagement, address, association, role, itSystem, manager,
  isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `engagement` 

**initial value:** `[object Object]` 

- `address` 

**initial value:** `[object Object]` 

- `association` 

**initial value:** `[object Object]` 

- `role` 

**initial value:** `[object Object]` 

- `itSystem` 

**initial value:** `[object Object]` 

- `manager` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

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

- `resetData()` 

  Resets the data fields. 

- `createEmployee(evt)` 

  Create a employee and check if the data fields are valid.
  Then throw a error if not. 

