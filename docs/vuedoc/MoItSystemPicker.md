# mo-it-system-picker 

A it system component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `preselected` ***String*** (*optional*) 

  Defines a preselected value. 

## data 

- `selected` 

  The selected, itSystems component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `itSystems` 

**initial value:** `[object Object]` 

## computed properties 

- `nameId` 

  Get name `it-system-picker`. 

   **dependencies:** `_uid` 


## events 

- `input` 

## methods 

- `getItSystems()` 

  Get it systems. 

- `updateSelectedItSystem()` 

  Update selected it system data. 

