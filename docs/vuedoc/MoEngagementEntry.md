# mo-engagement-entry 

A engagement entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity` ***Object*** (*optional*) 

  Defines the validity. 

## data 

- `entry` 

  The entry component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## computed properties 

- `datePickerHidden` 

  Hide the dates. 

   **dependencies:** `validity` 

- `orgUnitValidity` 

  Disabled organisation dates. 

   **dependencies:** `entry`, `entry` 


