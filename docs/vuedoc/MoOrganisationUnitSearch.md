# mo-organisation-unit-search 

A organisation unit search component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `date` ***Date*** (*optional*) 

  Defines a date. 

- `label` ***String*** (*optional*) `default: 'Angiv overenhed'` 

  Defines a label with a default name. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a valid unit name. 

## data 

- `selectedSuperUnit` 

  The selectedSuperUnit, items component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `items` 

**initial value:** `[object Object]` 

- `template` 

  The template component value.
  Used to add MoOrganisationUnitSearchTemplate to the autocomplete search. 

**initial value:** `'MoOrganisationUnitSearchTemplate'` 

- `noItem` 

  The noItem component value.
  Used to add a default noItem message. 

**initial value:** `[object Object]` 

## computed properties 

- `nameId` 

  Get name `org-unit`. 

   **dependencies:** `_uid` 


## methods 

- `getLabel(item)` 

  Get organisation label name. 

- `updateItems(query)` 

  Update organisation suggestions based on search query. 

- `selected(item)` 

  Return blank items. 

