# mo-entry-edit-modal 

A entry edit modal component. 

## props 

- `uuid` ***String*** (*optional*) 

  Defines a uuid. 

- `label` ***String*** (*optional*) 

  Defines a label. 

- `content` ***Object*** (*optional*) 

  Defines the content. 

- `content-type` ***String*** (*optional*) 

  Defines the contentType. 

- `entry-component` ***Object*** (*optional*) 

  Defines the entryComponent. 

- `type` ***String*** (*required*) 

  Defines a required type - employee or organisation unit. 

## data 

- `entry` 

  The entry, original, isLoading, backendValidationMessage component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `original` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationMessage` 

**initial value:** `null` 

## computed properties 

- `nameId` 

  Get name `moEdit`. 

   **dependencies:** `_uid` 

- `disableOrgUnitPicker` 

  Get disableOrgUnitPicker type. 

   **dependencies:** `type` 

- `hideOrgPicker` 

  Get hideOrgPicker type. 

   **dependencies:** `type` 

- `hideEmployeePicker` 

  Get hideEmployeePicker type. 

   **dependencies:** `type` 

- `hasEntryComponent` 

  If it has a entry component. 

   **dependencies:** `entryComponent` 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 


## methods 

- `handleContent(content)` 

  Handle the entry and original content. 

- `edit()` 

  Edit a employee or organisation entry. 

- `editEmployee(data)` 

  Edit a employee and check if the data fields are valid.
  Then throw a error if not. 

- `editOrganisationUnit(data)` 

  Edit a organisation and check if the data fields are valid.
  Then throw a error if not. 

- `handle(response)` 

