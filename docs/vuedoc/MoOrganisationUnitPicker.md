# mo-organisation-unit-picker 

A organisation unit picker component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `label` ***String*** (*optional*) 

  Defines a default label name. 

- `is-disabled` ***Boolean*** (*optional*) 

  This boolean property disable the value. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a valid name. 

- `validity` ***Object|undefined*** (*optional*) 

  An object of the validities, used for validation 

- `disabled-unit` ***Object*** (*optional*) 

  Unselectable unit. 

- `extra-validations` ***Object*** (*optional*) 

  An object of additional validations to be performed 

## data 

- `selectedSuperUnitUuid` 

  The selectedSuperUnitUuid, showTree, orgName component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `showTree` 

**initial value:** `false` 

- `orgName` 

**initial value:** `null` 

- `orgUnitUuid` 

**initial value:** `null` 

## computed properties 

- `nameId` 

  Get name `org-unit`. 

   **dependencies:** `_uid` 

- `isRequired` 

  When its not disable, make it required. 

   **dependencies:** `isDisabled`, `required` 

- `validations` 

   **dependencies:** `orgName`, `required`, `orgName`, `validity`, `orgUnitUuid`, `extraValidations`, `extraValidations` 


## methods 

- `getSelectedOrganistionUnit()` 

  Get selected oraganisation unit. 

- `toggleTree()` 

  Set showTree to not show. 

