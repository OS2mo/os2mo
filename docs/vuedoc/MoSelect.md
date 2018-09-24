# mo-select 

A select component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `options` ***Array*** (*optional*) 

  Defines options value. 

- `label` ***String*** (*optional*) 

  Defines the label. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected name. 

- `disabled` ***Boolean*** (*optional*) 

  This boolean property disable the label. 

## data 

- `selected` 

  The selected component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

## computed properties 

- `nameId` 

  Get name `mo-select`. 

   **dependencies:** `_uid` 

- `isRequired` 

  If its not disable, change it to required. 

   **dependencies:** `disabled`, `required` 


