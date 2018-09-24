# mo-organisation-unit-picker 

A organisation unit picker component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `label` ***String*** (*optional*) `default: 'Angiv overenhed'` 

  Defines a default label name. 

- `is-disabled` ***Boolean*** (*optional*) 

  This boolean property disable the value. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a valid name. 

## data 

- `selectedSuperUnit` 

  The selectedSuperUnit, showTree, orgName component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `showTree` 

**initial value:** `false` 

- `orgName` 

**initial value:** `null` 

## computed properties 

- `nameId` 

  Get name `org-unit`. 

   **dependencies:** `_uid` 

- `isRequired` 

  When its not disable, make it required. 

   **dependencies:** `isDisabled`, `required` 


## methods 

- `getSelectedOrganistionUnit()` 

  Get selected oraganisation unit. 

- `toggleTree()` 

  Set showTree to not show. 

