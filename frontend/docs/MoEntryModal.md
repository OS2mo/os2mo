# mo-entry-modal 

A entry modal component. 

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

- `action` ***String*** (*required*) 

  Defines a required action - employee or organisation unit. 

- `type` ***String*** (*required*) 

  Defines a required type - employee or organisation unit. 

## data 

- `entry` 

  The entry, original, org, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `original` 

**initial value:** `[object Object]` 

- `org` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

## computed properties 

- `idLabel` 

  Get idLabel `moCreate`. 

   **dependencies:** `_uid` 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `disableOrgUnitPicker` 

  Get disableOrgUnitPicker type. 

   **dependencies:** `type`, `action` 

- `iconLabel` 

  Switch between create and edit iconLabel. 

   **dependencies:** `action` 

- `modalTitle` 

  Switch between create and edit modalTitle. 

   **dependencies:** `action` 

- `hasEntryComponent` 

  If it has a entry component. 

   **dependencies:** `entryComponent` 


## methods 

- `handleContent(content)` 

  Handle the entry and original content. 

- `onClickAction()` 

  Switch between create and edit on click action. 

- `create()` 

  Switch between employee and organisation create entry. 

- `edit()` 

  Switch between employee and organisation edit. 

- `createEmployee(data)` 

  Create a employee. 

- `editEmployee(data)` 

  Edit a employee. 

- `createOrganisationUnit(data)` 

  Create organisation unit entry. 

- `editOrganisationUnit(data)` 

  Edit organisation unit entry. 

