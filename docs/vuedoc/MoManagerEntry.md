# mo-manager-entry 

A manager entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity-hidden` ***Boolean*** (*optional*) 

  This boolean property hides validity. 

## data 

- `entry` 

  The entry component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## computed properties 

- `datePickerHidden` 

  Hides the validity. 

   **dependencies:** `validity` 

- `facetPicker` 

  Adds the facetPicker to the add many component. 

   **dependencies:** `$emit`, `val`, `value` 


