# mo-it-system-entry 

A it system entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity-hidden` ***Boolean*** (*optional*) 

  This boolean property hides validity. 

- `disabled-dates` ***Object*** (*optional*) 

  The valid dates for the entry component date pickers 

## data 

- `entry` 

  The entry component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## computed properties 

- `nameId` 

   **dependencies:** `_uid` 


