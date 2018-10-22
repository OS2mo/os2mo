# mo-manager-entry 

A manager entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity-hidden` ***Boolean*** (*optional*) 

  This boolean property hides validity. 

- `hide-org-picker` ***Boolean*** (*optional*) 

  This boolean property hide the org picker. 

- `hide-employee-picker` ***Boolean*** (*optional*) 

  This boolean property hide the employee picker. 

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

  Adds the facetPicker template to the add many component. 

   **dependencies:** `$emit`, `val`, `value` 

- `managerAddressPicker` 

  Adds the managerAddressPicker template to the add many component. 

   **dependencies:** `value`, `val`, `value`, `value`, `value`, `$emit`, `val`, `value` 


