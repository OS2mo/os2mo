# mo-entry-create-modal 

A entry create modal component. 

## props 

- `uuid` ***String*** (*optional*) 

  Defines a uuid. 

- `entry-component` ***Object*** (*optional*) 

  Defines a entryComponent. 

- `type` ***String*** (*required*) 

  Defines a required type - employee or organisation unit. 

## data 

- `entry` 

  The entry, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

## computed properties 

- `nameId` 

  Get name `moCreate`. 

   **dependencies:** `_uid` 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `hasEntryComponent` 

  If it has a entry component. 

   **dependencies:** `entryComponent` 


## methods 

- `create()` 

  Create a employee or organisation entry. 

- `createEmployee(data)` 

  Create a employee and check if the data fields are valid.
  Then throw a error if not. 

- `createOrganisationUnit(data)` 

  Create a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

