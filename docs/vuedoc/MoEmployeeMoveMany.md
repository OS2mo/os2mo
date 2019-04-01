# mo-employee-move-many 

A employee move many component. 

## props 

- `show` ***Boolean*** (*optional*) `default: false` 

## data 

- `isLoading` 

**initial value:** `false` 

- `orgUnitSource` 

**initial value:** `undefined` 

## computed properties 

- `dateSelected` 

  Set dateSelected to disabled if moveDate is selected. 

   **dependencies:** `moveDate` 

- `isDisabled` 

   **dependencies:** `formValid`, `selected` 

- `validity` 

   **dependencies:** `moveDate` 


## events 

- `submitted` 

## methods 

- `moveMany(evt)` 

  Check if fields are valid, and move employees if they are.
  Otherwise validate the fields. 

- `onHidden()` 

