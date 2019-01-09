# mo-leave-entry 

A leave entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity` ***Object*** (*optional*) 

  Defines the validity. 

- `disabled-dates` ***Object*** (*optional*) 

  The valid dates for the entry component date pickers 

## data 

- `entry` 

  The entry component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## computed properties 

- `datePickerHidden` 

  Hides the validity. 

   **dependencies:** `validity` 


