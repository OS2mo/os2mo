# mo-employee-move-many 

A employee move many component. 

## data 

- `employees` 

  The employees, selected, moveDate, orgUnitSource, orgUnitDestination,
  isLoading, backendValidationError, columns component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `selected` 

**initial value:** `[object Object]` 

- `moveDate` 

**initial value:** `null` 

- `orgUnitSource` 

**initial value:** `null` 

- `orgUnitDestination` 

**initial value:** `null` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

- `columns` 

**initial value:** `[object Object]` 

## computed properties 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `dateSelected` 

  Set dateSelected to disable if moveDate is selected. 

   **dependencies:** `moveDate` 

- `sourceSelected` 

  When sourceSelected is selected, return orgUnitSource. 

   **dependencies:** `orgUnitSource`, `orgUnitSource` 

- `nameId` 

  Get name `engagement-picker`. 

   **dependencies:** `_uid` 


## methods 

- `resetData()` 

  Resets the data fields. 

- `selectedEmployees(val)` 

  Selected employees. 

- `getEmployees(orgUnitUuid)` 

  Get employees detail. 

- `moveMany(evt)` 

  Move many employees and check if the data fields are valid.
  Then throw a error if not. 

