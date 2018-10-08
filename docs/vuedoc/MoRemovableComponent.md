# mo-removable-component 

A removable component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `entry-component` ***Object*** (*required*) 

  This boolean property defines the entry. 

- `small-buttons` ***Boolean*** (*optional*) 

  This boolean property defines smallButtons. 

- `validity-hidden` ***Boolean*** (*optional*) 

  This boolean property hides the validity. 

## data 

- `entryValue` 

  The entryValue, removed component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `removed` 

**initial value:** `false` 

## events 

- `input` 

  Called after data change.
  Update entryValue. 

## methods 

- `remove()` 

  Remove a entryValue. 

