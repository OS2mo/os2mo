# mo-employee-move-many 

A employee move many component. 

## data 

- `orgUnitSource` 

**initial value:** `undefined` 

## computed properties 

- `formValid` 

  Loop over all contents of the fields object and check if they exist and valid. 

   **dependencies:** `fields`, `fields`, `fields` 

- `dateSelected` 

  Set dateSelected to disable if moveDate is selected. 

   **dependencies:** `moveDate` 


## methods 

- `moveMany()` 

  Check if fields are valid, and move employees if they are.
  Otherwise validate the fields. 

